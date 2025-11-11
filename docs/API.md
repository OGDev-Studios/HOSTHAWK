# HostHawk API Documentation

## Core Scanner API

### NetworkScanner

The main scanner class for network operations.

```python
from scanner.core.scanner import NetworkScanner

scanner = NetworkScanner(timeout=2.0, threads=50)
```

#### Methods

##### `scan_network(network, interface=None)`
Scan a network for active hosts.

**Parameters:**
 `network` (str): CIDR notation (e.g., "192.168.1.0/24")
 `interface` (str, optional): Network interface to use

**Returns:** List of discovered hosts

**Example:**
```python
hosts = scanner.scan_network("192.168.1.0/24")
```

##### `scan_ports(target, ports, protocol="tcp", scan_type="connect")`
Scan ports on a target host.

**Parameters:**
 `target` (str): IP address or hostname
 `ports` (list): List of ports to scan
 `protocol` (str): "tcp" or "udp"
 `scan_type` (str): "connect" or "syn"

**Returns:** List of tuples (port, status)

**Example:**
```python
results = scanner.scan_ports("192.168.1.1", [22, 80, 443])
```

## Configuration API

### ScannerConfig

Configuration management for scanner settings.

```python
from scanner.config import ScannerConfig

config = ScannerConfig(
    timeout=2.0,
    threads=50,
    log_level="INFO"
)
```

#### Methods

##### `to_dict()`
Convert configuration to dictionary.

##### `from_dict(config_dict)`
Create configuration from dictionary.

##### `save_to_file(path)`
Save configuration to JSON file.

##### `from_file(path)`
Load configuration from JSON file.

## Validation API

### Validators

Input validation utilities.

```python
from scanner.utils.validators import (
    validate_ip,
    validate_cidr,
    validate_port,
    validate_port_range
)
```

#### Functions

##### `validate_ip(ip)`
Validate IP address format.

**Raises:** `InvalidTargetException` if invalid

##### `validate_cidr(cidr)`
Validate CIDR notation.

**Raises:** `InvalidTargetException` if invalid

##### `validate_port(port)`
Validate port number (165535).

**Raises:** `InvalidPortRangeException` if invalid

##### `validate_port_range(port_range)`
Parse and validate port range string.

**Returns:** List of port numbers

**Example:**
```python
ports = validate_port_range("80,443,80008010")
```

## Logging API

### Logger

Structured logging with multiple handlers.

```python
from scanner.utils.logger import setup_logging, get_logger

setup_logging(
    log_level="INFO",
    log_file="hosthawk.log",
    console_output=True
)

logger = get_logger(__name__)
logger.info("Scan started")
```

## Plugin APIs

### VulnerabilityScanner

```python
from scanner.plugins.vulnerability_scanner import VulnerabilityScanner

vuln_scanner = VulnerabilityScanner(timeout=5)
vulnerabilities = vuln_scanner.scan_port(target, port, protocol, banner)
```

### SNMPScanner

```python
from scanner.plugins.snmp_scanner import SNMPScanner

snmp = SNMPScanner(timeout=2, threads=10)
communities = snmp.scan_community_strings(target)
system_info = snmp.get_system_info(target, community)
```

### DNSEnumerator

```python
from scanner.plugins.dns_enum import DNSEnumerator

dns = DNSEnumerator(domain="example.com")
records = dns.get_all_records()
subdomains = dns.enumerate_subdomains()
```

### WebCrawler

```python
from scanner.plugins.web_crawler import WebCrawler

crawler = WebCrawler(base_url="https://example.com", max_depth=2)
results = crawler.start_crawling()
```

## Report Generation API

### ReportGenerator

```python
from scanner.reporting.report_generator import ReportGenerator

generator = ReportGenerator(output_dir='reports')
report_path = generator.generate_report(
    data=scan_results,
    format='html',
    filename='scan_report'
)
```

### Supported Formats

 JSON
 HTML
 CSV
 XML
 PDF

## Exception Hierarchy

```
HostHawkException
├── ScannerException
│   ├── NetworkScanException
│   ├── PortScanException
│   ├── VulnerabilityScanException
│   ├── TimeoutException
│   ├── PermissionException
│   ├── DNSEnumerationException
│   ├── SNMPScanException
│   └── WebCrawlerException
├── ConfigurationException
├── ValidationException
│   ├── InvalidTargetException
│   └── InvalidPortRangeException
└── ReportGenerationException
```

## Web API Endpoints

### Start Scan

```http
POST /api/scan
ContentType: application/json

{
  "type": "port_scan",
  "target": "192.168.1.1",
  "ports": "11024"
}
```

### Get Scan Status

```http
GET /api/scan/{scan_id}
```

### Get Scan Report

```http
GET /api/scan/{scan_id}/report?format=html
```

## Environment Variables

```bash
HOSTHAWK_TIMEOUT=2.0
HOSTHAWK_THREADS=50
HOSTHAWK_LOG_LEVEL=INFO
HOSTHAWK_LOG_FILE=hosthawk.log
HOSTHAWK_OUTPUT_DIR=output
HOSTHAWK_REPORTS_DIR=reports
```

## Examples

### Basic Port Scan

```python
from scanner.core.scanner import NetworkScanner

scanner = NetworkScanner()
results = scanner.scan_ports("192.168.1.1", [22, 80, 443])

for port, status in results:
    print(f"Port {port}: {status}")
```

### Network Discovery with Validation

```python
from scanner.core.scanner import NetworkScanner
from scanner.utils.validators import validate_cidr

network = "192.168.1.0/24"
validate_cidr(network)

scanner = NetworkScanner()
hosts = scanner.scan_network(network)
```

### Custom Configuration

```python
from scanner.config import ScannerConfig
from scanner.core.scanner import NetworkScanner

config = ScannerConfig(
    timeout=5.0,
    threads=100,
    log_level="DEBUG"
)

scanner = NetworkScanner(
    timeout=config.timeout,
    threads=config.threads
)
```
