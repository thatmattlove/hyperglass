# flake8: noqa
# WORK IN PROGRESS

"""Linux-style parsers for ping & traceroute."""

# Standard Library
import re

# Project
from hyperglass.exceptions import ParsingError


def _process_numbers(numbers):
    """Convert string to float or int."""
    for num in numbers:
        num = float(num)
        if num.is_integer():
            num = int(num)
        yield num


def parse_linux_ping(output):
    """Parse standard Linux-style ping output to structured data.

    Example:
    64 bytes from 1.1.1.1: icmp_seq=0 ttl=59 time=1.151 ms
    64 bytes from 1.1.1.1: icmp_seq=1 ttl=59 time=1.180 ms
    64 bytes from 1.1.1.1: icmp_seq=2 ttl=59 time=1.170 ms
    64 bytes from 1.1.1.1: icmp_seq=3 ttl=59 time=1.338 ms
    64 bytes from 1.1.1.1: icmp_seq=4 ttl=59 time=4.913 ms

    --- 1.1.1.1 ping statistics ---
    5 packets transmitted, 5 packets received, 0% packet loss
    round-trip min/avg/max/stddev = 1.151/1.950/4.913/1.483 ms
    """
    try:
        # Extract target host
        host = re.findall(r"^PING (.+) \(.+\): \d+ data bytes", output)[0]

        # Separate echo replies from summary info
        replies, _stats = re.split(r"--- .+ ---", output)
        replies = [l for l in replies.splitlines()[1:] if l]

        reply_stats = []
        for line in replies:
            # Extract the numerical values from each echo reply line
            bytes_seq_ttl_rtt = re.findall(
                r"(\d+) bytes.+ icmp_seq=(\d+) ttl=(\d+) time=(\d+\.\d+).*", line
            )[0]

            _bytes, seq, ttl, rtt = _process_numbers(bytes_seq_ttl_rtt)

            reply_stats.append(
                {"bytes": _bytes, "sequence": seq, "ttl": ttl, "rtt": rtt}
            )

        stats = [l for l in _stats.splitlines() if l]

        # Extract the top summary line numbers & process
        tx_rx_loss = re.findall(r"(\d+) .+, (\d+) .+, (\d+)\%.+", stats[0])[0]
        tx, rx, loss = _process_numbers(tx_rx_loss)

        # Extract the bottom summary line numbers & process
        rt = stats[1].split(" = ")[1]
        min_max_avg = rt.split("/")[:-1]
        _min, _max, _avg = _process_numbers(min_max_avg)

        return {
            "host": host,
            "transmitted": tx,
            "received": rx,
            "loss_percent": loss,
            "min_rtt": _min,
            "max_rtt": _max,
            "avg_rtt": _avg,
            "replies": reply_stats,
        }

    except (KeyError, ValueError) as err:
        # KeyError for empty findalls, ValueError for regex errors
        raise ParsingError("Error parsing ping response: {e}", e=str(err))
