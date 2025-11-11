from fpdf import FPDF
from datetime import datetime
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class PDFReportGenerator:
    def __init__(self, title: str = "HostHawk Scan Report"):
        self.pdf = FPDF()
        self.title = title
        self.colors = {
            'primary': (45, 62, 80),
            'secondary': (52, 152, 219),
            'success': (46, 204, 113),
            'warning': (241, 196, 15),
            'danger': (231, 76, 60),
            'light': (236, 240, 241),
            'dark': (44, 62, 80),
            'text': (52, 73, 94)
        }
        self._setup_document()
    
    def _setup_document(self) -> None:
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        self._add_header()
    
    def _add_header(self) -> None:
        self.pdf.set_fill_color(*self.colors['primary'])
        self.pdf.rect(0, 0, 210, 30, 'F')
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font('Arial', 'B', 18)
        self.pdf.cell(0, 20, self.title, 0, 1, 'C')
        self.pdf.ln(10)
    
    def add_title(self, title: str, level: int = 1) -> None:
        self.pdf.set_font('Arial', 'B', 16 - (level * 2) if level < 4 else 10)
        self.pdf.set_text_color(*self.colors['primary'])
        self.pdf.cell(0, 10, title, 0, 1, 'L')
        self.pdf.ln(2)
    
    def add_paragraph(self, text: str) -> None:
        self.pdf.set_font('Arial', '', 12)
        self.pdf.set_text_color(*self.colors['text'])
        self.pdf.multi_cell(0, 10, text)
        self.pdf.ln(5)
    
    def add_table(self, data: List[List[str]], header: List[str] = None) -> None:
        if header:
            self._add_table_header(header)
        
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.colors['text'])
        
        for row in data:
            for item in row:
                self.pdf.cell(190 / len(row), 10, str(item), 1, 0, 'C')
            self.pdf.ln()
        
        self.pdf.ln(10)
    
    def _add_table_header(self, headers: List[str]) -> None:
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.set_fill_color(*self.colors['light'])
        self.pdf.set_text_color(*self.colors['dark'])
        
        for header in headers:
            self.pdf.cell(190 / len(headers), 10, header, 1, 0, 'C', 1)
        
        self.pdf.ln()
    
    def add_scan_summary(self, summary: Dict[str, Any]) -> None:
        self.add_title("Scan Summary", 2)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.set_text_color(*self.colors['dark'])
        
        for key, value in summary.items():
            self.pdf.cell(60, 10, f"{key}:", 0, 0, 'L')
            self.pdf.set_font('Arial', '', 12)
            self.pdf.cell(0, 10, str(value), 0, 1, 'L')
            self.pdf.set_font('Arial', 'B', 12)
        
        self.pdf.ln(10)
    
    def add_vulnerability_findings(self, findings: List[Dict[str, Any]]) -> None:
        if not findings:
            return
            
        self.add_title("Vulnerability Findings", 2)
        
        for finding in findings:
            self.pdf.set_fill_color(*self.colors['light'])
            self.pdf.set_font('Arial', 'B', 12)
            self.pdf.cell(0, 10, finding.get('title', 'Vulnerability'), 1, 1, 'L', 1)
            
            self.pdf.set_font('Arial', '', 10)
            self.pdf.set_text_color(*self.colors['text'])
            
            details = [
                ("Severity", finding.get('severity', 'N/A')),
                ("Confidence", finding.get('confidence', 'N/A')),
                ("Location", finding.get('location', 'N/A')),
                ("Description", finding.get('description', '')),
                ("Impact", finding.get('impact', '')),
                ("Recommendation", finding.get('recommendation', ''))
            ]
            
            for label, value in details:
                self.pdf.set_font('Arial', 'B', 10)
                self.pdf.cell(40, 8, f"{label}:", 0, 0, 'L')
                self.pdf.set_font('Arial', '', 10)
                self.pdf.multi_cell(0, 8, str(value) if value else 'N/A')
                self.pdf.ln(3)
            
            self.pdf.ln(5)
    
    def add_executive_summary(self, summary: Dict[str, Any]) -> None:
        self.add_page_break()
        self.add_title("Executive Summary", 1)
        
        stats = [
            ("Total Hosts Scanned", summary.get('total_hosts', 0)),
            ("Open Ports Found", summary.get('open_ports', 0)),
            ("Critical Vulnerabilities", summary.get('critical_vulns', 0)),
            ("High Severity Vulnerabilities", summary.get('high_vulns', 0)),
            ("Medium Severity Vulnerabilities", summary.get('medium_vulns', 0)),
            ("Low Severity Vulnerabilities", summary.get('low_vulns', 0)),
            ("Scan Duration", summary.get('duration', 'N/A')),
            ("Scan Completed", summary.get('end_time', 'N/A'))
        ]
        
        self.add_table([stats])
        
        if 'overview' in summary:
            self.add_paragraph(summary['overview'])
        
        if 'key_findings' in summary and isinstance(summary['key_findings'], list):
            self.add_title("Key Findings", 2)
            for i, finding in enumerate(summary['key_findings'], 1):
                self.pdf.set_font('Arial', 'B', 10)
                self.pdf.cell(10, 6, f"{i}.", 0, 0, 'L')
                self.pdf.set_font('Arial', '', 10)
                self.pdf.multi_cell(0, 6, finding)
                self.pdf.ln(2)
    
    def add_page_break(self) -> None:
        self.pdf.add_page()
        self._add_header()
    
    def save(self, filename: str) -> str:
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        self.pdf.output(filename)
        return os.path.abspath(filename)


def generate_pdf_report(scan_data: Dict[str, Any], output_path: str = "reports") -> str:
    """
    Generate a comprehensive PDF report from scan data.
    
    Args:
        scan_data: Dictionary containing scan results
        output_path: Directory to save the report
        
    Returns:
        Path to the generated PDF file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_path, f"hosthawk_scan_report_{timestamp}.pdf")
    
    pdf = PDFReportGenerator(f"HostHawk Scan Report - {timestamp}")
    
    if 'executive_summary' in scan_data:
        pdf.add_executive_summary(scan_data['executive_summary'])
    
    if 'scan_summary' in scan_data:
        pdf.add_scan_summary(scan_data['scan_summary'])
    
    if 'vulnerabilities' in scan_data and scan_data['vulnerabilities']:
        pdf.add_page_break()
        pdf.add_title("Detailed Vulnerability Findings", 1)
        pdf.add_vulnerability_findings(scan_data['vulnerabilities'])
    
    if 'hosts' in scan_data and scan_data['hosts']:
        pdf.add_page_break()
        pdf.add_title("Scanned Hosts", 1)
        
        for host_data in scan_data['hosts']:
            pdf.add_title(f"Host: {host_data.get('ip', 'Unknown')}", 2)
            
            if 'open_ports' in host_data and host_data['open_ports']:
                ports_table = [[p['port'], p['service'], p.get('version', 'N/A')] 
                             for p in host_data['open_ports']]
                pdf.add_table(ports_table, ["Port", "Service", "Version"])
            
            if 'vulnerabilities' in host_data and host_data['vulnerabilities']:
                pdf.add_title("Host Vulnerabilities", 3)
                pdf.add_vulnerability_findings(host_data['vulnerabilities'])
    
    if 'recommendations' in scan_data and scan_data['recommendations']:
        pdf.add_page_break()
        pdf.add_title("Security Recommendations", 1)
        
        for i, rec in enumerate(scan_data['recommendations'], 1):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"{i}. {rec.get('title', 'Recommendation')}", 0, 1)
            
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, rec.get('description', ''))
            
            if 'steps' in rec and rec['steps']:
                for j, step in enumerate(rec['steps'], 1):
                    pdf.cell(10, 6, "", 0, 0)
                    pdf.cell(0, 6, f"{j}. {step}", 0, 1)
            
            pdf.ln(5)
    
    return pdf.save(filename)
