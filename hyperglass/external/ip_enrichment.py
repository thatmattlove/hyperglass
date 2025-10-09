"""IP enrichment: ASN and IXP lookups for hyperglass.

Uses bgp.tools for both ASN and IXP lookups.
Provides lookup_ip, lookup_asn_name and network_info compatibility APIs.
"""

import asyncio
import typing as t
from ipaddress import ip_address, IPv4Address, IPv6Address
import socket

from hyperglass.log import log
from hyperglass.settings import Settings


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
        self.prefix = prefix
        self.country = country
        self.is_ixp = is_ixp
        self.ixp_name = ixp_name


class IPEnrichmentService:
    """Simplified IP enrichment service using only BGP.TOOLS for all lookups."""

    def __init__(self):
        # Runtime caches for performance
        self._ip_cache: t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]] = {}
        self.asn_info: t.Dict[int, t.Dict[str, str]] = {}  # asn -> {name, country}

    async def _query_bgp_tools_for_ip(
        self, ip_str: str
    ) -> t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]:
        """Query bgp.tools for a single IP.

        Returns (asn_int, asn_name, prefix) or (None, None, None) on failure.
        """
        # Check cache first
        if ip_str in self._ip_cache:
            return self._ip_cache[ip_str]

        # Use TCP WHOIS on bgp.tools:43
        def _whois_blocking(
            single_ips: t.List[str],
        ) -> t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]]:
            out: t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]] = {}
            host = "bgp.tools"
            port = 43
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
                                if asn is not None:
                                    out_key1 = f"AS{asn}"
                                    out_key2 = str(asn)
                                    out[out_key1] = (asn, org, prefix)
                                    out[out_key2] = (asn, org, prefix)
                        else:
                            # Fallback parsing
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

                    # Map results back to original query keys
                    mapped: t.Dict[
                        str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]
                    ] = {}
                    for orig, sent in zip(single_ips, send_keys):
                        if sent in out:
                            mapped[orig] = out[sent]
                        elif orig in out:
                            mapped[orig] = out[orig]
                        else:
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
                for ip in single_ips:
                    out[ip] = (None, None, None)
                return out

        loop = asyncio.get_running_loop()
        resp_map = await loop.run_in_executor(None, _whois_blocking, [ip_str])
        asn, org, prefix = resp_map.get(ip_str, (None, None, None))
        # Cache result
        self._ip_cache[ip_str] = (asn, org, prefix)
        return (asn, org, prefix)

    async def _query_bgp_tools_bulk(
        self, ips: t.List[str]
    ) -> t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]]:
        """Query bgp.tools for multiple IPs using a single connection.

        Returns a mapping ip -> (asn, asn_name, prefix).
        """

        def _whois_bulk_blocking(
            bulk_ips: t.List[str],
        ) -> t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]]:
            host = "bgp.tools"
            port = 43
            out: t.Dict[str, t.Tuple[t.Optional[int], t.Optional[str], t.Optional[str]]] = {}
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
                            # Check if this is an exchange IP (IXP)
                            is_ixp = any(
                                keyword in (org or "").lower()
                                for keyword in ["ix", "exchange", "peering"]
                            )
                            if ipcol:
                                # If it's an IXP, mark it specially
                                if is_ixp:
                                    out[ipcol] = (
                                        None,
                                        org,
                                        prefix,
                                    )  # Use None for ASN to indicate IXP
                                else:
                                    out[ipcol] = (asn, org, prefix)
                            else:
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
        """Bulk lookup for multiple IPs using BGP.TOOLS."""
        results: t.Dict[str, IPInfo] = {}

        # Prepare list for query
        query_ips: t.List[str] = []
        for ip in ips:
            try:
                target_ip = ip_address(ip)
            except Exception:
                results[ip] = IPInfo(ip)
                continue

            # Check for private/reserved addresses
            if target_ip.is_private or target_ip.is_reserved or target_ip.is_loopback:
                results[ip] = IPInfo(ip, asn=0, asn_name="Private", prefix="Private Network")
                continue

            query_ips.append(ip)

        # Query BGP.TOOLS in bulk for all IPs
        if query_ips:
            bulk = await self._query_bgp_tools_bulk(query_ips)
            for ip in query_ips:
                asn, asn_name, prefix = bulk.get(ip, (None, None, None))

                # Check if this is an IXP (indicated by None ASN from our parsing)
                is_ixp = asn is None and asn_name is not None

                if is_ixp:
                    results[ip] = IPInfo(ip, is_ixp=True, ixp_name=asn_name)
                elif asn:
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
        if Settings.debug:
            log.debug(f"Looking up IP {ip_str}")

        try:
            target_ip = ip_address(ip_str)
        except ValueError:
            if Settings.debug:
                log.debug(f"Invalid IP address: {ip_str}")
            return IPInfo(ip_str)

        # Check private/reserved addresses
        if target_ip.is_private or target_ip.is_reserved or target_ip.is_loopback:
            if Settings.debug:
                log.debug(f"IP {ip_str} is in private/reserved range")
            return IPInfo(ip_str, asn=0, asn_name="Private", prefix="Private Network")

        # Query bgp.tools for the IP
        try:
            asn, asn_name, prefix = await self._query_bgp_tools_for_ip(ip_str)

            # Check if this is an IXP (indicated by keywords in organization name)
            is_ixp = asn_name and any(
                keyword in asn_name.lower() for keyword in ["ix", "exchange", "peering"]
            )

            if is_ixp:
                if Settings.debug:
                    log.debug(f"Found IXP match for {ip_str}: {asn_name}")
                return IPInfo(ip_str, is_ixp=True, ixp_name=asn_name)
            elif asn:
                # Cache result
                try:
                    self.asn_info[int(asn)] = {"name": asn_name or f"AS{asn}", "country": ""}
                except Exception:
                    pass
                if Settings.debug:
                    log.debug(f"BGP.tools lookup for {ip_str}: AS{asn} ({asn_name})")
                return IPInfo(ip_str, asn=asn, asn_name=asn_name, prefix=prefix)
        except Exception as e:
            if Settings.debug:
                log.debug(f"BGP.tools lookup failed for {ip_str}: {e}")

        # No match found
        if Settings.debug:
            log.debug(f"No enrichment data found for {ip_str}")
        return IPInfo(ip_str, asn=0, asn_name="Unknown")

    async def lookup_asn_name(self, asn: int) -> str:
        """Get the organization name for an ASN."""
        asn_data = self.asn_info.get(asn, {})
        name = asn_data.get("name")


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


async def refresh_ip_enrichment_data() -> bool:
    """Manually refresh IP enrichment data."""
    log.info("Manual refresh requested")
    # Since we no longer cache data, just return True to indicate the feature is available
    return True


def get_data_status() -> dict:
    """Get status information about IP enrichment data."""
    status = {
        "mode": "real-time",
        "data_source": "BGP.TOOLS",
        "cache_enabled": False,
        "last_update": "Real-time lookups via BGP.TOOLS",
        "data_counts": {
            "cached_ips": len(_service._ip_cache),
            "cached_asns": len(_service.asn_info),
        },
    }
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
