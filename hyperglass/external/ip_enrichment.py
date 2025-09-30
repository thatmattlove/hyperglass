"""IP enrichment: ASN and IXP lookups for hyperglass.

Uses bgp.tools for ASN lookups and PeeringDB for IXP prefixes.
Provides lookup_ip, lookup_asn_name and network_info compatibility APIs.
"""

import asyncio
import time
import fcntl
import json
import csv
import pickle
import typing as t
from datetime import datetime, timedelta
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address
from pathlib import Path
import socket

from hyperglass.log import log
from hyperglass.state import use_state

# Process-wide lock to coordinate downloads across worker processes.
# Uses an on-disk lock directory so separate processes don't simultaneously
# download enrichment data and cause rate limits.


class _ProcessFileLock:
    """Async-friendly, process-wide filesystem lock.

    Provides an async context manager that runs blocking mkdir/remove
    operations in an executor so multiple processes can coordinate.
    """

    def __init__(self, lock_path: Path, timeout: int = 300, poll_interval: float = 0.1):
        self.lock_path = lock_path
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._lock_dir: t.Optional[str] = None
        # Small startup jitter (seconds) to reduce thundering herd on many
        # worker processes starting at the same time.
        self._startup_jitter = 0.25

    def _acquire_blocking(self) -> None:
        # Use atomic mkdir on a .lck directory as the lock primitive.
        import os
        import random
        import json
        import shutil

        lock_dir = str(self.lock_path) + ".lck"

        # Small jitter before first attempt to reduce concurrent mkdirs
        time.sleep(random.uniform(0, self._startup_jitter))
        start = time.time()

        while True:
            try:
                # Try to create the lock directory atomically; on success we
                # hold the lock. If it exists, retry until timeout.
                os.mkdir(lock_dir)

                # Write a small owner metadata file to help debugging stale locks
                try:
                    owner = {"pid": os.getpid(), "created": datetime.now().isoformat()}
                    with open(os.path.join(lock_dir, "owner.json"), "w") as f:
                        json.dump(owner, f)
                except Exception:
                    # Not critical; proceed even if writing metadata fails
                    pass

                self._lock_dir = lock_dir
                log.debug(f"Acquired process lock {lock_dir} (pid={os.getpid()})")
                return
            except FileExistsError:
                # If the lock appears stale (older than timeout), try cleanup.
                try:
                    owner_file = os.path.join(lock_dir, "owner.json")
                    mtime = None
                    if os.path.exists(owner_file):
                        mtime = os.path.getmtime(owner_file)
                    else:
                        mtime = os.path.getmtime(lock_dir)

                    # If owner file/dir mtime is older than timeout, remove it
                    if (time.time() - mtime) >= self.timeout:
                        log.warning(f"Removing stale lock directory {lock_dir}")
                        try:
                            shutil.rmtree(lock_dir)
                        except Exception:
                            # If we can't remove it, we'll continue to wait until
                            # the timeout is reached by this acquisition attempt.
                            pass
                        # After attempted cleanup, loop and try mkdir again
                        continue
                except Exception:
                    # Ignore issues during stale-check and continue waiting
                    pass

                if (time.time() - start) >= self.timeout:
                    raise TimeoutError(f"Timed out waiting for lock {self.lock_path}")
                time.sleep(self.poll_interval)

    def _release_blocking(self) -> None:
        import os
        import shutil

        try:
            if self._lock_dir:
                try:
                    owner_file = os.path.join(self._lock_dir, "owner.json")
                    if os.path.exists(owner_file):
                        try:
                            os.remove(owner_file)
                        except Exception:
                            pass

                    # Attempt to remove the directory. If it's empty, rmdir will
                    # succeed; if not, fall back to recursive removal as a best-effort.
                    try:
                        os.rmdir(self._lock_dir)
                    except Exception:
                        try:
                            shutil.rmtree(self._lock_dir)
                        except Exception:
                            log.debug(f"Failed to fully remove lock dir {self._lock_dir}")

                    log.debug(f"Released process lock {self._lock_dir}")
                    self._lock_dir = None
                except Exception:
                    # Best-effort; ignore errors removing the lock dir
                    pass
        except Exception:
            # Nothing we can do on release failure
            pass

    async def __aenter__(self):
        loop = asyncio.get_running_loop()
        # Run blocking acquire in executor
        await loop.run_in_executor(None, self._acquire_blocking)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._release_blocking)


# Instantiate a process-global lock file in the data dir. The data dir may not yet
# exist at import time; the constant path is defined below and we'll initialize
# the actual _download_lock after the paths are declared. (See below.)

# Optional dependencies - graceful fallback if not available
try:
    import httpx
except ImportError:
    log.warning("httpx not available - IP enrichment will be disabled")
    httpx = None

try:
    import aiofiles
except ImportError:
    log.warning("aiofiles not available - IP enrichment will use slower sync I/O")
    aiofiles = None

# File paths for persistent storage
IP_ENRICHMENT_DATA_DIR = Path("/etc/hyperglass/ip_enrichment")
IXP_PICKLE_FILE = IP_ENRICHMENT_DATA_DIR / "ixp_data.pickle"
LAST_UPDATE_FILE = IP_ENRICHMENT_DATA_DIR / "last_update.txt"

# Cache duration (seconds). Default: 24 hours. Can be overridden in config.
DEFAULT_CACHE_DURATION = 24 * 60 * 60


# Lazily-created process-wide download lock. Create this after the data
# directory is ensured to exist to avoid open() failing due to a missing
# parent directory and to ensure the lock file lives under the same path
# for all workers.
_download_lock: t.Optional[_ProcessFileLock] = None


def get_cache_duration() -> int:
    """Get cache duration from config, ensuring minimum of 24 hours."""
    try:
        from hyperglass.state import use_state

        params = use_state("params")
        cache_timeout = params.structured.ip_enrichment.cache_timeout
        return max(cache_timeout, DEFAULT_CACHE_DURATION)
    except Exception:
        # Fallback if config not available
        return DEFAULT_CACHE_DURATION


def should_refresh_data(force_refresh: bool = False) -> tuple[bool, str]:
    """Decide whether to refresh IXP data. Only PeeringDB IXP prefixes are
    considered relevant for startup refresh; BGP.tools bulk files are not used.
    """
    if force_refresh:
        return True, "Force refresh requested"

    # No persistent backoff marker; decide refresh purely by file age / config
    # and any transient network errors will be handled by the downloader's
    # retry logic.

    # If an IXP file exists, prefer it and do not perform automatic refreshes
    # unless the caller explicitly requested a force refresh.
    if IXP_PICKLE_FILE.exists() and not force_refresh:
        return False, "ixp_data.json exists; skipping automatic refresh"

    # If IXP file is missing, refresh is needed
    if not IXP_PICKLE_FILE.exists():
        return True, "No ixp_data.json present"

    # Otherwise check timestamp age
    try:
        with open(LAST_UPDATE_FILE, "r") as f:
            cached_time = datetime.fromisoformat(f.read().strip())
        age_seconds = (datetime.now() - cached_time).total_seconds()
        cache_duration = get_cache_duration()
        if age_seconds >= cache_duration:
            age_hours = age_seconds / 3600
            return True, f"Data expired (age: {age_hours:.1f}h, max: {cache_duration/3600:.1f}h)"
    except Exception as e:
        # If reading timestamp fails, prefer a refresh so we don't rely on stale data
        return True, f"Failed to read timestamp: {e}"

    return False, "Data is fresh"


# validate_data_files removed - legacy BGP.tools bulk files are no longer used


# Simple result classes
class IPInfo:
    """Result of IP lookup."""

    def __init__(
        self,
        ip: str,
        asn: t.Optional[int] = None,
        asn_name: t.Optional[str] = None,
        prefix: t.Optional[str] = None,
        country: t.Optional[str] = None,
        is_ixp: bool = False,
        ixp_name: t.Optional[str] = None,
    ):
        self.ip = ip
        self.asn = asn
        self.asn_name = asn_name
        self.prefix = prefix  # The CIDR prefix from table.jsonl
        self.country = country  # Country code from asns.csv
        self.is_ixp = is_ixp
        self.ixp_name = ixp_name


class IPEnrichmentService:
    """Main IP enrichment service with optimized lookups and pickle cache."""

    def __init__(self):
        self.cidr_networks: t.List[t.Tuple[t.Union[IPv4Address, IPv6Address], int, int, str]] = (
            []
        )  # (network, prefixlen, asn, cidr_string)
        self.asn_info: t.Dict[int, t.Dict[str, str]] = {}  # asn -> {name, country}
        self.ixp_networks: t.List[t.Tuple[t.Union[IPv4Address, IPv6Address], int, str]] = (
            []
        )  # (network, prefixlen, ixp_name)
        self.last_update: t.Optional[datetime] = None

        # Optimized lookup structures - populated after data load
        self._ipv4_networks: t.List[t.Tuple[int, int, int, str]] = (
            []
        )  # (net_int, mask_bits, asn, cidr)
        self._ipv6_networks: t.List[t.Tuple[int, int, int, str]] = (
            []
        )  # (net_int, mask_bits, asn, cidr)
        self._lookup_optimized = False

        # Combined cache for ultra-fast loading
        self._combined_cache: t.Optional[t.Dict[str, t.Any]] = None
        # Per-IP in-memory cache for bgp.tools lookups: ip -> (asn, asn_name, prefix, expires_at)
        self._per_ip_cache: t.Dict[
            str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str], float]
        ] = {}
        # Small in-memory cache for per-IP lookups to avoid repeated websocket
        # queries during runtime. Maps ip_str -> (asn, asn_name, prefix)
        self._ip_cache: t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]] = {}
        # Lock to serialize data load so concurrent callers don't duplicate work
        self._ensure_lock = asyncio.Lock()

    def _optimize_lookups(self):
        """Convert IP networks to integer format for faster lookups."""
        if self._lookup_optimized:
            return
        log.debug("Optimizing IP lookup structures...")
        optimize_start = datetime.now()

        self._ipv4_networks = []
        self._ipv6_networks = []

        for net_addr, prefixlen, asn, cidr_string in self.cidr_networks:
            if isinstance(net_addr, IPv4Address):
                net_int = int(net_addr)
                mask_bits = 32 - prefixlen
                self._ipv4_networks.append((net_int, mask_bits, asn, cidr_string))
            else:
                net_int = int(net_addr)
                mask_bits = 128 - prefixlen
                self._ipv6_networks.append((net_int, mask_bits, asn, cidr_string))

        self._ipv4_networks.sort(key=lambda x: x[1])
        self._ipv6_networks.sort(key=lambda x: x[1])

        optimize_time = (datetime.now() - optimize_start).total_seconds()
        log.debug(
            f"Optimized lookups: {len(self._ipv4_networks)} IPv4, {len(self._ipv6_networks)} IPv6 (took {optimize_time:.2f}s)"
        )
        self._lookup_optimized = True

    def _try_load_pickle(self) -> bool:
        """Attempt to load the optimized pickle from disk without triggering downloads.

        This is a best-effort, non-blocking load used during runtime lookups so
        we don't attempt network refreshes or acquire process locks while
        serving user requests.
        """
        try:
            pickle_path = IP_ENRICHMENT_DATA_DIR / "ixp_data.pickle"
            if pickle_path.exists():
                try:
                    with open(pickle_path, "rb") as f:
                        parsed = pickle.load(f)
                    if parsed and isinstance(parsed, list) and len(parsed) > 0:
                        self.ixp_networks = [
                            (ip_address(net), prefixlen, name) for net, prefixlen, name in parsed
                        ]
                        log.debug(
                            "Loaded {} IXP prefixes from optimized pickle (non-blocking)",
                            len(self.ixp_networks),
                        )
                        return True
                except Exception as e:
                    log.debug("Non-blocking pickle load failed: {}", e)
        except Exception:
            pass
        return False

    async def ensure_data_loaded(self, force_refresh: bool = False) -> bool:
        """Ensure data is loaded and fresh from persistent files.

        New behavior: only load PeeringDB IXP prefixes at startup. Do NOT bulk
        download BGP.tools CIDR or ASN data. Per-IP ASN lookups will query the
        bgp.tools API (websocket preferred) on-demand.
        """

        # Create data directory if it doesn't exist
        IP_ENRICHMENT_DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Lazily instantiate the process-wide download lock now that the
        # data directory exists and is guaranteed to be the same path for
        # all worker processes.
        global _download_lock
        if _download_lock is None:
            _download_lock = _ProcessFileLock(IP_ENRICHMENT_DATA_DIR / "download.lock")

        # Fast-path: if already loaded in memory, return immediately
        if self.ixp_networks:
            return True

        # Serialize loads to avoid duplicate file reads when multiple callers
        # call ensure_data_loaded concurrently.
        async with self._ensure_lock:
            # Double-check after acquiring the lock
            if self.ixp_networks:
                return True

            # Fast-path: if an optimized pickle exists and the caller did not
            # request a forced refresh, load it (fastest). Fall back to the
            # legacy JSON IXP file or downloads if the pickle is missing or
            # invalid. This ensures the pickle is the preferred on-disk cache
            # for faster startup.
            try:
                pickle_path = IP_ENRICHMENT_DATA_DIR / "ixp_data.pickle"
                if pickle_path.exists() and not force_refresh:
                    try:
                        with open(pickle_path, "rb") as f:
                            parsed = pickle.load(f)
                        if parsed and isinstance(parsed, list) and len(parsed) > 0:
                            self.ixp_networks = [
                                (ip_address(net), prefixlen, name)
                                for net, prefixlen, name in parsed
                            ]
                            log.info(
                                f"Loaded {len(self.ixp_networks)} IXP prefixes from optimized pickle (fast-path)"
                            )
                            return True
                        else:
                            log.warning(
                                "Optimized pickle exists but appears empty or invalid; falling back to JSON/load or refresh"
                            )
                    except Exception as e:
                        log.warning(
                            f"Failed to load optimized pickle {pickle_path}: {e}; falling back"
                        )
            except Exception:
                # Non-fatal; continue to JSON/download logic
                pass

            # Immediate guard: if an optimized pickle exists on disk and the
            # caller did not request a forced refresh, prefer it and skip any
            # network downloads. This keeps startup fast by loading the already
            # generated optimized mapping.
            try:
                pickle_path = IP_ENRICHMENT_DATA_DIR / "ixp_data.pickle"
                if pickle_path.exists() and not force_refresh:
                    try:
                        with open(pickle_path, "rb") as f:
                            parsed = pickle.load(f)
                        if parsed and isinstance(parsed, list) and len(parsed) > 0:
                            self.ixp_networks = [
                                (ip_address(net), prefixlen, name)
                                for net, prefixlen, name in parsed
                            ]
                            log.info(
                                f"Loaded {len(self.ixp_networks)} IXP prefixes from optimized pickle (early guard)"
                            )
                            return True
                        else:
                            log.warning(
                                "Optimized pickle exists but appears empty or invalid; will attempt to refresh"
                            )
                    except Exception as e:
                        log.warning(
                            f"Failed to read optimized pickle: {e}; will attempt to refresh"
                        )
            except Exception:
                # Ignore filesystem errors and continue to refresh logic
                pass

        # No operator raw-dump conversion: rely on endpoint JSON files (ixpfx.json,
        # ixlan.json, ix.json) in the data directory or download them from
        # PeeringDB when a refresh is required. Determine whether we should
        # refresh based on the backoff marker / cache duration.
        should_refresh, reason = should_refresh_data(force_refresh)

        # If an optimized pickle exists, prefer it and avoid downloads unless forced.
        try:
            pickle_path = IP_ENRICHMENT_DATA_DIR / "ixp_data.pickle"
            if pickle_path.exists():
                try:
                    st = pickle_path.stat()
                    size = getattr(st, "st_size", None)
                except Exception:
                    size = None

                # If file size indicates non-empty file try to load
                if size is not None and size > 0:
                    try:
                        with open(pickle_path, "rb") as f:
                            parsed = pickle.load(f)
                    except Exception as e:
                        log.warning(f"Failed to parse existing optimized IXP pickle: {e}")
                        parsed = None

                    if parsed and isinstance(parsed, list) and len(parsed) > 0:
                        self.ixp_networks = [
                            (ip_address(net), prefixlen, name) for net, prefixlen, name in parsed
                        ]
                        log.info(
                            f"Loaded {len(self.ixp_networks)} IXP prefixes from optimized pickle (size={size})"
                        )
                        return True
                    else:
                        log.warning(
                            "Existing optimized pickle appears empty or invalid (size={}) ; will attempt to refresh",
                            size,
                        )
                else:
                    log.debug(
                        f"Optimized pickle exists but size indicates empty or very small (size={size})"
                    )
        except Exception as e:
            log.warning(f"Failed to load existing optimized IXP data: {e}")

        # If we're currently under a backoff or refresh is not required, skip downloading
        if not should_refresh:
            # If the optimized pickle is missing but the raw PeeringDB JSON files
            # are present and the last_update timestamp is still within the
            # configured cache duration, attempt to build the optimized pickle
            # from the existing JSON files instead of downloading.
            try:
                pickle_path = IP_ENRICHMENT_DATA_DIR / "ixp_data.pickle"
                json_paths = [
                    IP_ENRICHMENT_DATA_DIR / "ixpfx.json",
                    IP_ENRICHMENT_DATA_DIR / "ixlan.json",
                    IP_ENRICHMENT_DATA_DIR / "ix.json",
                ]

                have_all_json = all(p.exists() for p in json_paths)
                if not pickle_path.exists() and have_all_json and LAST_UPDATE_FILE.exists():
                    try:
                        with open(LAST_UPDATE_FILE, "r") as f:
                            cached_time = datetime.fromisoformat(f.read().strip())
                        age_seconds = (datetime.now() - cached_time).total_seconds()
                        cache_duration = get_cache_duration()
                        if age_seconds < cache_duration:
                            log.info("Building optimized pickle from existing PeeringDB JSON files")
                            loop = asyncio.get_running_loop()
                            ok = await loop.run_in_executor(None, self._combine_peeringdb_files)
                            if ok and pickle_path.exists():
                                # Load the generated pickle into memory
                                try:
                                    with open(pickle_path, "rb") as f:
                                        parsed = pickle.load(f)
                                    self.ixp_networks = [
                                        (ip_address(net), prefixlen, name)
                                        for net, prefixlen, name in parsed
                                    ]
                                    log.info(
                                        "Loaded %d IXP prefixes from generated pickle",
                                        len(self.ixp_networks),
                                    )
                                    return True
                                except Exception as e:
                                    log.warning(f"Failed to load generated pickle: {e}")
                    except Exception:
                        # If reading last_update fails, fall through to skipping refresh
                        pass

            except Exception:
                # Non-fatal; proceed to skip refresh
                pass

            log.info("Skipping IXP refresh: {}", reason)
            return False

        # Acquire lock and refresh IXP list only
        async with _download_lock:
            # Double-check in case another worker refreshed
            try:
                # Double-check: if another worker already refreshed the IXP file
                # while we were waiting for the lock, load it regardless of the
                # general should_refresh flag.
                if IXP_PICKLE_FILE.exists():
                    try:
                        with open(IXP_PICKLE_FILE, "rb") as f:
                            parsed = pickle.load(f)
                    except Exception as e:
                        log.warning(
                            f"Existing optimized pickle is invalid after lock wait: {e}; will attempt to refresh"
                        )
                        parsed = None

                    if not parsed or (isinstance(parsed, list) and len(parsed) == 0):
                        log.warning(
                            "Existing optimized pickle is empty after lock wait; will attempt to refresh",
                        )
                    else:
                        self.ixp_networks = [
                            (ip_address(net), prefixlen, name) for net, prefixlen, name in parsed
                        ]
                        log.info(
                            f"Loaded {len(self.ixp_networks)} IXP prefixes from optimized pickle (post-lock)"
                        )
                        return True
            except Exception:
                pass

            if not httpx:
                log.error("httpx not available: cannot download PeeringDB prefixes")
                return False

            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    await self._download_ixp_data(client)

                # After download+combine, ensure we actually have prefixes and
                # update the last-update marker. The combined pickle is already
                # written by _combine_peeringdb_files invoked by _download_ixp_data.
                if not self.ixp_networks or len(self.ixp_networks) == 0:
                    log.warning(
                        "Downloaded 0 IXP prefixes; keeping existing optimized pickle if present"
                    )
                    # Even if no prefixes were combined, write a last-update
                    # marker so startup logic can see that a refresh was
                    # attempted and avoid endless retries.
                    try:
                        tmp_last = LAST_UPDATE_FILE.with_name(LAST_UPDATE_FILE.name + ".tmp")
                        with open(tmp_last, "w") as f:
                            f.write(datetime.now().isoformat())
                        import os

                        os.replace(tmp_last, LAST_UPDATE_FILE)
                        self.last_update = datetime.now()
                    except Exception:
                        log.debug("Failed to write last-update marker after empty IXP refresh")
                    return False

                # Update last update marker
                tmp_last = LAST_UPDATE_FILE.with_name(LAST_UPDATE_FILE.name + ".tmp")
                with open(tmp_last, "w") as f:
                    f.write(datetime.now().isoformat())
                import os

                os.replace(tmp_last, LAST_UPDATE_FILE)

                self.last_update = datetime.now()
                log.info("Refreshed and saved {} IXP prefixes (pickle)", len(self.ixp_networks))
                return True
            except Exception as e:
                log.error("Failed to refresh IXP prefixes: {}", e)
                # No persistent backoff behavior; log and return failure.
                return False

    # end async with _ensure_lock

    async def _download_ixp_data(self, client) -> None:
        """Download and combine PeeringDB datasets: ixpfx, ixlan, ix.

        Behavior:
        - Download each endpoint to {name}.temp (e.g., ixpfx.temp).
        - If download and JSON parsing succeed, atomically rename to {name}.json.
        - If any download fails, leave existing {name}.json (if present) in place.
        - After ensuring all three files exist (new or old), combine them into a
          list of tuples (str(network_address), prefixlen, ixp_name), sorted by
          prefixlen descending, and persist as a pickled file for fast loading.
        """
        log.info("Downloading PeeringDB datasets: ixpfx, ixlan, ix")

        if not client:
            log.error("HTTP client not available for PeeringDB downloads")
            return

        endpoints = {
            "ixpfx": "https://www.peeringdb.com/api/ixpfx",
            "ixlan": "https://www.peeringdb.com/api/ixlan",
            "ix": "https://www.peeringdb.com/api/ix",
        }

        # Helper: fetch a URL exactly once. Do NOT retry on 429 or other
        # errors - if PeeringDB is rate limiting the caller should decide
        # whether to retry later. This prevents the service from reattempting
        # downloads automatically and potentially worsening global rate limits.
        async def _fetch_with_backoff(url: str):
            try:
                log.debug("Downloading PeeringDB endpoint {} (single attempt)", url)
                resp = await client.get(url, timeout=30)

                # Do not retry on 429 - treat as a failed download and return None
                if resp.status_code != 200:
                    log.warning(
                        "PeeringDB download failed for {}: HTTP {} - not retrying",
                        url,
                        resp.status_code,
                    )
                    return None

                try:
                    return resp.json()
                except Exception:
                    log.warning("Failed to parse JSON from {}", url)
                    return None
            except Exception as e:
                log.warning("PeeringDB download error for {}: {} - not retrying", url, e)
                return None

        # Download each endpoint to .temp -> .json atomically
        for name, url in endpoints.items():
            temp_path = IP_ENRICHMENT_DATA_DIR / f"{name}.temp"
            final_path = IP_ENRICHMENT_DATA_DIR / f"{name}.json"
            try:
                data = await _fetch_with_backoff(url)
                if not data:
                    log.warning(
                        "Failed to download {} (no data); will use existing {} if present",
                        url,
                        final_path,
                    )
                    continue

                # Write to temp file first
                try:
                    with open(temp_path, "w") as f:
                        json.dump(data, f, separators=(",", ":"))
                    # Atomic replace
                    import os

                    os.replace(temp_path, final_path)
                    log.info("Saved PeeringDB dataset {} -> {}", name, final_path)
                except Exception as e:
                    log.warning("Failed to write {}: {}", temp_path, e)
                    try:
                        if temp_path.exists():
                            temp_path.unlink()
                    except Exception:
                        pass
            except Exception as e:
                log.warning(
                    "Failed to download {}: {}; will use existing {} if present", url, e, final_path
                )

        # After downloads, combine on-disk JSON files into the optimized pickle
        # The actual combine logic is implemented in _combine_peeringdb_files so
        # it can be reused (e.g., when the optimized pickle is missing but the
        # raw JSON endpoint files are present and still fresh).
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._combine_peeringdb_files)
        except Exception as e:
            log.warning("Failed to combine PeeringDB datasets after download: {}", e)

    async def _query_bgp_tools_for_ip(
        self, ip_str: str
    ) -> t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]:
        """Query bgp.tools for a single IP. Prefer websocket API; fallback to httpx.

        Returns (asn_int, asn_name, prefix) or (None, None, None) on failure.
        """
        # Check cache first
        if ip_str in self._ip_cache:
            return self._ip_cache[ip_str]

        # Use TCP WHOIS bulk mode on bgp.tools:43. We'll perform a blocking
        # socket WHOIS request in a thread executor to keep this function async.

        def _whois_blocking(
            single_ips: t.List[str],
        ) -> t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]]:
            out: t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]] = {}
            host = "bgp.tools"
            port = 43
            # If a query is numeric-only we should send it as an ASN query (AS12345)
            send_keys = [f"AS{q}" if q.isdigit() else q for q in single_ips]
            payload = "begin\n" + "\n".join(send_keys) + "\nend\n"
            try:
                with socket.create_connection((host, port), timeout=10) as s:
                    s.settimeout(10)
                    s.sendall(payload.encode("utf-8"))
                    parts = []
                    try:
                        while True:
                            chunk = s.recv(4096)
                            if not chunk:
                                break
                            parts.append(chunk)
                    except socket.timeout:
                        pass

                    raw = b"".join(parts).decode("utf-8", errors="replace")
                    # Parse lines like: "13335   | 1.1.1.1          | 1.1.1.0/24          | US | ARIN | ... | Cloudflare, Inc."
                    for line in raw.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        # split by pipe if present, else whitespace
                        if "|" in line:
                            cols = [c.strip() for c in line.split("|")]
                            try:
                                asn = int(cols[0]) if cols[0].isdigit() else None
                            except Exception:
                                asn = None
                            ipcol = cols[1] if len(cols) > 1 else None
                            prefix = cols[2] if len(cols) > 2 else None
                            org = cols[-1] if len(cols) > 0 else None
                            if ipcol:
                                out[ipcol] = (asn, org, prefix)
                            else:
                                # ASN-only response (no IP column). Index by ASN too.
                                if asn is not None:
                                    out_key1 = f"AS{asn}"
                                    out_key2 = str(asn)
                                    out[out_key1] = (asn, org, prefix)
                                    out[out_key2] = (asn, org, prefix)
                        else:
                            # Fallback parsing: "AS12345 ip prefix org"
                            parts_line = line.split()
                            if len(parts_line) >= 3:
                                try:
                                    asn = int(parts_line[0])
                                except Exception:
                                    asn = None
                                ipcol = parts_line[1]
                                prefix = parts_line[2]
                                org = " ".join(parts_line[3:]) if len(parts_line) > 3 else None
                                if ipcol:
                                    out[ipcol] = (asn, org, prefix)
                                else:
                                    if asn is not None:
                                        out_key1 = f"AS{asn}"
                                        out_key2 = str(asn)
                                        out[out_key1] = (asn, org, prefix)
                                        out[out_key2] = (asn, org, prefix)
                    # Map results back to the original query keys. For numeric
                    # inputs we sent 'AS{n}', but callers may provide 'n'. Ensure
                    # we return entries keyed by the original queries.
                    mapped: t.Dict[
                        str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]
                    ] = {}
                    for orig, sent in zip(single_ips, send_keys):
                        if sent in out:
                            mapped[orig] = out[sent]
                        elif orig in out:
                            mapped[orig] = out[orig]
                        else:
                            # Try ASN variants
                            if orig.isdigit():
                                if f"AS{orig}" in out:
                                    mapped[orig] = out[f"AS{orig}"]
                                elif orig in out:
                                    mapped[orig] = out[orig]
                                else:
                                    mapped[orig] = (None, None, None)
                            else:
                                mapped[orig] = (None, None, None)
                    return mapped
            except Exception:
                # On any socket/connect error return empties for all requested IPs
                for ip in single_ips:
                    out[ip] = (None, None, None)
                return out

        loop = asyncio.get_running_loop()
        resp_map = await loop.run_in_executor(None, _whois_blocking, [ip_str])
        asn, org, prefix = resp_map.get(ip_str, (None, None, None))
        # Cache result
        self._ip_cache[ip_str] = (asn, org, prefix)
        return (asn, org, prefix)

    def _combine_peeringdb_files(self) -> bool:
        """Combine existing PeeringDB JSON files into the optimized pickle.

        Reads ixpfx.json, ixlan.json, ix.json from the data directory (if
        present), builds a deduplicated prefix->IXP name mapping, sorts by
        prefix length (desc) and persists the result to ixp_data.pickle
        atomically. Returns True on success, False otherwise.
        """
        try:
            ixpfx_data = []
            ixlan_data = []
            ix_data = []

            if (IP_ENRICHMENT_DATA_DIR / "ixpfx.json").exists():
                with open(IP_ENRICHMENT_DATA_DIR / "ixpfx.json", "r") as f:
                    raw = json.load(f)
                    if isinstance(raw, dict) and "data" in raw:
                        ixpfx_data = raw.get("data", [])
                    elif isinstance(raw, list):
                        ixpfx_data = raw

            if (IP_ENRICHMENT_DATA_DIR / "ixlan.json").exists():
                with open(IP_ENRICHMENT_DATA_DIR / "ixlan.json", "r") as f:
                    raw = json.load(f)
                    if isinstance(raw, dict) and "data" in raw:
                        ixlan_data = raw.get("data", [])
                    elif isinstance(raw, list):
                        ixlan_data = raw

            if (IP_ENRICHMENT_DATA_DIR / "ix.json").exists():
                with open(IP_ENRICHMENT_DATA_DIR / "ix.json", "r") as f:
                    raw = json.load(f)
                    if isinstance(raw, dict) and "data" in raw:
                        ix_data = raw.get("data", [])
                    elif isinstance(raw, list):
                        ix_data = raw

            # Build mappings: ixlan_id -> ix_id, ix_id -> ix_name
            ixlan_to_ix = {}
            for rec in ixlan_data:
                try:
                    rid = rec.get("id")
                    ix_id = rec.get("ix_id")
                    if rid is not None and ix_id is not None:
                        ixlan_to_ix[rid] = ix_id
                except Exception:
                    continue

            ix_id_to_name = {}
            for rec in ix_data:
                try:
                    ixid = rec.get("id")
                    name = rec.get("name_long") or rec.get("name")
                    if ixid is not None and name:
                        ix_id_to_name[ixid] = name
                except Exception:
                    continue

            # Combine prefixes to IXP name
            prefix_map: dict[str, str] = {}
            for rec in ixpfx_data:
                try:
                    prefix = rec.get("prefix") or rec.get("network")
                    ixlan_id = rec.get("ixlan_id")
                    if not prefix:
                        continue
                    ix_id = ixlan_to_ix.get(ixlan_id)
                    ix_name = None
                    if ix_id is not None:
                        ix_name = ix_id_to_name.get(ix_id)
                    # Fallback: some ixpfx entries include ix_name or ixlan name
                    if not ix_name:
                        ix_name = rec.get("name") or rec.get("ixp_name")
                    if not ix_name:
                        ix_name = "IXP"
                    # Normalize network
                    try:
                        net = ip_network(prefix, strict=False)
                        prefix_map[str(net)] = ix_name
                    except Exception:
                        # store raw prefix if parsing fails
                        prefix_map[prefix] = ix_name
                except Exception:
                    continue

            # Build sorted list of tuples: (network_address_str, prefixlen, ix_name)
            parsed = []
            for pfx, name in prefix_map.items():
                try:
                    net = ip_network(pfx, strict=False)
                    parsed.append((str(net.network_address), net.prefixlen, name))
                except Exception:
                    # try to skip invalid entries
                    continue

            # Sort by prefixlen desc
            parsed.sort(key=lambda x: x[1], reverse=True)

            # Persist parsed mapping as pickle for performance
            tmp_pickle = IP_ENRICHMENT_DATA_DIR / "ixp_data.pickle.tmp"
            final_pickle = IP_ENRICHMENT_DATA_DIR / "ixp_data.pickle"
            try:
                with open(tmp_pickle, "wb") as f:
                    pickle.dump(parsed, f, protocol=pickle.HIGHEST_PROTOCOL)
                import os

                os.replace(tmp_pickle, final_pickle)
                log.info(
                    "Saved combined IXP prefix mapping (%d prefixes) -> %s",
                    len(parsed),
                    final_pickle,
                )
                # Also update in-memory list for immediate use
                self.ixp_networks = [
                    (ip_address(net), prefixlen, name) for net, prefixlen, name in parsed
                ]
                return True
            except Exception as e:
                log.warning("Failed to persist optimized pickle: %s", e)
                return False

        except Exception as e:
            log.warning("Failed to combine PeeringDB datasets: %s", e)
            return False

    async def _query_bgp_tools_bulk(
        self, ips: t.List[str]
    ) -> t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]]:
        """Query bgp.tools for multiple IPs using a single websocket connection when possible.

        Returns a mapping ip -> (asn, asn_name, prefix).
        """
        results: t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]] = {}

        # Implement TCP WHOIS bulk mode against bgp.tools:43. Perform the
        # blocking socket work in a thread executor so async callers are not
        # blocked.

        def _whois_bulk_blocking(
            bulk_ips: t.List[str],
        ) -> t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]]:
            host = "bgp.tools"
            port = 43
            out: t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]] = {}
            # Normalize numeric-only queries to ASN form for the WHOIS service
            send_keys = [f"AS{q}" if q.isdigit() else q for q in bulk_ips]
            payload = "begin\n" + "\n".join(send_keys) + "\nend\n"
            try:
                with socket.create_connection((host, port), timeout=15) as s:
                    s.settimeout(15)
                    s.sendall(payload.encode("utf-8"))
                    parts = []
                    try:
                        while True:
                            chunk = s.recv(8192)
                            if not chunk:
                                break
                            parts.append(chunk)
                            if sum(len(p) for p in parts) > 512 * 1024:
                                # safety cap 512KB
                                break
                    except socket.timeout:
                        pass

                    raw = b"".join(parts).decode("utf-8", errors="replace")
                    for line in raw.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        if "|" in line:
                            cols = [c.strip() for c in line.split("|")]
                            try:
                                asn = int(cols[0]) if cols[0].isdigit() else None
                            except Exception:
                                asn = None
                            ipcol = cols[1] if len(cols) > 1 else None
                            prefix = cols[2] if len(cols) > 2 else None
                            org = cols[-1] if len(cols) > 0 else None
                            if ipcol:
                                out[ipcol] = (asn, org, prefix)
                            else:
                                # ASN-only response (no IP column). Index by ASN too.
                                if asn is not None:
                                    out_key1 = f"AS{asn}"
                                    out_key2 = str(asn)
                                    out[out_key1] = (asn, org, prefix)
                                    out[out_key2] = (asn, org, prefix)
                        else:
                            parts_line = line.split()
                            if len(parts_line) >= 3:
                                try:
                                    asn = int(parts_line[0])
                                except Exception:
                                    asn = None
                                ipcol = parts_line[1]
                                prefix = parts_line[2]
                                org = " ".join(parts_line[3:]) if len(parts_line) > 3 else None
                                out[ipcol] = (asn, org, prefix)

                    # Map results back to original query keys
                    mapped: t.Dict[
                        str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]
                    ] = {}
                    for orig, sent in zip(bulk_ips, send_keys):
                        if sent in out:
                            mapped[orig] = out[sent]
                        elif orig in out:
                            mapped[orig] = out[orig]
                        else:
                            # Try ASN variants for numeric orig
                            if orig.isdigit():
                                if f"AS{orig}" in out:
                                    mapped[orig] = out[f"AS{orig}"]
                                elif orig in out:
                                    mapped[orig] = out[orig]
                                else:
                                    mapped[orig] = (None, None, None)
                            else:
                                mapped[orig] = (None, None, None)
                    return mapped
            except Exception:
                for ip in bulk_ips:
                    out[ip] = (None, None, None)
                return out

        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(None, _whois_bulk_blocking, ips)
        return resp

    async def lookup_ips_bulk(self, ips: t.List[str]) -> t.Dict[str, IPInfo]:
        """Bulk lookup for multiple IPs, using local data first and bgp.tools bulk queries for misses."""
        results: t.Dict[str, IPInfo] = {}

        # Try a fast, non-blocking load of the optimized pickle; do NOT
        # attempt a network refresh or acquire the download lock here since
        # this function is called during request handling. If the pickle
        # cannot be loaded, proceed with bgp.tools lookups only.
        if not self.ixp_networks:
            self._try_load_pickle()

        # Prepare misses
        misses: t.List[str] = []
        for ip in ips:
            try:
                target_ip = ip_address(ip)
            except Exception:
                results[ip] = IPInfo(ip)
                continue

            # private/reserved
            if target_ip.is_private or target_ip.is_reserved or target_ip.is_loopback:
                results[ip] = IPInfo(ip, asn=0, asn_name="Private", prefix="Private Network")
                continue

            # check IXP
            found_ixp = False
            for net_addr, prefixlen, ixp_name in self.ixp_networks:
                try:
                    network = ip_network(f"{net_addr}/{prefixlen}", strict=False)
                    if target_ip in network:
                        results[ip] = IPInfo(ip, is_ixp=True, ixp_name=ixp_name)
                        found_ixp = True
                        break
                except Exception:
                    continue
            if found_ixp:
                continue

            # try local optimized tables
            if not self._lookup_optimized:
                self._optimize_lookups()

            matched = False
            target_int = int(target_ip)
            if isinstance(target_ip, IPv4Address):
                for net_int, mask_bits, asn, cidr_string in self._ipv4_networks:
                    if (target_int >> mask_bits) == (net_int >> mask_bits):
                        asn_data = self.asn_info.get(asn, {})
                        asn_name = asn_data.get("name", f"AS{asn}")
                        country = asn_data.get("country", "")
                        results[ip] = IPInfo(
                            ip, asn=asn, asn_name=asn_name, prefix=cidr_string, country=country
                        )
                        matched = True
                        break
            else:
                for net_int, mask_bits, asn, cidr_string in self._ipv6_networks:
                    if (target_int >> mask_bits) == (net_int >> mask_bits):
                        asn_data = self.asn_info.get(asn, {})
                        asn_name = asn_data.get("name", f"AS{asn}")
                        country = asn_data.get("country", "")
                        results[ip] = IPInfo(
                            ip, asn=asn, asn_name=asn_name, prefix=cidr_string, country=country
                        )
                        matched = True
                        break

            if not matched:
                misses.append(ip)

        # Query bgp.tools in bulk for misses
        if misses:
            bulk = await self._query_bgp_tools_bulk(misses)
            for ip in misses:
                asn, asn_name, prefix = bulk.get(ip, (None, None, None))
                if asn:
                    try:
                        self.asn_info[int(asn)] = {"name": asn_name or f"AS{asn}", "country": ""}
                    except Exception:
                        pass
                    results[ip] = IPInfo(ip, asn=asn, asn_name=asn_name, prefix=prefix)
                else:
                    results[ip] = IPInfo(ip, asn=0, asn_name="Unknown")

        return results

    async def lookup_ip(self, ip_str: str) -> IPInfo:
        """Lookup an IP address and return ASN or IXP information."""
        # Try to load IXP data, but continue even if the load fails. We still
        # want to perform on-demand bgp.tools lookups for IPs when local data
        # is missing; failing to load the IXP file should not prevent remote
        # lookups.
        try:
            if not self.ixp_networks:
                # Attempt a non-blocking pickle load only; don't trigger
                # downloads or acquire locks while handling requests.
                self._try_load_pickle()
        except Exception:
            log.debug("Non-blocking data load failed; continuing with on-demand lookups")

        # Ensure lookup optimization is done
        self._optimize_lookups()

        log.debug(
            f"Looking up IP {ip_str} - have {len(self.cidr_networks)} CIDR entries, {len(self.asn_info)} ASN entries"
        )

        try:
            target_ip = ip_address(ip_str)
        except ValueError:
            log.debug(f"Invalid IP address: {ip_str}")
            return IPInfo(ip_str)

        # Check if it's a private/reserved/loopback address
        if target_ip.is_private or target_ip.is_reserved or target_ip.is_loopback:
            log.debug(f"IP {ip_str} is in private/reserved range - returning AS0 'Private'")
            return IPInfo(ip_str, asn=0, asn_name="Private", prefix="Private Network")

        # First check IXP networks (more specific usually)
        for net_addr, prefixlen, ixp_name in self.ixp_networks:
            try:
                network = ip_network(f"{net_addr}/{prefixlen}", strict=False)
                if target_ip in network:
                    log.debug(f"Found IXP match for {ip_str}: {ixp_name}")
                    return IPInfo(ip_str, is_ixp=True, ixp_name=ixp_name)
            except Exception:
                continue

        # Fast integer-based lookup for ASN
        target_int = int(target_ip)

        if isinstance(target_ip, IPv4Address):
            # Use optimized IPv4 lookup
            for net_int, mask_bits, asn, cidr_string in self._ipv4_networks:
                if (target_int >> mask_bits) == (net_int >> mask_bits):
                    asn_data = self.asn_info.get(asn, {})
                    asn_name = asn_data.get("name", f"AS{asn}")
                    country = asn_data.get("country", "")
                    log.debug(
                        f"Found ASN match for {ip_str}: AS{asn} ({asn_name}) in {cidr_string}"
                    )
                    return IPInfo(
                        ip_str, asn=asn, asn_name=asn_name, prefix=cidr_string, country=country
                    )
        # Not found in local tables - do an on-demand query to bgp.tools
        try:
            asn, asn_name, prefix = await self._query_bgp_tools_for_ip(ip_str)
            if asn:
                # Update asn_info cache (best-effort)
                try:
                    self.asn_info[int(asn)] = {"name": asn_name or f"AS{asn}", "country": ""}
                except Exception:
                    pass
                return IPInfo(ip_str, asn=asn, asn_name=asn_name, prefix=prefix)
        except Exception:
            pass
        # Not found locally - try one-off query
        try:
            asn, asn_name, prefix = asyncio.get_event_loop().run_until_complete(
                self._query_bgp_tools_for_ip(ip_str)
            )
            if asn:
                try:
                    self.asn_info[int(asn)] = {"name": asn_name or f"AS{asn}", "country": ""}
                except Exception:
                    pass
                return IPInfo(ip_str, asn=asn, asn_name=asn_name, prefix=prefix)
        except Exception:
            pass
        else:
            # Use optimized IPv6 lookup
            for net_int, mask_bits, asn, cidr_string in self._ipv6_networks:
                if (target_int >> mask_bits) == (net_int >> mask_bits):
                    asn_data = self.asn_info.get(asn, {})
                    asn_name = asn_data.get("name", f"AS{asn}")
                    country = asn_data.get("country", "")
                    log.debug(
                        f"Found ASN match for {ip_str}: AS{asn} ({asn_name}) in {cidr_string}"
                    )
                    return IPInfo(
                        ip_str, asn=asn, asn_name=asn_name, prefix=cidr_string, country=country
                    )

        # No match found - return AS0 with "Unknown" to indicate missing data
        log.debug(f"No enrichment data found for {ip_str} - returning AS0 'Unknown'")
        return IPInfo(ip_str, asn=0, asn_name="Unknown")

    async def lookup_asn_name(self, asn: int) -> str:
        """Get the organization name for an ASN."""
        # Attempt to load data but don't fail if we can't; fall back to
        # returning the numeric ASN string if we have no cached name.
        try:
            await self.ensure_data_loaded()
        except Exception:
            log.debug(
                "ensure_data_loaded raised an exception while getting ASN name; using cached data if present"
            )

        asn_data = self.asn_info.get(asn, {})
        name = asn_data.get("name")
        if name:
            return name

        # Fallback: query bgp.tools via WHOIS bulk for ASN (e.g., 'AS12345')
        try:
            query = f"AS{asn}"
            resp = await self._query_bgp_tools_bulk([query])
            # resp maps 'AS12345' -> (asn_int, org, prefix) or maps '12345' -> ...
            entry = resp.get(query) or resp.get(str(asn))
            if entry:
                a, org, _ = entry
                if org:
                    try:
                        self.asn_info[int(asn)] = {"name": org, "country": ""}
                    except Exception:
                        pass
                    return org
        except Exception:
            pass

        return f"AS{asn}"

    async def lookup_asn_country(self, asn: int) -> str:
        """Get the country code for an ASN."""
        try:
            await self.ensure_data_loaded()
        except Exception:
            log.debug(
                "ensure_data_loaded raised an exception while getting ASN country; using cached data if present"
            )

        asn_data = self.asn_info.get(asn, {})
        return asn_data.get("country", "")

    def lookup_ip_direct(self, ip_str: str) -> IPInfo:
        """Direct IP lookup without ensuring data is loaded - for bulk operations."""
        try:
            target_ip = ip_address(ip_str)
        except ValueError as e:
            log.error(f"Invalid IP address: {ip_str}: {e}")
            return IPInfo(ip_str)

        # Check if IP is in private/reserved ranges first
        if target_ip.is_private or target_ip.is_reserved or target_ip.is_loopback:
            log.debug(f"IP {ip_str} is in private/reserved range - returning AS0 'Private'")
            return IPInfo(ip_str, asn=0, asn_name="Private", prefix="Private Network")

        # Check IXP networks first
        for ixp_net, ixp_prefix, ixp_name in self.ixp_networks:
            try:
                ixp_network = ip_network(f"{ixp_net}/{ixp_prefix}")
                if target_ip in ixp_network:
                    log.debug(f"Found IXP match for {ip_str}: {ixp_name}")
                    return IPInfo(ip_str, is_ixp=True, ixp_name=ixp_name)
            except Exception:
                continue

        # Ensure optimized lookup is ready
        if not self._lookup_optimized:
            self._optimize_lookups()

        # Fast integer-based lookup for ASN
        target_int = int(target_ip)

        if isinstance(target_ip, IPv4Address):
            # Use optimized IPv4 lookup
            for net_int, mask_bits, asn, cidr_string in self._ipv4_networks:
                if (target_int >> mask_bits) == (net_int >> mask_bits):
                    asn_data = self.asn_info.get(asn, {})
                    asn_name = asn_data.get("name", f"AS{asn}")
                    country = asn_data.get("country", "")
                    log.debug(
                        f"Found ASN match for {ip_str}: AS{asn} ({asn_name}) in {cidr_string}"
                    )
                    return IPInfo(
                        ip_str, asn=asn, asn_name=asn_name, prefix=cidr_string, country=country
                    )
        else:
            # Use optimized IPv6 lookup
            for net_int, mask_bits, asn, cidr_string in self._ipv6_networks:
                if (target_int >> mask_bits) == (net_int >> mask_bits):
                    asn_data = self.asn_info.get(asn, {})
                    asn_name = asn_data.get("name", f"AS{asn}")
                    country = asn_data.get("country", "")
                    log.debug(
                        f"Found ASN match for {ip_str}: AS{asn} ({asn_name}) in {cidr_string}"
                    )
                    return IPInfo(
                        ip_str, asn=asn, asn_name=asn_name, prefix=cidr_string, country=country
                    )

        # No match found - return AS0 with "Unknown" to indicate missing data
        log.debug(f"No enrichment data found for {ip_str} - returning AS0 'Unknown'")
        return IPInfo(ip_str, asn=0, asn_name="Unknown")


# Global service instance
_service = IPEnrichmentService()


# Public API functions
async def lookup_ip(ip_address: str) -> IPInfo:
    """Lookup an IP address and return ASN or IXP information."""
    return await _service.lookup_ip(ip_address)


async def lookup_asn_name(asn: int) -> str:
    """Get the organization name for an ASN number."""
    # ASN lookups do not require loading PeeringDB data; perform direct lookup
    return await _service.lookup_asn_name(asn)


async def lookup_asn_country(asn: int) -> str:
    """Get the country code for an ASN number."""
    return await _service.lookup_asn_country(asn)


async def lookup_asns_bulk(asns: t.List[t.Union[str, int]]) -> t.Dict[str, t.Dict[str, str]]:
    """Bulk lookup ASN organization names and countries.

    Args:
        asns: List of ASN numbers (as strings like "12345" or integers)

    Returns:
        Dict mapping ASN string to {"name": org_name, "country": country_code}
        Example: {"12345": {"name": "Example ISP", "country": "US"}}
    """
    # Do NOT load PeeringDB data for ASN-only lookups; these use bgp.tools WHOIS
    # and the in-memory `_service.asn_info` cache only. This avoids triggering
    # PeeringDB downloads when callers only need ASN org names.
    results = {}

    # Normalize ASN list to strings and filter invalids
    requested: list[str] = []
    for asn in asns:
        if asn is None:
            continue
        if str(asn) == "IXP":
            continue
        try:
            _ = int(asn)
            requested.append(str(asn))
        except (ValueError, TypeError):
            continue

    # Ensure we have the data loaded
    # Identify ASNs missing a human-friendly name so we can attempt a live WHOIS
    missing: list[str] = []
    for asn in requested:
        try:
            ai = _service.asn_info.get(int(asn), {})
            name = ai.get("name") if isinstance(ai, dict) else None
            if not name or name == f"AS{asn}":
                missing.append(asn)
        except Exception:
            missing.append(asn)

    # If we have missing ASNs, try a live bgp.tools WHOIS bulk query to fetch org names
    if missing and hasattr(_service, "_query_bgp_tools_bulk"):
        try:
            log.debug("lookup_asns_bulk: querying bgp.tools for missing ASNs: {}", missing)
            queries = [f"AS{a}" for a in missing]
            resp = await _service._query_bgp_tools_bulk(queries)
            # resp maps query -> (asn_int, org, prefix)
            for asn in missing:
                q = f"AS{asn}"
                entry = resp.get(q) or resp.get(str(asn))
                if entry:
                    _, org, _ = entry
                    if org:
                        try:
                            _service.asn_info[int(asn)] = {"name": org, "country": ""}
                            log.debug("lookup_asns_bulk: updated asn_info[{}] = {}", asn, org)
                        except Exception:
                            pass
        except Exception as e:
            log.debug("lookup_asns_bulk: bgp.tools lookup failed: {}", e)

    # Build final results from asn_info (may include newly-populated entries)
    for asn in requested:
        try:
            asn_int = int(asn)
            asn_data = _service.asn_info.get(asn_int, {})
            results[asn] = {
                "name": asn_data.get("name", f"AS{asn}"),
                "country": asn_data.get("country", ""),
            }
        except Exception:
            results[asn] = {"name": f"AS{asn}", "country": ""}

    return results


async def refresh_ip_enrichment_data(force: bool = False) -> bool:
    """Manually refresh IP enrichment data."""
    log.info(f"Manual refresh requested (force={force})")
    # Respect configuration: if IP enrichment is disabled, do not attempt
    # to refresh or download PeeringDB data. This prevents manual or UI-
    # triggered refreshes from hitting the network when the feature is
    # administratively turned off.
    try:
        params = use_state("params")
        if (
            not getattr(params, "structured", None)
            or not params.structured.ip_enrichment.enrich_traceroute
            or getattr(params.structured, "enable_for_traceroute", None) is False
        ):
            log.debug(
                "IP enrichment for traceroute is disabled in configuration; skipping manual refresh"
            )
            return False
    except Exception:
        # If we can't read config for some reason, proceed with refresh to
        # avoid silently ignoring an admin's request.
        pass

    return await _service.ensure_data_loaded(force_refresh=force)


def get_data_status() -> dict:
    """Get status information about IP enrichment data."""
    status = {
        "data_directory": str(IP_ENRICHMENT_DATA_DIR),
        "files_exist": {
            "ixp_data_pickle": IXP_PICKLE_FILE.exists(),
            "last_update": LAST_UPDATE_FILE.exists(),
        },
        "last_update": None,
        "age_hours": None,
        "data_counts": {
            # Prefer the in-memory count when available; otherwise try to
            # inspect the optimized pickle on disk so status is accurate
            # across multiple worker processes.
            "ixp_networks": len(_service.ixp_networks) if _service.ixp_networks else None,
        },
    }

    if LAST_UPDATE_FILE.exists():
        try:
            with open(LAST_UPDATE_FILE, "r") as f:
                last_update = datetime.fromisoformat(f.read().strip())
                status["last_update"] = last_update.isoformat()
                status["age_hours"] = (datetime.now() - last_update).total_seconds() / 3600
        except Exception:
            pass

    # If in-memory count is empty (likely this worker hasn't loaded the
    # pickle), attempt to read the optimized pickle on disk to compute a
    # reliable count for the status endpoint without mutating service state.
    if status["data_counts"].get("ixp_networks") in (None, 0) and IXP_PICKLE_FILE.exists():
        try:
            with open(IXP_PICKLE_FILE, "rb") as f:
                parsed = pickle.load(f)
            if isinstance(parsed, list):
                status["data_counts"]["ixp_networks"] = len(parsed)
            else:
                status["data_counts"]["ixp_networks"] = 0
        except Exception:
            # If reading the pickle fails, leave the previously reported
            # value (None or 0). This avoids crashing the status endpoint.
            pass

    return status


# Compatibility functions for existing code
TargetDetail = t.TypedDict(
    "TargetDetail",
    {
        "asn": str,
        "ip": str,
        "prefix": str,
        "country": str,
        "rir": str,
        "allocated": str,
        "org": str,
    },
)

TargetData = t.Dict[str, TargetDetail]


def default_ip_targets(*targets: str) -> t.Tuple[TargetData, t.List[str]]:
    """Filter targets and create default data for private/special addresses."""
    _log = log.bind(source="ip_enrichment")

    default_data: TargetData = {}
    query_targets: t.List[str] = []

    for target in targets:
        try:
            target_ip = ip_address(target)

            # Check for special address types
            special_types = [
                (target_ip.is_loopback, "Loopback Address"),
                (target_ip.is_multicast, "Multicast Address"),
                (target_ip.is_link_local, "Link Local Address"),
                (target_ip.is_private, "Private Address"),
                (target_ip.version == 6 and target_ip.is_site_local, "Site Local Address"),
            ]

            is_special = False
            for check, rir_type in special_types:
                if check:
                    default_data[target] = {
                        "asn": "None",
                        "ip": target,
                        "prefix": "None",
                        "country": "None",
                        "rir": rir_type,
                        "allocated": "None",
                        "org": "None",
                    }
                    is_special = True
                    break

            if not is_special and (target_ip.is_global or target_ip.is_unspecified):
                query_targets.append(target)
            elif not is_special:
                # Other non-global addresses
                default_data[target] = {
                    "asn": "None",
                    "ip": target,
                    "prefix": "None",
                    "country": "None",
                    "rir": "Reserved Address",
                    "allocated": "None",
                    "org": "None",
                }

        except ValueError:
            # Invalid IP address
            default_data[target] = {
                "asn": "None",
                "ip": target,
                "prefix": "None",
                "country": "None",
                "rir": "Invalid Address",
                "allocated": "None",
                "org": "None",
            }

    return default_data, query_targets


async def network_info(*targets: str) -> TargetData:
    """Get network information using IP enrichment - compatibility function."""
    _log = log.bind(source="ip_enrichment")

    default_data, query_targets = default_ip_targets(*targets)

    if not query_targets:
        _log.debug("No valid global IPs to query")
        return default_data

    try:
        _log.info(f"Enriching {len(query_targets)} IP addresses using bulk lookup")

        # Use the bulk lookup to query bgp.tools efficiently
        query_data = {}
        bulk_results = await _service.lookup_ips_bulk(query_targets)

        for target, ip_info in bulk_results.items():
            # Convert to TargetDetail format
            if ip_info.is_ixp and ip_info.ixp_name:
                detail: TargetDetail = {
                    "asn": "IXP",
                    "ip": target,
                    "prefix": "None",
                    "country": "None",
                    "rir": "IXP",
                    "allocated": "None",
                    "org": ip_info.ixp_name,
                }
            elif ip_info.asn is not None and ip_info.asn != 0:
                detail = {
                    "asn": str(ip_info.asn),
                    "ip": target,
                    "prefix": ip_info.prefix or "None",
                    "country": ip_info.country or "None",
                    "rir": "UNKNOWN",
                    "allocated": "None",
                    "org": ip_info.asn_name or "None",
                }
            elif ip_info.asn == 0:
                detail = {
                    "asn": "None",
                    "ip": target,
                    "prefix": "None",
                    "country": "None",
                    "rir": "Unknown",
                    "allocated": "None",
                    "org": "None",
                }
            else:
                detail = {
                    "asn": "None",
                    "ip": target,
                    "prefix": "None",
                    "country": "None",
                    "rir": "Unknown",
                    "allocated": "None",
                    "org": "None",
                }

            query_data[target] = detail

            if ip_info.is_ixp:
                _log.debug(f"Enriched {target}: IXP={ip_info.ixp_name}")
            elif ip_info.asn:
                _log.debug(f"Enriched {target}: AS{ip_info.asn} ({ip_info.asn_name})")
            else:
                _log.debug(f"No enrichment data found for {target}")

    except Exception as e:
        _log.error(f"Error in network_info lookup: {e}")
        # Return default data for all targets on error
        query_data = {}
        for target in query_targets:
            query_data[target] = {
                "asn": "None",
                "ip": target,
                "prefix": "None",
                "country": "None",
                "rir": "Error",
                "allocated": "None",
                "org": "None",
            }

    return {**default_data, **query_data}


def network_info_sync(*targets: str) -> TargetData:
    """Synchronous wrapper for network_info."""
    return asyncio.run(network_info(*targets))


async def network_info_single(target: str) -> TargetDetail:
    """Get network information for a single IP address."""
    result = await network_info(target)
    return result[target]
