import socket
import threading
import ipaddress
import queue
import time
import json
from scapy.all import *
from scapy.layers.inet import IP, ICMP, TCP, UDP, traceroute
from scapy.layers.l2 import ARP, Ether, getmacbyip
from scapy.sendrecv import sr, sr1, srp, srp1
import netifaces
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..plugins.vulnerability_scanner import VulnerabilityScanner

class NetworkScanner:
    def __init__(self, timeout=2, threads=50):
        self.timeout = timeout
        self.threads = threads
        self.lock = threading.Lock()
        self.results = []
        self.stop_event = threading.Event()
        self.vuln_scanner = VulnerabilityScanner(timeout=timeout)
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = timeout
        self.dns_resolver.lifetime = timeout

    def _ping_scan(self, ip):
        try:
            pkt = IP(dst=str(ip))/ICMP()
            resp = sr1(pkt, timeout=self.timeout, verbose=0)
            if resp is not None:
                return str(ip)
        except Exception:
            pass
        return None

    def _arp_scan(self, ip, interface):
        try:
            pkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=str(ip))
            resp = srp1(pkt, timeout=self.timeout, iface=interface, verbose=0)
            if resp is not None:
                return str(ip), resp[Ether].src
        except Exception:
            pass
        return None, None

    def _tcp_scan(self, target, port, scan_type="connect"):
        try:
            if scan_type == "syn":
                pkt = IP(dst=target)/TCP(dport=port, flags="S")
                resp = sr1(pkt, timeout=self.timeout, verbose=0)
                if resp is not None and resp.haslayer(TCP):
                    if resp[TCP].flags & 0x12:
                        return port, "open"
                    elif resp[TCP].flags & 0x14:
                        return port, "closed"
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((target, port))
                sock.close()
                if result == 0:
                    return port, "open"
                return port, "closed"
        except Exception:
            pass
        return port, "filtered"

    def _udp_scan(self, target, port):
        try:
            pkt = IP(dst=target)/UDP(dport=port)
            resp = sr1(pkt, timeout=self.timeout, verbose=0)
            if resp is None:
                return port, "open|filtered"
            elif resp.haslayer(ICMP):
                if int(resp[ICMP].type) == 3 and int(resp[ICMP].code) in [1, 2, 3, 9, 10, 13]:
                    return port, "filtered"
                elif int(resp[ICMP].type) == 3 and int(resp[ICMP].code) in [3]:
                    return port, "closed"
        except Exception:
            pass
        return port, "open|filtered"

    def _service_detection(self, target, port, protocol="tcp"):
        banner = ""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM if protocol == "tcp" else socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            sock.connect((target, port))
            
            if protocol == "tcp":
                try:
                    if port == 80:
                        sock.send(b"GET / HTTP/1.0\r\n\r\n")
                        banner = sock.recv(4096).decode('utf-8', 'ignore').strip()
                    elif port == 21:
                        banner = sock.recv(1024).decode('utf-8', 'ignore').strip()
                        sock.send(b"HELP\r\n")
                        banner += "\n" + sock.recv(1024).decode('utf-8', 'ignore').strip()
                    elif port == 25 or port == 587:
                        banner = sock.recv(1024).decode('utf-8', 'ignore').strip()
                        sock.send(b"HELO example.com\r\n")
                        banner += "\n" + sock.recv(1024).decode('utf-8', 'ignore').strip()
                    else:
                        sock.send(b"\r\n")
                        banner = sock.recv(1024).decode('utf-8', 'ignore').strip()
                except socket.timeout:
                    pass
            
            if banner:
                self.vuln_scanner.scan_port(target, port, protocol, banner)
            
            sock.close()
            return banner
        except Exception as e:
            return ""

    def _os_fingerprint(self, target):
        try:
            ttl_values = []
            for _ in range(3):
                pkt = IP(dst=target, ttl=128)/ICMP()
                resp = sr1(pkt, timeout=self.timeout, verbose=0)
                if resp:
                    ttl_values.append(resp[IP].ttl)
            
            if ttl_values:
                avg_ttl = sum(ttl_values) / len(ttl_values)
                if 64 <= avg_ttl <= 128:
                    return "Linux/Unix"
                elif 128 <= avg_ttl <= 255:
                    return "Windows"
                elif 64 <= avg_ttl <= 64:
                    return "Linux"
                elif 255 <= avg_ttl <= 255:
                    return "Windows"
        except Exception:
            pass
        return "Unknown"

    def _worker(self, task_queue, scan_func, *args):
        while not self.stop_event.is_set() and not task_queue.empty():
            try:
                target = task_queue.get_nowait()
                result = scan_func(target, *args)
                if result and result[0]:
                    with self.lock:
                        self.results.append(result)
                task_queue.task_done()
            except queue.Empty:
                break

    def _run_scan(self, targets, scan_func, *args):
        task_queue = queue.Queue()
        for target in targets:
            task_queue.put(target)
        
        threads = []
        for _ in range(min(self.threads, task_queue.qsize())):
            t = threading.Thread(target=self._worker, args=(task_queue, scan_func, *args))
            t.daemon = True
            t.start()
            threads.append(t)
        
        try:
            while any(t.is_alive() for t in threads):
                time.sleep(0.1)
                if self.stop_event.is_set():
                    break
        except KeyboardInterrupt:
            self.stop_event.set()
            for t in threads:
                t.join()
            raise
        
        return [r for r in self.results if r]

    def scan_network(self, network, interface=None):
        self.results = []
        targets = [str(ip) for ip in ipaddress.IPv4Network(network, strict=False)]
        
        if interface and netifaces.AF_LINK in netifaces.ifaddresses(interface):
            scan_func = lambda ip: self._arp_scan(ip, interface)
        else:
            scan_func = self._ping_scan
        
        return self._run_scan(targets, scan_func)

    def scan_ports(self, target, ports, protocol="tcp", scan_type="connect"):
        self.results = []
        if isinstance(ports, str) and '-' in ports:
            start, end = map(int, ports.split('-'))
            ports = range(start, end + 1)
        elif isinstance(ports, str):
            ports = [int(p) for p in ports.split(',')]
        
        scan_func = self._tcp_scan if protocol.lower() == "tcp" else self._udp_scan
        return self._run_scan(ports, scan_func, target, scan_type if protocol.lower() == "tcp" else None)

    def _dns_enumeration(self, domain):
        records = {}
        try:
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
            
            for rtype in record_types:
                try:
                    answers = self.dns_resolver.resolve(domain, rtype, raise_on_no_answer=False)
                    if answers.rrset is not None:
                        records[rtype] = [str(r) for r in answers.rrset]
                except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                    continue
            
            if 'NS' in records:
                for ns in records['NS']:
                    try:
                        zone = dns.zone.from_xfr(dns.query.xfr(ns, domain, timeout=self.timeout))
                        records['AXFR'] = [str(record[0]) for record in zone.iterate_rdatas()]
                        break
                    except Exception:
                        continue
            
            return records
        except Exception as e:
            return {}

    def traceroute(self, target, max_hops=30):
        results = []
        try:
            ans, unans = traceroute(target, maxttl=max_hops, timeout=self.timeout, verbose=0)
            
            for snd, rcv in ans:
                results.append({
                    'ttl': snd.ttl,
                    'ip': rcv.src,
                    'rtt': (rcv.time - snd.sent_time) * 1000,
                    'is_target': rcv.src == target
                })
                
                if rcv.src == target:
                    break
                    
        except Exception as e:
            pass
            
        return results

    def get_vulnerabilities(self):
        return self.vuln_scanner.get_vulnerabilities()

    def stop_scan(self):
        self.stop_event.set()
