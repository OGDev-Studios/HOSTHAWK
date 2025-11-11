import os
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class ReportGenerator:
    def __init__(self, output_dir='reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.template_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            autoescape=True
        )
    
    def _get_timestamp(self):
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _save_report(self, content, filename, extension):
        filename = f"{filename}_{self._get_timestamp()}.{extension}"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def generate_json_report(self, data, filename='scan_report'):
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'tool': 'HostHawk',
                'version': '1.0.0'
            },
            'data': data
        }
        content = json.dumps(report, indent=2)
        return self._save_report(content, filename, 'json')
    
    def generate_html_report(self, data, template_name='report.html', filename='scan_report'):
        template = self.template_env.get_template(template_name)
        
        report_data = {
            'scan_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'hosts': [],
            'vulnerabilities': [],
            'statistics': {
                'total_hosts': 0,
                'open_ports': 0,
                'vulnerabilities_found': 0,
                'services_identified': 0
            }
        }
        
        if isinstance(data, dict) and 'hosts' in data:
            report_data['hosts'] = data['hosts']
            report_data['statistics']['total_hosts'] = len(data['hosts'])
            
            for host in data['hosts']:
                if 'ports' in host:
                    report_data['statistics']['open_ports'] += len(host['ports'])
                    for port in host['ports']:
                        if 'service' in port:
                            report_data['statistics']['services_identified'] += 1
                        if 'vulnerabilities' in port:
                            report_data['vulnerabilities'].extend(port['vulnerabilities'])
                            report_data['statistics']['vulnerabilities_found'] += len(port['vulnerabilities'])
        
        content = template.render(
            report=report_data,
            vulnerabilities=report_data['vulnerabilities'],
            stats=report_data['statistics']
        )
        
        self._copy_report_assets()
        
        return self._save_report(content, filename, 'html')
    
    def _copy_report_assets(self):
        assets_dir = os.path.join(os.path.dirname(__file__), 'templates', 'assets')
        target_assets_dir = os.path.join(self.output_dir, 'assets')
        
        if not os.path.exists(target_assets_dir):
            os.makedirs(target_assets_dir, exist_ok=True)
            
            for asset in os.listdir(assets_dir):
                src = os.path.join(assets_dir, asset)
                dst = os.path.join(target_assets_dir, asset)
                if os.path.isfile(src):
                    with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
                        f_dst.write(f_src.read())
    
    def generate_csv_report(self, data, filename='scan_report'):
        rows = []
        
        if isinstance(data, dict) and 'hosts' in data:
            for host in data['hosts']:
                host_ip = host.get('ip', 'Unknown')
                host_mac = host.get('mac', 'Unknown')
                host_status = host.get('status', 'Unknown')
                
                if 'ports' in host:
                    for port in host['ports']:
                        row = {
                            'Host': host_ip,
                            'MAC': host_mac,
                            'Status': host_status,
                            'Port': port.get('port', ''),
                            'Protocol': port.get('protocol', 'tcp'),
                            'State': port.get('status', ''),
                            'Service': port.get('service', {}).get('name', ''),
                            'Version': port.get('service', {}).get('version', ''),
                            'Vulnerabilities': ', '.join([v['id'] for v in port.get('vulnerabilities', [])])
                        }
                        rows.append(row)
                else:
                    rows.append({
                        'Host': host_ip,
                        'MAC': host_mac,
                        'Status': host_status,
                        'Port': '',
                        'Protocol': '',
                        'State': '',
                        'Service': '',
                        'Version': '',
                        'Vulnerabilities': ''
                    })
        
        if not rows:
            return None
            
        fieldnames = rows[0].keys()
        output = []
        
        output.append(','.join(fieldnames))
        
        for row in rows:
            output.append(','.join(['"' + str(row.get(field, '')).replace('"', '""') + '"' for field in fieldnames]))
        
        return self._save_report('\n'.join(output), filename, 'csv')
    
    def generate_xml_report(self, data, filename='scan_report'):
        root = ET.Element('nmaprun', {
            'scanner': 'HostHawk',
            'version': '1.0',
            'start': str(int(datetime.now().timestamp())),
            'xmloutputversion': '1.04'
        })
        
        scaninfo = ET.SubElement(root, 'scaninfo', {
            'type': 'syn',
            'protocol': 'tcp',
            'numservices': '1000',
            'services': '1-1000'
        })
        
        if isinstance(data, dict) and 'hosts' in data:
            for host in data['hosts']:
                host_elem = ET.SubElement(root, 'host')
                
                status = ET.SubElement(host_elem, 'status', {
                    'state': 'up' if host.get('status') == 'up' else 'down',
                    'reason': 'echo-reply'
                })
                
                if 'ip' in host:
                    ET.SubElement(host_elem, 'address', {
                        'addr': host['ip'],
                        'addrtype': 'ipv4'
                    })
                
                if 'mac' in host and host['mac'] != 'Unknown':
                    ET.SubElement(host_elem, 'address', {
                        'addr': host['mac'],
                        'addrtype': 'mac',
                        'vendor': host.get('vendor', 'Unknown')
                    })
                
                if 'ports' in host and host['ports']:
                    ports_elem = ET.SubElement(host_elem, 'ports')
                    
                    for port in host['ports']:
                        port_elem = ET.SubElement(ports_elem, 'port', {
                            'protocol': port.get('protocol', 'tcp'),
                            'portid': str(port.get('port', ''))
                        })
                        
                        ET.SubElement(port_elem, 'state', {
                            'state': port.get('status', '').lower(),
                            'reason': 'syn-ack',
                            'reason_ttl': '0'
                        })
                        
                        if 'service' in port:
                            service = port['service']
                            ET.SubElement(port_elem, 'service', {
                                'name': service.get('name', ''),
                                'product': service.get('product', ''),
                                'version': service.get('version', ''),
                                'extrainfo': service.get('extrainfo', '')
                            })
                        
                        if 'vulnerabilities' in port:
                            for vuln in port['vulnerabilities']:
                                ET.SubElement(port_elem, 'script', {
                                    'id': 'vuln-scan',
                                    'output': f"{vuln.get('id', '')}: {vuln.get('description', '')}"
                                })
        
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        return self._save_report(xml_str, filename, 'xml')
    
    def generate_report(self, data, format='html', **kwargs):
        format = format.lower()
        filename = kwargs.get('filename', 'scan_report')
        template_name = kwargs.get('template_name', 'report.html')
        
        if format == 'json':
            return self.generate_json_report(data, filename=filename)
        elif format == 'html':
            return self.generate_html_report(data, template_name=template_name, filename=filename)
        elif format == 'csv':
            return self.generate_csv_report(data, filename=filename)
        elif format == 'xml':
            return self.generate_xml_report(data, filename=filename)
        else:
            raise ValueError(f"Unsupported report format: {format}")
