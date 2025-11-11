import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import concurrent.futures
from typing import Set, Dict, List, Optional, Tuple
import ssl
import socket
import whois
from datetime import datetime

class WebCrawler:
    def __init__(self, base_url: str, max_depth: int = 2, max_pages: int = 50, 
                 user_agent: str = None, timeout: int = 10):
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls = set()
        self.external_urls = set()
        self.forms = []
        self.assets = []
        self.sitemap = {}
        self.cookies = {}
        self.session = requests.Session()
        self.session.verify = False
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        requests.packages.urllib3.disable_warnings()
        
    def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    
    def get_domain_info(self) -> Dict:
        try:
            domain = urlparse(self.base_url).netloc
            w = whois.whois(domain)
            return {
                'domain_name': w.domain_name,
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': w.name_servers,
                'status': w.status,
                'emails': w.emails,
                'dnssec': w.dnssec
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_ssl_cert_info(self) -> Dict:
        try:
            hostname = urlparse(self.base_url).netloc
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    not_after = dict(x[0] for x in cert['notAfter'].split())
                    expiry_date = datetime.strptime(
                        f"{not_after['D']} {not_after['M']} {not_after['Y']} {not_after['H']}:{not_after['M']}:{not_after['S']}",
                        "%d %b %Y %H:%M:%S"
                    )
                    
                    return {
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'subject': dict(x[0] for x in cert['subject']),
                        'version': cert.get('version', 'Unknown'),
                        'serial_number': cert.get('serialNumber', 'Unknown'),
                        'not_before': cert['notBefore'],
                        'not_after': cert['notAfter'],
                        'expiry_days': (expiry_date - datetime.now()).days,
                        'signature_algorithm': cert.get('signatureAlgorithm', 'Unknown'),
                        'extensions': cert.get('extensions', [])
                    }
        except Exception as e:
            return {"error": str(e)}
    
    def extract_links(self, url: str, soup: BeautifulSoup) -> Set[str]:
        links = set()
        domain_name = urlparse(url).netloc
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            absolute_url = urljoin(url, href)
            
            if self.is_valid_url(absolute_url):
                if domain_name in absolute_url:
                    links.add(absolute_url)
                else:
                    self.external_urls.add(absolute_url)
        
        return links
    
    def extract_forms(self, url: str, soup: BeautifulSoup) -> List[Dict]:
        forms = []
        for form in soup.find_all("form"):
            form_details = {
                'action': urljoin(url, form.attrs.get('action', '')),
                'method': form.attrs.get('method', 'get').lower(),
                'inputs': []
            }
            
            for input_tag in form.find_all("input"):
                input_type = input_tag.attrs.get('type', 'text')
                input_name = input_tag.attrs.get('name', '')
                input_value = input_tag.attrs.get('value', '')
                form_details['inputs'].append({
                    'type': input_type,
                    'name': input_name,
                    'value': input_value
                })
            
            forms.append(form_details)
        return forms
    
    def extract_assets(self, url: str, soup: BeautifulSoup) -> None:
        for tag in soup.find_all(['img', 'script', 'link', 'source']):
            attr = 'src' if tag.name in ['img', 'script'] else 'href' if tag.name == 'link' else 'srcset'
            if tag.has_attr(attr):
                asset_url = urljoin(url, tag[attr])
                if self.is_valid_url(asset_url):
                    self.assets.append({
                        'url': asset_url,
                        'type': tag.name,
                        'tag': str(tag)
                    })
    
    def crawl_page(self, url: str, depth: int = 0) -> None:
        if depth > self.max_depth or len(self.visited_urls) >= self.max_pages or url in self.visited_urls:
            return
        
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            self.visited_urls.add(url)
            
            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.text, 'html.parser')
                
                self.forms.extend(self.extract_forms(url, soup))
                self.extract_assets(url, soup)
                
                page_title = soup.title.string if soup.title else 'No title'
                self.sitemap[url] = {
                    'title': page_title,
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'size': len(response.content),
                    'links': []
                }
                
                if depth < self.max_depth:
                    links = self.extract_links(url, soup)
                    for link in links:
                        if link not in self.visited_urls and len(self.visited_urls) < self.max_pages:
                            self.sitemap[url]['links'].append(link)
                            self.crawl_page(link, depth + 1)
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    def start_crawling(self) -> Dict:
        self.crawl_page(self.base_url)
        
        return {
            'base_url': self.base_url,
            'pages_crawled': len(self.visited_urls),
            'external_links': list(self.external_urls),
            'forms_found': self.forms,
            'assets': self.assets,
            'sitemap': self.sitemap,
            'domain_info': self.get_domain_info(),
            'ssl_info': self.get_ssl_cert_info() if self.base_url.startswith('https') else {}
        }
    
    def export_results(self, format_type: str = 'json') -> bool:
        try:
            results = self.start_crawling()
            
            if format_type == 'json':
                import json
                with open('crawl_results.json', 'w') as f:
                    json.dump(results, f, indent=4)
            
            elif format_type == 'html':
                from jinja2 import Environment, FileSystemLoader
                import os
                
                env = Environment(loader=FileSystemLoader('templates'))
                template = env.get_template('crawl_report.html')
                
                with open('crawl_report.html', 'w') as f:
                    f.write(template.render(
                        base_url=results['base_url'],
                        pages_crawled=results['pages_crawled'],
                        external_links=results['external_links'],
                        forms=results['forms_found'],
                        assets=results['assets'],
                        sitemap=results['sitemap'],
                        domain_info=results['domain_info'],
                        ssl_info=results.get('ssl_info', {})
                    ))
            
            return True
            
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False
