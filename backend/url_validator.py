
import ipaddress
import socket
from urllib.parse import urlsplit


def validate_url(url: str) -> None:
    """Reject URLs that point to local or non-public network addresses."""

    try:
        parsed = urlsplit(str(url))

        # Allow only HTTP and HTTPS
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("Only HTTP and HTTPS URLs are allowed.")

        hostname = parsed.hostname

        if not hostname:
            raise ValueError("URL must contain a hostname.")

        # Reject embedded usernames/passwords
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("URLs containing credentials are not allowed.")

        hostname = hostname.rstrip(".").lower()

        # Block common local/internal hostnames
        if (
            hostname == "localhost"
            or hostname.endswith(".localhost")
            or hostname.endswith(".local")
            or hostname.endswith(".internal")
        ):
            raise ValueError("Local or internal hostnames are not allowed.")

        # Resolve the hostname and check every returned IP address
        try:
            addresses = socket.getaddrinfo(
                hostname,
                parsed.port or (443 if parsed.scheme.lower() == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror:
            raise ValueError("Hostname could not be resolved.")

        if not addresses:
            raise ValueError("Hostname has no valid IP addresses.")

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                raise ValueError(
                    "URLs pointing to private or reserved IP addresses are not allowed."
                )

    except ValueError:
        raise
    except Exception:
        raise ValueError("Invalid or unsafe URL.")
