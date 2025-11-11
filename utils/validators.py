import ipaddress
import re
from typing import List, Tuple, Union
from ..exceptions import InvalidTargetException, InvalidPortRangeException


def validate_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        raise InvalidTargetException(f"Invalid IP address: {ip}")


def validate_cidr(cidr: str) -> bool:
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        raise InvalidTargetException(f"Invalid CIDR notation: {cidr}")


def validate_port(port: int) -> bool:
    if not isinstance(port, int):
        raise InvalidPortRangeException(f"Port must be an integer: {port}")
    
    if port < 1 or port > 65535:
        raise InvalidPortRangeException(f"Port must be between 1 and 65535: {port}")
    
    return True


def validate_port_range(port_range: str) -> List[int]:
    ports = []
    
    try:
        for part in port_range.split(','):
            part = part.strip()
            
            if '-' in part:
                start, end = map(int, part.split('-'))
                
                if start < 1 or end > 65535 or start > end:
                    raise InvalidPortRangeException(
                        f"Invalid port range: {part}. Ports must be between 1-65535 and start <= end"
                    )
                
                ports.extend(range(start, end + 1))
            else:
                port = int(part)
                validate_port(port)
                ports.append(port)
        
        return sorted(set(ports))
    
    except ValueError as e:
        raise InvalidPortRangeException(f"Invalid port range format: {port_range}") from e


def validate_hostname(hostname: str) -> bool:
    if len(hostname) > 255:
        raise InvalidTargetException(f"Hostname too long: {hostname}")
    
    if hostname[-1] == ".":
        hostname = hostname[:-1]
    
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    
    if not all(allowed.match(x) for x in hostname.split(".")):
        raise InvalidTargetException(f"Invalid hostname: {hostname}")
    
    return True


def sanitize_input(input_str: str) -> str:
    dangerous_chars = ['&', '|', ';', '$', '`', '\n', '\r']
    
    for char in dangerous_chars:
        if char in input_str:
            raise InvalidTargetException(f"Input contains dangerous character: {char}")
    
    return input_str.strip()
