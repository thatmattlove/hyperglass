def parse(output, type, cmd):
    """Splits Cisco IOS BGP output by AFI, returns only IPv4 & IPv6 output for protocol-agnostic commands (Community & AS_PATH Lookups)"""
    try:
        if cmd in ["bgp_community", "bgp_aspath"] and type in ["cisco_ios"]:
            delimiter = "For address family: "
            parsed_ipv4 = output.split(delimiter)[1]
            parsed_ipv6 = output.split(delimiter)[2]
            return delimiter + parsed_ipv4 + delimiter + parsed_ipv6
        else:
            return output
        if cmd in ["bgp_community", "bgp_aspath"] and type in ["cisco_xr"]:
            delimiter = "Address Family: "
            parsed_ipv4 = output.split(delimiter)[1]
            parsed_ipv6 = output.split(delimiter)[2]
            return delimiter + parsed_ipv4 + delimiter + parsed_ipv6
    except:
        raise
