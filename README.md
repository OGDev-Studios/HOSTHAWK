# 🦅 HostHawk Enterprise Network Scanner

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

HostHawk is an enterprisegrade, multithreaded network scanner designed for security professionals and network administrators. It provides comprehensive network discovery, port scanning, service detection, OS fingerprinting, and vulnerability assessment capabilities.

```
┌─────────────────────────────────────────────────────────────┐
│                    HostHawk Scanner                         │
├─────────────────────────────────────────────────────────────┤
│  Network Discovery  →  Port Scanning  →  Service Detection │
│         ↓                    ↓                    ↓         │
│  Vulnerability Scan  →  OS Fingerprint  →  Report Gen      │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### Core Scanning Capabilities
 **🔍 Host Discovery**: ICMP ping and ARP scanning for local network discovery
 **🔌 Port Scanning**: TCP (SYN, Connect) and UDP scanning with configurable speed
 **🔧 Service Detection**: Advanced banner grabbing and service identification
 **💻 OS Fingerprinting**: TTLbased and TCP/IP stack fingerprinting
 **🛡️ Vulnerability Scanning**: Builtin vulnerability detection for common services

### Advanced Features
 **📡 SNMP Enumeration**: Comprehensive SNMP scanning and information gathering
 **🌐 DNS Enumeration**: Subdomain discovery and DNS record enumeration
 **🕷️ Web Crawling**: Website structure analysis and asset discovery
 **⚡ Multithreaded**: Highperformance scanning with configurable concurrency

### Output & Interface
 **📊 Multiple Output Formats**: JSON, CSV, XML, HTML, and PDF reports
 **🎨 Web Interface**: Modern Flaskbased web UI with realtime updates
 **📝 Comprehensive Logging**: Structured logging with multiple output handlers

### Enterprise Ready
 **🔐 Security**: Input validation, rate limiting, and comprehensive logging
 **🧩 Modular Design**: Pluginbased architecture for easy extension
 **⚙️ Configuration Management**: Environment variables and JSON config support
 **🐳 Docker Support**: Containerized deployment with Docker and Docker Compose

## 📋 Requirements

```
┌─────────────────────────────────────────┐
│  Component    │  Requirement            │
├───────────────┼─────────────────────────┤
│  Python       │  3.8 or higher          │
│  OS           │  Linux, macOS, Windows  │
│  RAM          │  512 MB minimum         │
│  Privileges   │  User (root for SYN)    │
└─────────────────────────────────────────┘
```

**Privilege Requirements:**
 Standard User: TCP Connect, Service Detection, Banner Grabbing
 Root/Administrator: SYN Scans, ICMP Ping, ARP Scans, OS Fingerprinting

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/hosthawk.git
cd hosthawk
pip install e .
```

### Basic Usage

```bash
hosthawk network 192.168.1.0/24
hosthawk host 192.168.1.1 p 22,80,443
hosthawk host example.com p 11024 format json o results.json
```

### Docker Quick Start

```bash
dockercompose up d
```

Access web interface at: http://localhost:5000

📖 **For detailed installation instructions, see [docs/INSTALLATION.md](docs/INSTALLATION.md)**

## 💡 Usage Examples

### Network Discovery

```bash
hosthawk network 192.168.1.0/24
```

**Output:**
```
[*] Starting network scan on 192.168.1.0/24
[+] Found 12 active hosts
    192.168.1.1    (Gateway)
    192.168.1.10   (Active)
    192.168.1.15   (Active)
[*] Scan completed in 3.2 seconds
```

### Port Scanning

```bash
hosthawk host 192.168.1.100 p 22,80,443,3306
```

**Output:**
```
[+] Port 22/tcp    open    ssh         OpenSSH 8.2
[+] Port 80/tcp    open    http        nginx 1.18.0
[+] Port 443/tcp   open    https       nginx 1.18.0
[] Port 3306/tcp  closed
```

### Advanced Scanning

```bash
sudo hosthawk host 192.168.1.100 \
  p 11024 \
  scantype syn \
  servicedetection \
  vulnscan \
  format html \
  o report.html
```

📖 **For more examples and realworld scenarios, see [docs/USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md)**

## 📊 Output Formats

HostHawk supports multiple output formats for different use cases:

| Format | Use Case | Command |
||||
| **JSON** | API integration, automation | `format json` |
| **CSV** | Spreadsheet analysis | `format csv` |
| **XML** | Enterprise systems | `format xml` |
| **HTML** | Humanreadable reports | `format html` |
| **PDF** | Professional documentation | `format pdf` |

**Example:**
```bash
hosthawk host 192.168.1.1 p 11024 format html o report.html
```

## ⚡ Performance Tuning

```
Threads │ Scan Time │ CPU Usage │ Recommended For
────────┼───────────┼───────────┼─────────────────
   10   │   180s    │    15%    │ Slow networks
   50   │    45s    │    45%    │ Default (balanced)
  100   │    25s    │    75%    │ Fast networks
  200   │    18s    │    95%    │ Highperformance
```

**Adjust threads:**
```bash
hosthawk network 192.168.1.0/24 threads 100
```

**Adjust timeout:**
```bash
hosthawk host 192.168.1.1 timeout 1.5
```

## 🔒 Security Considerations

```
⚠️  IMPORTANT: Always obtain proper authorization before scanning
```

**Legal & Ethical:**
 ✅ Obtain written permission before scanning
 ✅ Only scan networks you own or have authorization for
 ❌ Unauthorized scanning may be illegal in your jurisdiction
 ❌ Respect network policies and IDS/IPS systems

**Best Practices:**
 Use rate limiting to avoid network disruption
 Run with appropriate privileges (root for raw sockets)
 Monitor scan impact on target systems
 Review our [Security Policy](docs/SECURITY.md) for detailed guidelines

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/hosthawk.git
cd hosthawk
make installdev
```

### Code Quality

```bash
make format
make lint
```

### Project Structure

```
hosthawk/
├── scanner/           # Core scanner package
│   ├── core/         # Scanning engine
│   ├── plugins/      # Extensible plugins
│   ├── output/       # Output formatters
│   └── utils/        # Utilities
├── web/              # Web interface
├── docs/             # Documentation
└── tests/            # Test suite
```

## 📚 Documentation

### Core Documentation
 **[Installation Guide](docs/INSTALLATION.md)**  Detailed installation instructions for all platforms
 **[Usage Examples](docs/USAGE_EXAMPLES.md)**  Comprehensive examples and realworld scenarios
 **[Architecture](docs/ARCHITECTURE.md)**  System design and technical architecture
 **[API Reference](docs/API.md)**  Complete API documentation

### Additional Resources
 **[Quick Start](docs/QUICK_START.md)**  Get started in 5 minutes
 **[Contributing Guidelines](docs/CONTRIBUTING.md)**  How to contribute to HostHawk
 **[Security Policy](docs/SECURITY.md)**  Security guidelines and reporting
 **[Changelog](docs/CHANGELOG.md)**  Version history and updates

## 🤝 Contributing

We welcome contributions! Here's how you can help:

```
┌─────────────────────────────────────────┐
│  Contribution Type  │  How to Help      │
├─────────────────────┼───────────────────┤
│  🐛 Bug Reports     │  GitHub Issues    │
│  ✨ Features        │  Pull Requests    │
│  📖 Documentation   │  Edit docs/       │
│  🧪 Testing         │  Add test cases   │
│  💡 Ideas           │  Discussions      │
└─────────────────────────────────────────┘
```

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout b feature/amazingfeature`)
3. Make your changes
4. Run tests and linters (`make lint`)
5. Commit your changes (`git commit m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazingfeature`)
7. Open a Pull Request

📖 **See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines**

## 📝 Changelog

See [docs/CHANGELOG.md](docs/CHANGELOG.md) for version history and updates.

## 🐛 Bug Reports & Support

**Found a bug?** Please report it via [GitHub Issues](https://github.com/yourusername/hosthawk/issues)

**Need help?** Check our documentation or contact us:
 📧 General: team@hosthawk.io
 🔒 Security: security@hosthawk.io
 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/hosthawk/discussions)

## 🌟 Features Roadmap

### Current (v1.0)
 ✅ Core scanning functionality
 ✅ Multiple output formats
 ✅ Web interface
 ✅ Docker support

### Planned (v2.0)
 🔄 Database integration
 🔄 Scan history and comparison
 🔄 Advanced reporting
 🔄 API authentication

### Future (v3.0)
 📅 Distributed scanning
 📅 Machine learning integration
 📅 Realtime alerting
 📅 Cloud deployment support

## License

This project is licensed under the MIT License  see the [LICENSE](LICENSE) file for details.

## Acknowledgments

 Built with [Scapy](https://scapy.net/) for packet manipulation
 Uses [Flask](https://flask.palletsprojects.com/) for the web interface
 Inspired by tools like Nmap, Masscan, and Metasploit

## Disclaimer

This tool is provided for educational and authorized security testing purposes only. Users are responsible for complying with all applicable laws and regulations. The authors assume no liability for misuse or damage caused by this tool.



**Made with ❤️ by Joshua Ryan | TheOGDev**
