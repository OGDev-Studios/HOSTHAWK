import socket
import concurrent.futures
import ipaddress
from typing import List, Dict, Tuple, Optional, Union
import nmap
import re

class PortScanner:
    def __init__(self, target: str, ports: Union[str, List[int], None] = None, 
                 max_threads: int = 100, timeout: float = 1.0):
        self.target = target
        self.ports = self._parse_ports(ports) if ports else list(range(1, 1025))
        self.max_threads = max_threads
        self.timeout = timeout
        self.open_ports = []
        self.service_versions = {}
        self.nm = nmap.PortScanner()
        
    def _parse_ports(self, ports: Union[str, List[int]]) -> List[int]:
        if isinstance(ports, str):
            port_list = []
            for part in ports.split(','):
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    port_list.extend(range(start, end + 1))
                else:
                    port_list.append(int(part))
            return sorted(set(port_list))
        return ports
    
    def scan_port(self, port: int) -> Optional[Tuple[int, str]]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            if result == 0:
                service = self._get_service_name(port)
                return port, service
        except Exception as e:
            pass
        return None
    
    def _get_service_name(self, port: int) -> str:
        try:
            return socket.getservbyport(port)
        except:
            return "unknown"
    
    def fast_scan(self) -> List[Dict]:
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_port = {executor.submit(self.scan_port, port): port for port in self.ports}
            for future in concurrent.futures.as_completed(future_to_port):
                result = future.result()
                if result:
                    port, service = result
                    results.append({"port": port, "service": service, "state": "open"})
        return sorted(results, key=lambda x: x["port"])
    
    def service_scan(self, ports: str = None) -> Dict:
        if not ports and self.open_ports:
            ports = ",".join(str(p["port"]) for p in self.open_ports)
        elif not ports:
            ports = ",".join(str(p) for p in self.ports)
            
        self.nm.scan(hosts=self.target, ports=ports, arguments='-sV --version-intensity 3')
        
        results = {}
        for host in self.nm.all_hosts():
            results[host] = {}
            for proto in self.nm[host].all_protocols():
                results[host][proto] = {}
                for port in self.nm[host][proto]:
                    port_info = self.nm[host][proto][port]
                    results[host][proto][port] = {
                        'state': port_info['state'],
                        'service': port_info['name'],
                        'version': port_info.get('version', 'unknown'),
                        'product': port_info.get('product', ''),
                        'extrainfo': port_info.get('extrainfo', '')
                    }
        return results
    
    def os_detection(self) -> Dict:
        self.nm.scan(hosts=self.target, arguments='-O')
        results = {}
        for host in self.nm.all_hosts():
            if 'osmatch' in self.nm[host]:
                results[host] = [{
                    'name': os_match['name'],
                    'accuracy': os_match['accuracy'],
                    'osclass': [{
                        'type': os_class['type'],
                        'vendor': os_class['vendor'],
                        'osfamily': os_class['osfamily'],
                        'osgen': os_class.get('osgen', '')
                    } for os_class in os_match.get('osclass', [])]
                } for os_match in self.nm[host]['osmatch']]
        return results
    
    def export_scan_results(self, filename: str, format_type: str = 'json') -> bool:
        try:
            if format_type == 'json':
                import json
                with open(f"{filename}.json", 'w') as f:
                    json.dump({
                        'open_ports': self.open_ports,
                        'service_versions': self.service_versions
                    }, f, indent=4)
            elif format_type == 'csv':
                import csv
                with open(f"{filename}.csv", 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Port', 'Service', 'State', 'Version', 'Product'])
                    for port in self.open_ports:
                        svc = self.service_versions.get(str(port), {})
                        writer.writerow([
                            port,
                            svc.get('service', ''),
                            'open',
                            svc.get('version', ''),
                            svc.get('product', '')
                        ])
            return True
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False
