import dns.resolver
import dns.reversename
import socket
import concurrent.futures
from typing import Dict, List, Optional, Tuple

class DNSEnumerator:
    def __init__(self, domain: str, wordlist: Optional[List[str]] = None):
        self.domain = domain
        self.wordlist = wordlist or self._default_wordlist()
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 3
        self.resolver.lifetime = 3
        self.found_records = {
            'A': [],
            'MX': [],
            'NS': [],
            'TXT': [],
            'CNAME': [],
            'SOA': [],
            'subdomains': []
        }

    def _default_wordlist(self) -> List[str]:
        return [
            'www', 'mail', 'smtp', 'pop', 'imap', 'webmail', 'dev', 'test',
            'staging', 'api', 'vpn', 'admin', 'portal', 'secure', 'ns1', 'ns2'
        ]

    def get_a_record(self, hostname: str) -> List[str]:
        try:
            return [str(ip) for ip in self.resolver.resolve(hostname, 'A')]
        except:
            return []

    def get_mx_records(self) -> List[Tuple[str, int]]:
        try:
            return [(str(mx.exchange), mx.preference) for mx in self.resolver.resolve(self.domain, 'MX')]
        except:
            return []

    def get_ns_records(self) -> List[str]:
        try:
            return [str(ns) for ns in self.resolver.resolve(self.domain, 'NS')]
        except:
            return []

    def get_txt_records(self) -> List[str]:
        try:
            return [str(txt) for txt in self.resolver.resolve(self.domain, 'TXT')]
        except:
            return []

    def get_soa_record(self) -> List[str]:
        try:
            return [str(soa) for soa in self.resolver.resolve(self.domain, 'SOA')]
        except:
            return []

    def reverse_dns_lookup(self, ip: str) -> str:
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return ""

    def check_subdomain(self, subdomain: str) -> bool:
        hostname = f"{subdomain}.{self.domain}"
        try:
            ip = socket.gethostbyname(hostname)
            self.found_records['subdomains'].append({
                'subdomain': hostname,
                'ip': ip,
                'reverse_dns': self.reverse_dns_lookup(ip)
            })
            return True
        except:
            return False

    def enumerate_subdomains(self, max_workers: int = 10) -> Dict:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.check_subdomain, word) for word in self.wordlist]
            concurrent.futures.wait(futures)
        return self.found_records

    def get_all_records(self) -> Dict:
        self.found_records.update({
            'A': self.get_a_record(self.domain),
            'MX': self.get_mx_records(),
            'NS': self.get_ns_records(),
            'TXT': self.get_txt_records(),
            'SOA': self.get_soa_record()
        })
        return self.found_records

    def export_to_json(self, filename: str) -> bool:
        try:
            import json
            with open(filename, 'w') as f:
                json.dump(self.found_records, f, indent=4)
            return True
        except:
            return False
