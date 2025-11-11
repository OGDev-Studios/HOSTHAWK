import argparse
import sys
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from .core.scanner import NetworkScanner
from .output.formatters import OutputFormatter

def parse_ports(port_str):
    if not port_str:
        return list(range(1, 1025))
    
    ports = set()
    for part in port_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.update(range(start, end + 1))
        else:
            ports.add(int(part))
    return sorted(ports)

def format_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_status(message, status_type="info"):
    colors = {
        "info": "\033[94m",
        "success": "\033[92m",
        "warning": "\033[93m",
        "error": "\033[91m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(status_type, '')}[{format_timestamp()}] {message}{colors['reset']}")

def main():
    parser = argparse.ArgumentParser(description='HostHawk - Enterprise Network Scanner')
    
    scan_group = parser.add_argument_group('Scan Types')
    scan_type = scan_group.add_mutually_exclusive_group(required=True)
    scan_type.add_argument('--host', help='Single host to scan')
    scan_type.add_argument('--network', help='Network to scan in CIDR notation (e.g., 192.168.1.0/24)')
    scan_type.add_argument('--dns-enum', metavar='DOMAIN', help='Perform DNS enumeration on a domain')
    scan_type.add_argument('--traceroute', metavar='HOST', help='Perform a traceroute to a host')
    
    port_group = parser.add_argument_group('Port Scanning')
    port_group.add_argument('-p', '--ports', help='Ports to scan (e.g., 80,443 or 1-1024)')
    port_group.add_argument('--protocol', choices=['tcp', 'udp'], default='tcp', help='Protocol to scan (default: tcp)')
    port_group.add_argument('--scan-type', choices=['connect', 'syn'], default='connect', 
                          help='Port scan type (default: connect)')
    
    vuln_group = parser.add_argument_group('Vulnerability Scanning')
    vuln_group.add_argument('--vuln-scan', action='store_true',
                          help='Enable vulnerability scanning on open ports')
    
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('-o', '--output', help='Output file')
    output_group.add_argument('--format', choices=['json', 'csv', 'xml'], default='json',
                            help='Output format (default: json)')
    output_group.add_argument('-v', '--verbose', action='store_true',
                            help='Show detailed scan progress')
    
    performance_group = parser.add_argument_group('Performance Options')
    performance_group.add_argument('-t', '--threads', type=int, default=50,
                                 help='Number of threads (default: 50)')
    performance_group.add_argument('--timeout', type=float, default=2.0,
                                 help='Timeout in seconds (default: 2.0)')
    
    args = parser.parse_args()
    
    try:
        scanner = NetworkScanner(timeout=args.timeout, threads=args.threads)
        results = {}
        
        if args.dns_enum:
            print_status(f"Starting DNS enumeration for {args.dns_enum}...", "info")
            dns_results = scanner._dns_enumeration(args.dns_enum)
            results = {
                'scan_type': 'dns_enum',
                'target': args.dns_enum,
                'results': dns_results
            }
            
            if args.verbose:
                print_status("DNS Enumeration Results:", "success")
                for rtype, records in dns_results.items():
                    print(f"{rtype}:")
                    for record in records:
                        print(f"  {record}")
        
        elif args.traceroute:
            print_status(f"Starting traceroute to {args.traceroute}...", "info")
            trace_results = scanner.traceroute(args.traceroute)
            results = {
                'scan_type': 'traceroute',
                'target': args.traceroute,
                'hops': trace_results
            }
            
            if args.verbose:
                print_status("Traceroute Results:", "success")
                for hop in trace_results:
                    status = ""
                    if hop['is_target']:
                        status = " <-- TARGET"
                    print(f"{hop['ttl']:>3}  {hop['ip']:15}  {hop['rtt']:.2f}ms{status}")
        
        elif args.host or args.network:
            target = args.host if args.host else args.network
            print_status(f"Starting scan on {target}...", "info")
            
            if args.host:
                target = args.host
                if args.ports:
                    ports = parse_ports(args.ports)
                    if args.verbose:
                        print_status(f"Scanning {len(ports)} ports on {target}...", "info")
                    
                    port_results = scanner.scan_ports(target, ports, args.protocol, args.scan_type)
                    host_results = []
                    
                    for port, status in port_results:
                        result = {
                            'port': port,
                            'protocol': args.protocol,
                            'status': status
                        }
                        
                        if status == 'open':
                            if args.verbose:
                                print_status(f"Port {port}/tcp is open", "success")
                            banner = scanner._service_detection(target, port, args.protocol)
                            if banner:
                                result['banner'] = banner
                                
                            if args.vuln_scan:
                                print_status(f"Scanning for vulnerabilities on {target}:{port}...", "info")
                                vulns = scanner.get_vulnerabilities()
                                if vulns:
                                    result['vulnerabilities'] = vulns
                                    for vuln in vulns:
                                        print_status(f"Found {vuln['type']} vulnerability: {vuln['details']}", "warning")
                        
                        host_results.append(result)
                    
                    results = {
                        'scan_type': 'port_scan',
                        'target': target,
                        'ports': host_results
                    }
                else:
                    os_info = scanner._os_fingerprint(target)
                    results = {
                        'scan_type': 'host_discovery',
                        'target': target,
                        'status': 'alive',
                        'os': os_info
                    }
                    if args.verbose:
                        print_status(f"Host {target} is alive. OS: {os_info}", "success")
            
            elif args.network:
                if args.verbose:
                    print_status(f"Discovering hosts on {args.network}...", "info")
                
                live_hosts = scanner.scan_network(args.network)
                network_results = []
                
                for host_info in live_hosts:
                    if isinstance(host_info, tuple):
                        ip, mac = host_info
                        host_result = {'ip': ip, 'mac': mac, 'status': 'alive'}
                    else:
                        ip = host_info
                        host_result = {'ip': ip, 'status': 'alive'}
                    
                    if args.ports:
                        ports = parse_ports(args.ports)
                        if args.verbose:
                            print_status(f"Scanning {len(ports)} ports on {ip}...", "info")
                        
                        port_results = scanner.scan_ports(ip, ports, args.protocol, args.scan_type)
                        host_ports = []
                        
                        for port, status in port_results:
                            port_info = {
                                'port': port,
                                'protocol': args.protocol,
                                'status': status
                            }
                            
                            if status == 'open':
                                if args.verbose:
                                    print_status(f"  Port {port}/tcp is open on {ip}", "success")
                                banner = scanner._service_detection(ip, port, args.protocol)
                                if banner:
                                    port_info['banner'] = banner
                                
                                if args.vuln_scan:
                                    print_status(f"  Scanning for vulnerabilities on {ip}:{port}...", "info")
                                    vulns = scanner.get_vulnerabilities()
                                    if vulns:
                                        port_info['vulnerabilities'] = vulns
                                        for vuln in vulns:
                                            print_status(f"  Found {vuln['type']} vulnerability: {vuln['details']}", "warning")
                            
                            host_ports.append(port_info)
                        
                        if host_ports:
                            host_result['ports'] = host_ports
                    
                    network_results.append(host_result)
                
                results = {
                    'scan_type': 'network_scan',
                    'network': args.network,
                    'hosts': network_results
                }
        
        if not results:
            print_status("No results found.", "error")
            sys.exit(1)
        
        output = OutputFormatter.format(results, args.format, args.output)
        
        if not args.output:
            print(output)
        else:
            print_status(f"Results saved to {args.output}", "success")
    
    except KeyboardInterrupt:
        print("\nScan stopped by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
