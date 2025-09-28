"""IP enrichment service - the main network lookup system for hyperglass.

This completely replaces bgp.tools with bulk data approach using:
- BGP.tools static files for CIDR->ASN mapping
- BGP.tools ASN database for ASN->Organization names
- PeeringDB for IXP detection

Core Functions:
- lookup_ip(ip_address) -> ASN number/name OR IXP name
- lookup_asn_name(asn_number) -> ASN organization name
- network_info(*ips) -> bulk lookup (for compatibility)
"""

import asyncio
import json
import csv
import pickle
import typing as t
from datetime import datetime, timedelta
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address
from pathlib import Path

from hyperglass.log import log
from hyperglass.state import use_state

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
CIDR_DATA_FILE = IP_ENRICHMENT_DATA_DIR / "cidr_data.json"
ASN_DATA_FILE = IP_ENRICHMENT_DATA_DIR / "asn_data.json"
IXP_DATA_FILE = IP_ENRICHMENT_DATA_DIR / "ixp_data.json"
LAST_UPDATE_FILE = IP_ENRICHMENT_DATA_DIR / "last_update.txt"
COMBINED_CACHE_FILE = IP_ENRICHMENT_DATA_DIR / "combined_cache.pickle"

# Raw data files for debugging/inspection
RAW_TABLE_FILE = IP_ENRICHMENT_DATA_DIR / "table.jsonl"
RAW_ASNS_FILE = IP_ENRICHMENT_DATA_DIR / "asns.csv"

# Data URLs
BGP_TOOLS_TABLE_URL = "https://bgp.tools/table.jsonl"
BGP_TOOLS_ASNS_URL = "https://bgp.tools/asns.csv"
PEERINGDB_IXPFX_URL = "https://www.peeringdb.com/api/ixpfx"

# Cache duration (24 hours default, configurable)
DEFAULT_CACHE_DURATION = 24 * 60 * 60


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
    """Check if data should be refreshed and return reason."""
    if force_refresh:
        return True, "Force refresh requested"

    if not LAST_UPDATE_FILE.exists():
        return True, "No timestamp file found"

    # Check each required file individually - if ANY are missing, refresh ALL
    required_files = [
        (CIDR_DATA_FILE, "cidr_data.json"),
        (ASN_DATA_FILE, "asn_data.json"),
        (IXP_DATA_FILE, "ixp_data.json"),
    ]

    missing_files = []
    for file_path, file_name in required_files:
        if not file_path.exists():
            missing_files.append(file_name)

    if missing_files:
        return True, f"Missing data files: {', '.join(missing_files)}"

    # Check file age
    try:
        with open(LAST_UPDATE_FILE, "r") as f:
            cached_time = datetime.fromisoformat(f.read().strip())

        age_seconds = (datetime.now() - cached_time).total_seconds()
        cache_duration = get_cache_duration()

        if age_seconds >= cache_duration:
            age_hours = age_seconds / 3600
            return True, f"Data expired (age: {age_hours:.1f}h, max: {cache_duration/3600:.1f}h)"

    except Exception as e:
        return True, f"Failed to read timestamp: {e}"

    return False, "Data is fresh"


def validate_data_files() -> tuple[bool, str]:
    """Validate that data files contain reasonable data."""
    try:
        # Check CIDR data
        if CIDR_DATA_FILE.exists():
            with open(CIDR_DATA_FILE, "r") as f:
                cidr_data = json.load(f)
            if not isinstance(cidr_data, list) or len(cidr_data) < 1000:
                return (
                    False,
                    f"CIDR data invalid or too small: {len(cidr_data) if isinstance(cidr_data, list) else 'not a list'}",
                )

        # Check ASN data
        if ASN_DATA_FILE.exists():
            with open(ASN_DATA_FILE, "r") as f:
                asn_data = json.load(f)
            if not isinstance(asn_data, dict) or len(asn_data) < 100:
                return (
                    False,
                    f"ASN data invalid or too small: {len(asn_data) if isinstance(asn_data, dict) else 'not a dict'}",
                )

        return True, "Data files are valid"

    except Exception as e:
        return False, f"Data validation failed: {e}"


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
                # Convert IPv4 to integer for fast bitwise operations
                net_int = int(net_addr)
                mask_bits = 32 - prefixlen
                self._ipv4_networks.append((net_int, mask_bits, asn, cidr_string))
            else:
                # Convert IPv6 to integer
                net_int = int(net_addr)
                mask_bits = 128 - prefixlen
                self._ipv6_networks.append((net_int, mask_bits, asn, cidr_string))

        # Sort by mask bits (ascending) for longest-match-first
        self._ipv4_networks.sort(key=lambda x: x[1])
        self._ipv6_networks.sort(key=lambda x: x[1])

        optimize_time = (datetime.now() - optimize_start).total_seconds()
        log.debug(
            f"Optimized lookups: {len(self._ipv4_networks)} IPv4, {len(self._ipv6_networks)} IPv6 "
            f"networks in {optimize_time:.2f}s"
        )
        self._lookup_optimized = True

    def _save_combined_cache(self):
        """Save all data structures to a single pickle file for ultra-fast loading."""
        try:
            cache_data = {
                "cidr_networks": self.cidr_networks,
                "asn_info": self.asn_info,
                "ixp_networks": self.ixp_networks,
                "ipv4_networks": self._ipv4_networks,
                "ipv6_networks": self._ipv6_networks,
                "last_update": self.last_update,
                "lookup_optimized": self._lookup_optimized,
            }

            with open(COMBINED_CACHE_FILE, "wb") as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            log.debug(
                f"Saved combined cache with {len(self.cidr_networks)} CIDR entries to pickle file"
            )
        except Exception as e:
            log.error(f"Failed to save combined cache: {e}")

    def _load_combined_cache(self) -> bool:
        """Load all data structures from pickle file."""
        if not COMBINED_CACHE_FILE.exists():
            return False

        try:
            with open(COMBINED_CACHE_FILE, "rb") as f:
                cache_data = pickle.load(f)

            self.cidr_networks = cache_data["cidr_networks"]
            self.asn_info = cache_data["asn_info"]
            self.ixp_networks = cache_data["ixp_networks"]
            self._ipv4_networks = cache_data["ipv4_networks"]
            self._ipv6_networks = cache_data["ipv6_networks"]
            self.last_update = cache_data["last_update"]
            self._lookup_optimized = cache_data["lookup_optimized"]

            log.debug(
                f"Loaded combined cache with {len(self.cidr_networks)} CIDR entries from pickle file"
            )
            return True
        except Exception as e:
            log.error(f"Failed to load combined cache: {e}")
            return False

    async def ensure_data_loaded(self, force_refresh: bool = False) -> bool:
        """Ensure data is loaded and fresh from persistent files."""
        # Create data directory if it doesn't exist
        IP_ENRICHMENT_DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Check if refresh is needed
        should_refresh, reason = should_refresh_data(force_refresh)

        if not should_refresh:
            # Validate existing data files
            is_valid, validation_msg = validate_data_files()
            if not is_valid:
                should_refresh = True
                reason = f"Data validation failed: {validation_msg}"

        if not should_refresh:
            # Try to load from ultra-fast pickle cache first
            if self._load_combined_cache():
                age_hours = (
                    (datetime.now() - self.last_update).total_seconds() / 3600
                    if self.last_update
                    else 0
                )
                log.info(f"Loading IP enrichment data from pickle cache (age: {age_hours:.1f}h)")
                log.debug(
                    f"Cache contains: {len(self.cidr_networks)} CIDR entries, "
                    f"{len(self.asn_info)} ASN entries, {len(self.ixp_networks)} IXP networks"
                )
                return True

            # Fallback to JSON files if pickle cache failed
            try:
                with open(CIDR_DATA_FILE, "r") as f:
                    cidr_data = json.load(f)
                with open(ASN_DATA_FILE, "r") as f:
                    asn_data = json.load(f)
                with open(IXP_DATA_FILE, "r") as f:
                    ixp_data = json.load(f)
                with open(LAST_UPDATE_FILE, "r") as f:
                    cached_time = datetime.fromisoformat(f.read().strip())

                age_hours = (datetime.now() - cached_time).total_seconds() / 3600
                log.info(f"Loading IP enrichment data from JSON files (age: {age_hours:.1f}h)")
                log.debug(
                    f"Files contain: {len(cidr_data)} CIDR entries, "
                    f"{len(asn_data)} ASN entries, {len(ixp_data)} IXP networks"
                )

                # Convert string IP addresses back to IP objects
                self.cidr_networks = [
                    (ip_address(net), prefixlen, asn, cidr)
                    for net, prefixlen, asn, cidr in cidr_data
                ]
                # ASN data has integer keys that become strings in JSON
                self.asn_info = {int(k): v for k, v in asn_data.items()}
                self.ixp_networks = [
                    (ip_address(net), prefixlen, name) for net, prefixlen, name in ixp_data
                ]
                self.last_update = cached_time

                # Reset optimization flag so it gets rebuilt with new data
                self._lookup_optimized = False

                # Save to pickle cache for next time
                self._optimize_lookups()
                self._save_combined_cache()

                return True

            except Exception as e:
                log.warning(f"Failed to load existing data files: {e} - will refresh")
                should_refresh = True
                reason = f"Failed to load files: {e}"

        # Download fresh data
        log.info(f"Refreshing IP enrichment data: {reason}")

        if not httpx:
            log.error("httpx not available - cannot download IP enrichment data")
            return False

        try:
            log.info("🌐 Starting fresh IP enrichment data download...")
            download_start = datetime.now()

            async with httpx.AsyncClient(timeout=300) as client:
                # Track which downloads succeeded
                bgp_success = False
                ixp_success = False

                # Try to download BGP data (required)
                try:
                    await self._download_bgp_data(client)
                    bgp_success = True
                    log.debug("✅ BGP data download successful")
                except Exception as e:
                    log.error(f"❌ BGP data download failed: {e}")
                    # BGP data is critical - if this fails, we can't continue
                    raise Exception(f"Critical BGP data download failed: {e}")

                # Try to download IXP data (optional but preferred)
                try:
                    await self._download_ixp_data(client)
                    ixp_success = True
                    log.debug("✅ IXP data download successful")
                except Exception as e:
                    log.error(f"❌ IXP data download failed: {e}")
                    # IXP data is optional - clear any partial data and continue
                    self.ixp_networks = []
                    log.warning("Continuing without IXP data - IXP detection will be unavailable")

            download_duration = (datetime.now() - download_start).total_seconds()

            if not bgp_success:
                # This shouldn't happen due to the raise above, but be explicit
                raise Exception("BGP data download failed - cannot continue")

            log.info(
                f"📊 Download summary: BGP data: ✅, IXP data: {'✅' if ixp_success else '❌'}"
            )

            # Continue with saving even if IXP failed...

            # Save the data to persistent files
            log.debug("💾 Saving IP enrichment data to persistent files...")
            cache_start = datetime.now()

            # Convert IP addresses to strings for JSON serialization
            cidr_file_data = [
                (str(net), prefixlen, asn, cidr) for net, prefixlen, asn, cidr in self.cidr_networks
            ]
            ixp_file_data = [
                (str(net), prefixlen, name) for net, prefixlen, name in self.ixp_networks
            ]

            with open(CIDR_DATA_FILE, "w") as f:
                json.dump(cidr_file_data, f, separators=(",", ":"))  # Compact JSON
            with open(ASN_DATA_FILE, "w") as f:
                json.dump(self.asn_info, f, separators=(",", ":"))
            with open(IXP_DATA_FILE, "w") as f:
                json.dump(ixp_file_data, f, separators=(",", ":"))
            with open(LAST_UPDATE_FILE, "w") as f:
                f.write(datetime.now().isoformat())

            cache_duration_actual = (datetime.now() - cache_start).total_seconds()

            self.last_update = datetime.now()

            # Optimize lookups and create pickle cache for ultra-fast loading
            self._lookup_optimized = False
            self._optimize_lookups()
            self._save_combined_cache()

            log.info(f"✅ IP enrichment data loaded successfully!")
            log.info(
                f"📊 Data summary: {len(self.cidr_networks)} CIDR entries, "
                f"{len(self.asn_info)} ASN entries, {len(self.ixp_networks)} IXP networks"
            )
            log.debug(
                f"⏱️  Download time: {download_duration:.1f}s, Save time: {cache_duration_actual:.1f}s"
            )
            return True

        except Exception as e:
            log.error(f"Failed to download IP enrichment data: {e}")
            return False

    async def _download_bgp_data(self, client) -> None:
        """Download BGP.tools data."""
        log.info("📥 Downloading BGP.tools CIDR table from bgp.tools...")
        download_start = datetime.now()
        response = await client.get(BGP_TOOLS_TABLE_URL)
        response.raise_for_status()
        download_time = (datetime.now() - download_start).total_seconds()

        # Save raw file for debugging
        with open(RAW_TABLE_FILE, "w") as f:
            f.write(response.text)

        # Process JSONL data
        process_start = datetime.now()
        cidr_count = 0
        total_lines = len(response.text.strip().split("\n"))
        log.debug(f"Processing {total_lines} lines from CIDR table...")

        for line in response.text.strip().split("\n"):
            if line.strip():
                try:
                    entry = json.loads(line)
                    cidr = entry.get("CIDR")
                    asn = entry.get("ASN")
                    if cidr and asn:
                        network = ip_network(cidr, strict=False)
                        self.cidr_networks.append(
                            (network.network_address, network.prefixlen, asn, cidr)
                        )
                        cidr_count += 1
                except Exception as e:
                    log.debug(f"Failed to parse CIDR line: {line[:100]} - {e}")
                    continue

        process_time = (datetime.now() - process_start).total_seconds()
        log.info(
            f"✅ Downloaded {cidr_count}/{total_lines} CIDR entries "
            f"(download: {download_time:.1f}s, process: {process_time:.1f}s)"
        )

        # Sort by prefix length (descending) for longest-match lookup
        sort_start = datetime.now()
        self.cidr_networks.sort(key=lambda x: x[1], reverse=True)
        sort_time = (datetime.now() - sort_start).total_seconds()
        log.debug(f"Sorted CIDR entries by prefix length in {sort_time:.1f}s")

        # Download ASN names
        log.info("📥 Downloading BGP.tools ASN names from bgp.tools...")
        download_start = datetime.now()
        response = await client.get(BGP_TOOLS_ASNS_URL)
        response.raise_for_status()
        download_time = (datetime.now() - download_start).total_seconds()

        # Save raw file for debugging
        with open(RAW_ASNS_FILE, "w") as f:
            f.write(response.text)

        # Process CSV data
        process_start = datetime.now()
        lines = response.text.strip().split("\n")
        if not lines:
            log.error("Empty ASN data received")
            return

        # Debug: log the first few lines to see the format
        log.debug(f"ASN CSV header: {lines[0] if lines else 'NO HEADER'}")
        if len(lines) > 1:
            log.debug(f"ASN CSV first data line: {lines[1]}")

        reader = csv.DictReader(lines)
        asn_count = 0
        total_asns = 0
        failed_count = 0

        for row in reader:
            total_asns += 1
            try:
                asn_str = row.get("asn", "").strip()
                name = row.get("name", "").strip()
                country = row.get("cc", "").strip()  # Country code from CC column

                if not asn_str:
                    failed_count += 1
                    continue

                # Handle ASN formats like "AS12345" or just "12345"
                if asn_str.upper().startswith("AS"):
                    asn = int(asn_str[2:])
                else:
                    asn = int(asn_str)

                if asn > 0 and name:
                    self.asn_info[asn] = {"name": name, "country": country}
                    asn_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                failed_count += 1
                if failed_count < 5:  # Only log first few failures
                    log.debug(f"Failed to parse ASN row {total_asns}: {row} - {e}")
                continue

        process_time = (datetime.now() - process_start).total_seconds()
        log.info(
            f"✅ Downloaded {asn_count}/{total_asns} ASN entries with country codes "
            f"(download: {download_time:.1f}s, process: {process_time:.1f}s, failed: {failed_count})"
        )

    async def _download_ixp_data(self, client) -> None:
        """Download PeeringDB IXP prefixes data - simplified approach using only IXPFX."""
        log.info("📥 Downloading PeeringDB IXP prefixes from peeringdb.com...")

        max_retries = 3
        base_delay = 5  # Start with 5 second delay

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = base_delay * (2**attempt)  # Exponential backoff
                    log.info(f"Retry attempt {attempt + 1}/{max_retries} after {delay}s delay...")
                    await asyncio.sleep(delay)

                # Get IXP prefixes directly - no need for IXLAN lookup
                log.debug("Downloading IXP prefixes...")
                download_start = datetime.now()
                response = await client.get(PEERINGDB_IXPFX_URL)
                response.raise_for_status()
                ixpfxs = response.json()["data"]
                prefix_time = (datetime.now() - download_start).total_seconds()

                # Process IXP prefixes - use a generic IXP name since we don't need specific names
                process_start = datetime.now()
                ixp_count = 0
                total_prefixes = len(ixpfxs)
                failed_prefixes = 0

                for ixpfx in ixpfxs:
                    try:
                        prefix = ixpfx.get("prefix")

                        if prefix:
                            network = ip_network(prefix, strict=False)
                            # Use "IXP Network" as generic name since we only need to know it's an IXP
                            ixp_name = "IXP Network"
                            self.ixp_networks.append(
                                (network.network_address, network.prefixlen, ixp_name)
                            )
                            ixp_count += 1
                        else:
                            failed_prefixes += 1
                    except Exception:
                        failed_prefixes += 1

                process_time = (datetime.now() - process_start).total_seconds()

                # Sort by prefix length (descending) for longest-match lookup
                sort_start = datetime.now()
                self.ixp_networks.sort(key=lambda x: x[1], reverse=True)
                sort_time = (datetime.now() - sort_start).total_seconds()

                log.info(
                    f"✅ Downloaded {ixp_count}/{total_prefixes} IXP networks "
                    f"(download: {prefix_time:.1f}s, process: {process_time:.1f}s, "
                    f"sort: {sort_time:.1f}s, failed: {failed_prefixes})"
                )
                return  # Success - exit retry loop

            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** (attempt + 1))
                        log.warning(
                            f"Rate limited by PeeringDB API (attempt {attempt + 1}/{max_retries}). Retrying in {delay}s..."
                        )
                        continue
                    else:
                        log.error(
                            f"Rate limited by PeeringDB API after {max_retries} attempts. Skipping IXP data."
                        )
                        break
                else:
                    log.warning(
                        f"Failed to download IXP data (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        continue
                    break

        # If we get here, all retries failed
        log.warning("Could not download IXP data after retries - continuing without IXP detection")
        log.info("ASN lookups will still work, but IXP networks won't be identified")
        self.ixp_networks = []

    async def lookup_ip(self, ip_str: str) -> IPInfo:
        """Lookup an IP address and return ASN or IXP information."""
        if not await self.ensure_data_loaded():
            log.warning("IP enrichment data not available")
            return IPInfo(ip_str)

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
        if not await self.ensure_data_loaded():
            return f"AS{asn}"

        asn_data = self.asn_info.get(asn, {})
        return asn_data.get("name", f"AS{asn}")

    async def lookup_asn_country(self, asn: int) -> str:
        """Get the country code for an ASN."""
        if not await self.ensure_data_loaded():
            return ""

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
    await _service.ensure_data_loaded()

    results = {}
    for asn in asns:
        # Skip non-numeric ASNs like "IXP"
        if asn == "IXP" or asn is None:
            continue

        try:
            asn_int = int(asn)
            asn_data = _service.asn_info.get(asn_int, {})
            results[str(asn)] = {
                "name": asn_data.get("name", f"AS{asn}"),
                "country": asn_data.get("country", ""),
            }
        except (ValueError, TypeError):
            # Skip invalid ASN values
            continue

    return results


async def refresh_ip_enrichment_data(force: bool = False) -> bool:
    """Manually refresh IP enrichment data."""
    log.info(f"Manual refresh requested (force={force})")
    return await _service.ensure_data_loaded(force_refresh=force)


def get_data_status() -> dict:
    """Get status information about IP enrichment data."""
    status = {
        "data_directory": str(IP_ENRICHMENT_DATA_DIR),
        "files_exist": {
            "cidr_data": CIDR_DATA_FILE.exists(),
            "asn_data": ASN_DATA_FILE.exists(),
            "ixp_data": IXP_DATA_FILE.exists(),
            "last_update": LAST_UPDATE_FILE.exists(),
            "combined_cache": COMBINED_CACHE_FILE.exists(),
            "raw_table": RAW_TABLE_FILE.exists(),
            "raw_asns": RAW_ASNS_FILE.exists(),
        },
        "last_update": None,
        "age_hours": None,
        "data_counts": {
            "cidr_entries": len(_service.cidr_networks),
            "asn_entries": len(_service.asn_info),
            "ixp_networks": len(_service.ixp_networks),
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
        _log.info(f"Enriching {len(query_targets)} IP addresses")

        # Load data ONCE for all lookups
        await _service.ensure_data_loaded()

        query_data = {}

        # Process each target without reloading data
        for target in query_targets:
            ip_info = _service.lookup_ip_direct(
                target
            )  # Use direct lookup that doesn't reload data

            # Convert to TargetDetail format
            if ip_info.is_ixp and ip_info.ixp_name:
                # IXP case - put "IXP" in ASN field and IXP name in org field
                detail: TargetDetail = {
                    "asn": "IXP",  # Show "IXP" as the ASN for IXPs
                    "ip": target,
                    "prefix": "None",
                    "country": "None",
                    "rir": "IXP",  # Mark as IXP in RIR field
                    "allocated": "None",
                    "org": ip_info.ixp_name,
                }
            elif ip_info.asn is not None:
                # ASN case - normal network - return just the NUMBER, no AS prefix
                detail = {
                    "asn": str(ip_info.asn),  # Just the number as string, e.g. "12345"
                    "ip": target,
                    "prefix": ip_info.prefix or "None",  # Use the CIDR from table.jsonl
                    "country": ip_info.country or "None",  # Use country code from asns.csv
                    "rir": "UNKNOWN",  # Not available from our enrichment
                    "allocated": "None",  # Not available from our enrichment
                    "org": ip_info.asn_name or "None",
                }
            else:
                # No match found
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
