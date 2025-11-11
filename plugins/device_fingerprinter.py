import socket
import re
import json
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether, ARP, Dot1Q, STP, CDP, LLDP
import dpkt
import struct

class DeviceFingerprinter:
    def __init__(self, timeout=2):
        self.timeout = timeout
        self.oui_file = None
        self.oui_db = {}
        self._load_oui_database()
    
    def _load_oui_database(self):
        try:
            import requests
            oui_url = "https://standards-oui.ieee.org/oui/oui.txt"
            response = requests.get(oui_url, timeout=10)
            if response.status_code == 200:
                self._parse_oui_data(response.text)
        except:
            pass
    
    def _parse_oui_data(self, oui_text):
        for line in oui_text.split('\n'):
            if '(base 16)' in line:
                parts = line.split('(base 16)')
                if len(parts) == 2:
                    oui = parts[0].strip().lower().replace('-', ':')
                    vendor = parts[1].strip()
                    self.oui_db[oui] = vendor
    
    def _get_vendor_from_mac(self, mac):
        if not mac or mac == '00:00:00:00:00:00':
            return "Unknown"
        
        mac = mac.lower()
        oui = ':'.join(mac.split(':')[:3])
        
        if oui in self.oui_db:
            return self.oui_db[oui]
        
        return "Unknown"
    
    def _tcp_fingerprint(self, ip, port=80, timeout=2):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            
            banner = b""
            try:
                if port == 80:
                    sock.send(b"GET / HTTP/1.0\r\n\r\n")
                    banner = sock.recv(1024)
                elif port == 21:
                    banner = sock.recv(1024)
                    sock.send(b"HELP\r\n")
                    banner += sock.recv(1024)
                elif port in [22, 23, 25, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432]:
                    banner = sock.recv(1024)
            except:
                pass
                
            sock.close()
            return banner.decode('utf-8', 'ignore')
        except:
            return ""
    
    def _analyze_tcp_banner(self, banner):
        if not banner:
            return {}
        
        result = {}
        
        if 'HTTP/' in banner:
            result['service'] = 'http'
            server_match = re.search(r'Server:\s*([^\r\n]+)', banner, re.IGNORECASE)
            if server_match:
                result['server_software'] = server_match.group(1).strip()
        
        elif '220' in banner and ('FTP' in banner or 'FileZilla' in banner):
            result['service'] = 'ftp'
            result['banner'] = banner.strip()
        
        elif 'SSH-' in banner:
            result['service'] = 'ssh'
            result['version'] = banner.split('\n')[0].strip()
        
        elif '220 ' in banner and ('ESMTP' in banner or 'SMTP' in banner):
            result['service'] = 'smtp'
            result['banner'] = banner.strip()
        
        return result
    
    def _analyze_network_traffic(self, pcap_file):
        results = []
        try:
            with open(pcap_file, 'rb') as f:
                pcap = dpkt.pcap.Reader(f)
                for ts, buf in pcap:
                    try:
                        eth = dpkt.ethernet.Ethernet(buf)
                        if not isinstance(eth.data, dpkt.ip.IP):
                            continue
                            
                        ip = eth.data
                        src_ip = socket.inet_ntoa(ip.src)
                        dst_ip = socket.inet_ntoa(ip.dst)
                        protocol = ip.p
                        
                        if protocol == dpkt.ip.IP_PROTO_TCP:
                            tcp = ip.data
                            result = {
                                'timestamp': ts,
                                'source_ip': src_ip,
                                'dest_ip': dst_ip,
                                'protocol': 'tcp',
                                'source_port': tcp.sport,
                                'dest_port': tcp.dport,
                                'flags': self._get_tcp_flags(tcp.flags)
                            }
                            
                            if tcp.dport == 80 and len(tcp.data) > 0:
                                try:
                                    http = dpkt.http.Request(tcp.data)
                                    result['http_method'] = http.method
                                    result['http_uri'] = http.uri
                                    result['http_version'] = http.version
                                    result['http_headers'] = dict(http.headers)
                                except:
                                    pass
                            
                            results.append(result)
                            
                    except Exception as e:
                        continue
        except Exception as e:
            pass
            
        return results
    
    def _get_tcp_flags(self, flags):
        flag_names = []
        if flags & dpkt.tcp.TH_FIN:
            flag_names.append('FIN')
        if flags & dpkt.tcp.TH_SYN:
            flag_names.append('SYN')
        if flags & dpkt.tcp.TH_RST:
            flag_names.append('RST')
        if flags & dpkt.tcp.TH_PUSH:
            flag_names.append('PSH')
        if flags & dpkt.tcp.TH_ACK:
            flag_names.append('ACK')
        if flags & dpkt.tcp.TH_URG:
            flag_names.append('URG')
        if flags & dpkt.tcp.TH_ECE:
            flag_names.append('ECE')
        if flags & dpkt.tcp.TH_CWR:
            flag_names.append('CWR')
        return '|'.join(flag_names) if flag_names else 'NONE'
    
    def _detect_network_devices(self, pkt):
        devices = {}
        
        if pkt.haslayer(CDP):
            device = {
                'type': 'network_device',
                'vendor': 'Cisco',
                'protocol': 'CDP'
            }
            
            if pkt[CDP].haslayer(CDPDeviceID):
                device['device_id'] = pkt[CDP].id.val
            if pkt[CDP].haslayer(CDPSoftwareVersion):
                device['software'] = pkt[CDP].software
            if pkt[CDP].haslayer(CDPPlatform):
                device['platform'] = pkt[CDP].platform
                
            src_mac = pkt[Ether].src
            device['mac_address'] = src_mac
            device['vendor'] = self._get_vendor_from_mac(src_mac)
            
            devices[src_mac] = device
        
        elif pkt.haslayer(LLDP):
            device = {
                'type': 'network_device',
                'protocol': 'LLDP'
            }
            
            if pkt[LLDP].haslayer(LLDPChassisID):
                device['chassis_id'] = pkt[LLDP].chassisid.id
            if pkt[LLDP].haslayer(LLDPPortID):
                device['port_id'] = pkt[LLDP].portid.id
            if pkt[LLDP].haslayer(LLDPSystemName):
                device['system_name'] = pkt[LLDP].systemname
            if pkt[LLDP].haslayer(LLDPSystemDescription):
                device['system_description'] = pkt[LLDP].systemdesc
            
            src_mac = pkt[Ether].src
            device['mac_address'] = src_mac
            device['vendor'] = self._get_vendor_from_mac(src_mac)
            
            devices[src_mac] = device
        
        elif pkt.haslayer(STP):
            device = {
                'type': 'switch',
                'protocol': 'STP'
            }
            
            stp = pkt[STP]
            device['root_id'] = stp.rootid
            device['bridge_id'] = stp.bridgeid
            device['port_id'] = stp.port
            
            src_mac = pkt[Ether].src
            device['mac_address'] = src_mac
            device['vendor'] = self._get_vendor_from_mac(src_mac)
            
            devices[src_mac] = device
        
        return devices
    
    def _analyze_dhcp(self, pkt):
        if not pkt.haslayer(DHCP):
            return {}
            
        dhcp = pkt[DHCP]
        options = {}
        
        for opt in dhcp.options:
            if isinstance(opt, tuple):
                options[opt[0]] = opt[1]
        
        result = {
            'type': 'dhcp',
            'client_mac': pkt[Ether].src,
            'options': options
        }
        
        if 'message-type' in options:
            msg_types = {
                1: 'DHCPDISCOVER',
                2: 'DHCPOFFER',
                3: 'DHCPREQUEST',
                4: 'DHCPDECLINE',
                5: 'DHCPACK',
                6: 'DHCPNAK',
                7: 'DHCPRELEASE',
                8: 'DHCPINFORM'
            }
            result['message_type'] = msg_types.get(options['message-type'], 'UNKNOWN')
        
        return result
    
    def fingerprint_device(self, ip, ports=[21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432, 8080]):
        results = {
            'ip': ip,
            'services': {},
            'os_fingerprint': {},
            'network_info': {}
        }
        
        try:
            ans, unans = arping(ip, timeout=self.timeout, verbose=0)
            if ans:
                mac = ans[0][1].hwsrc
                results['mac_address'] = mac
                results['vendor'] = self._get_vendor_from_mac(mac)
        except:
            pass
        
        for port in ports:
            try:
                banner = self._tcp_fingerprint(ip, port, self.timeout)
                if banner:
                    service_info = self._analyze_tcp_banner(banner)
                    if service_info:
                        results['services'][str(port)] = service_info
            except:
                pass
        
        try:
            ans = sr1(IP(dst=ip)/ICMP(), timeout=self.timeout, verbose=0)
            if ans:
                ttl = ans[IP].ttl
                if ttl <= 64:
                    results['os_fingerprint']['likely_os'] = 'Linux/Unix'
                elif ttl <= 128:
                    results['os_fingerprint']['likely_os'] = 'Windows'
                elif ttl <= 255:
                    results['os_fingerprint']['likely_os'] = 'Cisco/Network Device'
                results['os_fingerprint']['ttl'] = ttl
        except:
            pass
        
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            results['hostname'] = hostname
        except:
            pass
            
        return results
