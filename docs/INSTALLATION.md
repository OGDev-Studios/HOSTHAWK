# HostHawk Installation Guide

## Table of Contents
 [System Requirements](#systemrequirements)
 [Installation Methods](#installationmethods)
 [PlatformSpecific Instructions](#platformspecificinstructions)
 [Verification](#verification)
 [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

```
┌─────────────────────────────────────────┐
│  Component    │  Requirement            │
├───────────────┼─────────────────────────┤
│  OS           │  Linux, macOS, Windows  │
│  Python       │  3.8 or higher          │
│  RAM          │  512 MB minimum         │
│  Disk Space   │  100 MB                 │
│  Network      │  Active connection      │
└─────────────────────────────────────────┘
```

### Recommended Requirements

```
┌─────────────────────────────────────────┐
│  Component    │  Recommendation         │
├───────────────┼─────────────────────────┤
│  OS           │  Linux (Ubuntu/Debian)  │
│  Python       │  3.9+                   │
│  RAM          │  2 GB                   │
│  Disk Space   │  500 MB                 │
│  CPU          │  Multicore             │
└─────────────────────────────────────────┘
```

### Required Privileges

```
Standard User:
├── TCP Connect Scans
├── Service Detection
├── Banner Grabbing
└── Report Generation

Root/Administrator:
├── SYN Scans
├── ICMP Ping
├── ARP Scans
└── OS Fingerprinting
```

## Installation Methods

### Method 1: From Source (Recommended)

**Step 1: Clone Repository**

```bash
git clone https://github.com/yourusername/hosthawk.git
cd hosthawk
```

**Step 2: Install Dependencies**

```bash
pip install e .
```

**Installation Flow:**
```
┌──────────────┐
│ Clone Repo   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Install Deps │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Verify       │
└──────────────┘
```

### Method 2: Using pip (Future)

```bash
pip install hosthawk
```

### Method 3: Docker

**Step 1: Pull Image**

```bash
docker pull hosthawk/hosthawk:latest
```

**Step 2: Run Container**

```bash
docker run it rm \
  network host \
  capadd=NET_ADMIN \
  hosthawk/hosthawk:latest
```

**Docker Architecture:**
```
┌─────────────────────────────────────┐
│  Host System                        │
│  ┌───────────────────────────────┐  │
│  │  Docker Container             │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  HostHawk Application   │  │  │
│  │  └─────────────────────────┘  │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Python Runtime         │  │  │
│  │  └─────────────────────────┘  │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  Alpine Linux           │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Method 4: Docker Compose

**Step 1: Create dockercompose.yml**

```yaml
version: '3.8'

services:
  hosthawk:
    build: .
    ports:
       "5000:5000"
    volumes:
       ./reports:/app/reports
       ./logs:/app/logs
    environment:
       HOSTHAWK_THREADS=50
       HOSTHAWK_TIMEOUT=2.0
    cap_add:
       NET_ADMIN
    network_mode: host
```

**Step 2: Start Services**

```bash
dockercompose up d
```

## PlatformSpecific Instructions

### Linux (Ubuntu/Debian)

**Step 1: Update System**

```bash
sudo apt update
sudo apt upgrade y
```

**Step 2: Install Python and Dependencies**

```bash
sudo apt install y python3 python3pip python3venv
sudo apt install y libpcapdev nmap
```

**Step 3: Install HostHawk**

```bash
git clone https://github.com/yourusername/hosthawk.git
cd hosthawk
python3 m venv venv
source venv/bin/activate
pip install e .
```

**Installation Timeline:**
```
[0:00] Update system packages
[0:30] Install Python and tools
[1:00] Clone repository
[1:15] Create virtual environment
[1:30] Install dependencies
[2:00] ✓ Installation complete
```

### Linux (RHEL/CentOS/Fedora)

**Step 1: Install Dependencies**

```bash
sudo dnf install y python3 python3pip
sudo dnf install y libpcapdevel nmap
```

**Step 2: Install HostHawk**

```bash
git clone https://github.com/yourusername/hosthawk.git
cd hosthawk
python3 m venv venv
source venv/bin/activate
pip install e .
```

### macOS

**Step 1: Install Homebrew (if not installed)**

```bash
/bin/bash c "$(curl fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Step 2: Install Dependencies**

```bash
brew install python@3.9
brew install libpcap nmap
```

**Step 3: Install HostHawk**

```bash
git clone https://github.com/yourusername/hosthawk.git
cd hosthawk
python3 m venv venv
source venv/bin/activate
pip install e .
```

**macOS Installation Flow:**
```
┌──────────────────┐
│ Install Homebrew │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Install Python   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Install libpcap  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Clone & Install  │
└──────────────────┘
```

### Windows

**Step 1: Install Python**

1. Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify installation:

```powershell
python version
```

**Step 2: Install Npcap**

1. Download Npcap from [npcap.com](https://npcap.com/)
2. Run installer with "WinPcap APIcompatible Mode"

**Step 3: Install HostHawk**

```powershell
git clone https://github.com/yourusername/hosthawk.git
cd hosthawk
python m venv venv
venv\Scripts\activate
pip install e .
```

**Windows Installation Checklist:**
```
☐ Python 3.9+ installed
☐ Python added to PATH
☐ Npcap installed
☐ Git installed
☐ Repository cloned
☐ Virtual environment created
☐ Dependencies installed
☐ HostHawk verified
```

## Virtual Environment Setup

### Why Use Virtual Environments?

```
System Python                Virtual Environment
┌─────────────┐             ┌─────────────────┐
│  Python 3.9 │             │  Python 3.9     │
│             │             │                 │
│  Package A  │             │  HostHawk       │
│  Package B  │             │  Dependencies   │
│  Package C  │             │  (Isolated)     │
└─────────────┘             └─────────────────┘
     Global                      Projectspecific
```

### Creating Virtual Environment

**Linux/macOS:**

```bash
python3 m venv venv
source venv/bin/activate
```

**Windows:**

```powershell
python m venv venv
venv\Scripts\activate
```

**Verification:**

```bash
which python
python version
```

**Expected Output:**
```
/path/to/hosthawk/venv/bin/python
Python 3.9.7
```

## Verification

### Basic Verification

**Step 1: Check Installation**

```bash
hosthawk version
```

**Expected Output:**
```
HostHawk v1.0.0
Python 3.9.7
```

**Step 2: Check Help**

```bash
hosthawk help
```

**Expected Output:**
```
usage: hosthawk [h] [network NETWORK] [host HOST] 
                [p PORTS] [scantype {connect,syn}]
                [format {json,csv,xml,html}] [o OUTPUT]
                [threads THREADS] [timeout TIMEOUT]
                [verbose]

HostHawk  Enterprise Network Scanner

optional arguments:
  h, help            show this help message
  network NETWORK     Network to scan (CIDR notation)
  host HOST           Single host to scan
  ...
```

### Functional Verification

**Test 1: Local Scan**

```bash
hosthawk host 127.0.0.1 p 22,80,443
```

**Test 2: Network Discovery**

```bash
hosthawk network 192.168.1.0/24
```

**Test 3: Output Generation**

```bash
hosthawk host 127.0.0.1 p 80 format json o test.json
cat test.json
```

**Verification Checklist:**
```
✓ Commandline tool accessible
✓ Help documentation displays
✓ Local host scan works
✓ Output file generation works
✓ No error messages
```

### Advanced Verification

**Test SYN Scan (requires root):**

```bash
sudo hosthawk host 127.0.0.1 p 80 scantype syn
```

**Test Web Interface:**

```bash
hosthawk web
```

Then open browser to: http://localhost:5000

**Web Interface Verification:**
```
┌─────────────────────────────────────┐
│  HostHawk Web Interface             │
├─────────────────────────────────────┤
│  ✓ Page loads successfully          │
│  ✓ Scan form is visible             │
│  ✓ Can submit scan                  │
│  ✓ Results display correctly        │
└─────────────────────────────────────┘
```

## Troubleshooting

### Common Issues

#### Issue 1: Command Not Found

**Error:**
```bash
hosthawk: command not found
```

**Solution:**

```bash
pip install e .

export PATH="$HOME/.local/bin:$PATH"

source venv/bin/activate
```

#### Issue 2: Permission Denied

**Error:**
```
[!] Error: Permission denied
[*] SYN scans require root privileges
```

**Solution:**

```bash
sudo hosthawk host 192.168.1.1 scantype syn
```

**Permission Hierarchy:**
```
┌─────────────────────────────────────┐
│  Scan Type    │  Required Privilege │
├───────────────┼─────────────────────┤
│  TCP Connect  │  User               │
│  Service Det  │  User               │
│  SYN Scan     │  Root               │
│  ICMP Ping    │  Root               │
│  ARP Scan     │  Root               │
└─────────────────────────────────────┘
```

#### Issue 3: Module Import Error

**Error:**
```python
ModuleNotFoundError: No module named 'scapy'
```

**Solution:**

```bash
pip install r requirements.txt

pip install scapy
```

#### Issue 4: libpcap Not Found

**Error:**
```
OSError: libpcap.so.1: cannot open shared object file
```

**Solution:**

**Linux:**
```bash
sudo apt install libpcapdev
```

**macOS:**
```bash
brew install libpcap
```

**Windows:**
```
Install Npcap from https://npcap.com/
```

#### Issue 5: Docker Network Issues

**Error:**
```
Error: Cannot connect to network
```

**Solution:**

```bash
docker run network host capadd=NET_ADMIN hosthawk
```

**Docker Network Modes:**
```
┌─────────────────────────────────────────┐
│  Mode         │  Use Case               │
├───────────────┼─────────────────────────┤
│  bridge       │  Isolated network       │
│  host         │  Direct host access     │
│  none         │  No networking          │
└─────────────────────────────────────────┘
```

### Dependency Issues

**Check Python Version:**

```bash
python version
```

**Required:** Python 3.8+

**Check pip Version:**

```bash
pip version
```

**Upgrade pip:**

```bash
pip install upgrade pip
```

**Install Missing Dependencies:**

```bash
pip install r requirements.txt
```

**Dependency Tree:**
```
HostHawk
├── scapy (packet manipulation)
├── flask (web interface)
├── requests (HTTP client)
├── jinja2 (templating)
├── click (CLI framework)
└── pythondotenv (config)
```

### Performance Issues

**Issue: Slow Scanning**

**Diagnosis:**

```bash
hosthawk host 192.168.1.1 p 11000 verbose
```

**Solutions:**

1. **Increase Threads:**
```bash
hosthawk host 192.168.1.1 p 11000 threads 100
```

2. **Decrease Timeout:**
```bash
hosthawk host 192.168.1.1 p 11000 timeout 1.0
```

3. **Use SYN Scan:**
```bash
sudo hosthawk host 192.168.1.1 p 11000 scantype syn
```

**Performance Comparison:**
```
Configuration          │ Time   │ Accuracy
───────────────────────┼────────┼──────────
Default (50 threads)   │  45s   │   98%
100 threads            │  25s   │   98%
200 threads            │  18s   │   95%
SYN scan (root)        │  12s   │   99%
```

## PostInstallation Configuration

### Environment Variables

Create `.env` file:

```bash
HOSTHAWK_THREADS=50
HOSTHAWK_TIMEOUT=2.0
HOSTHAWK_LOG_LEVEL=INFO
HOSTHAWK_OUTPUT_DIR=./output
HOSTHAWK_REPORTS_DIR=./reports
```

### Configuration File

Create `config.json`:

```json
{
  "scanner": {
    "threads": 50,
    "timeout": 2.0,
    "retry_attempts": 3
  },
  "output": {
    "default_format": "json",
    "output_dir": "./output"
  },
  "logging": {
    "level": "INFO",
    "file": "hosthawk.log"
  }
}
```

### Logging Configuration

**Enable Debug Logging:**

```bash
hosthawk host 192.168.1.1 loglevel DEBUG
```

**Log Levels:**
```
DEBUG    → Detailed diagnostic info
INFO     → General informational messages
WARNING  → Warning messages
ERROR    → Error messages
CRITICAL → Critical errors
```

## Upgrading

### Upgrade from Source

```bash
cd hosthawk
git pull origin main
pip install e . upgrade
```

### Upgrade via pip (Future)

```bash
pip install upgrade hosthawk
```

**Upgrade Flow:**
```
┌──────────────┐
│ Backup Data  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Pull Updates │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Reinstall    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Verify       │
└──────────────┘
```

## Uninstallation

### Remove HostHawk

```bash
pip uninstall hosthawk
```

### Remove Virtual Environment

```bash
deactivate
rm rf venv
```

### Remove Repository

```bash
cd ..
rm rf hosthawk
```

### Clean Docker

```bash
docker rmi hosthawk/hosthawk:latest
docker system prune a
```

## Getting Help

### Documentation

 **Installation Guide:** This document
 **Usage Examples:** docs/USAGE_EXAMPLES.md
 **API Reference:** docs/API.md
 **Contributing:** docs/CONTRIBUTING.md

### Support Channels

```
┌─────────────────────────────────────────┐
│  Issue Type    │  Contact               │
├────────────────┼────────────────────────┤
│  Bug Report    │  GitHub Issues         │
│  Feature Req   │  GitHub Issues         │
│  Security      │  security@hosthawk.io  │
│  General       │  team@hosthawk.io      │
└─────────────────────────────────────────┘
```

### Diagnostic Information

When reporting issues, include:

```bash
hosthawk version
python version
pip list | grep E "(scapy|flask)"
uname a
```

**Example Output:**
```
HostHawk v1.0.0
Python 3.9.7
scapy==2.4.5
flask==2.0.2
Linux hostname 5.10.08amd64 x86_64 GNU/Linux
```
