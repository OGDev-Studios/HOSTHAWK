# HostHawk Usage Examples

## Table of Contents
 [Basic Scanning](#basicscanning)
 [Advanced Scanning](#advancedscanning)
 [Output Formats](#outputformats)
 [Web Interface](#webinterface)
 [Docker Usage](#dockerusage)
 [RealWorld Scenarios](#realworldscenarios)

## Basic Scanning

### Network Discovery

Discover all active hosts on a network:

```bash
hosthawk network 192.168.1.0/24
```

**Output Example:**
```
[*] Starting network scan on 192.168.1.0/24
[+] Found 12 active hosts
    192.168.1.1    (Gateway)
    192.168.1.10   (Active)
    192.168.1.15   (Active)
    192.168.1.20   (Active)
    ...
[*] Scan completed in 3.2 seconds
```

**Visual Representation:**
```
Network: 192.168.1.0/24
┌─────────────────────────────────────┐
│  Gateway (192.168.1.1)              │
│         │                           │
│    ┌────┴────┐                      │
│    │ Switch  │                      │
│    └─┬──┬──┬─┘                      │
│      │  │  │                        │
│   ┌──┘  │  └──┐                     │
│   │     │     │                     │
│  Host  Host  Host                   │
│  .10   .15   .20                    │
└─────────────────────────────────────┘
```

### Single Host Port Scan

Scan common ports on a single host:

```bash
hosthawk host 192.168.1.100 p 22,80,443,3306,8080
```

**Output Example:**
```
[*] Scanning 192.168.1.100
[+] Port 22/tcp    open    ssh         OpenSSH 8.2
[+] Port 80/tcp    open    http        nginx 1.18.0
[+] Port 443/tcp   open    https       nginx 1.18.0
[] Port 3306/tcp  closed
[+] Port 8080/tcp  open    httpproxy  
[*] Scan completed: 3 open, 1 closed, 1 filtered
```

### Port Range Scanning

Scan a range of ports:

```bash
hosthawk host 192.168.1.100 p 11024
```

**Progress Indicator:**
```
[*] Scanning ports 11024 on 192.168.1.100
Progress: [████████████████████░░░░] 80% (820/1024)
Open ports: 5
Estimated time remaining: 12s
```

## Advanced Scanning

### SYN Stealth Scan

Perform a stealthy SYN scan (requires root):

```bash
sudo hosthawk host 192.168.1.100 p 165535 scantype syn threads 100
```

**Scan Flow Diagram:**
```
HostHawk                    Target (192.168.1.100)
   │                               │
   ├──────── SYN ─────────────────>│
   │                               │
   │<─────── SYNACK ──────────────┤ (Port Open)
   │                               │
   ├──────── RST ─────────────────>│
   │                               │
   
   ├──────── SYN ─────────────────>│
   │                               │
   │<─────── RST ──────────────────┤ (Port Closed)
   │                               │
```

### Service Detection

Scan with service version detection:

```bash
hosthawk host 192.168.1.100 p 80,443,22 servicedetection
```

**Output Example:**
```
PORT     STATE  SERVICE   VERSION
22/tcp   open   ssh       OpenSSH 8.2p1 Ubuntu 4ubuntu0.5
80/tcp   open   http      nginx 1.18.0 (Ubuntu)
443/tcp  open   ssl/http  nginx 1.18.0 (Ubuntu)

Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### OS Fingerprinting

Detect operating system:

```bash
sudo hosthawk host 192.168.1.100 osdetection
```

**Output Example:**
```
[*] OS Detection Results for 192.168.1.100
    
    OS: Linux 4.15  5.6
    Confidence: 95%
    
    Details:
     TTL: 64 (Linux/Unix)
     Window Size: 29200
     TCP Options: MSS, SACK, Timestamps, NOP, WScale
    
    Likely Distribution: Ubuntu 20.04 LTS
```

### Vulnerability Scanning

Scan for common vulnerabilities:

```bash
hosthawk host 192.168.1.100 p 11024 vulnscan
```

**Output Example:**
```
[*] Vulnerability Scan Results

[!] CRITICAL: Port 21  FTP Anonymous Login Enabled
    CVE: N/A
    Risk: High
    Description: Anonymous FTP access is enabled
    Recommendation: Disable anonymous access

[!] HIGH: Port 22  SSH Weak Encryption
    CVE: CVE202014145
    Risk: Medium
    Description: Weak encryption algorithms detected
    Recommendation: Update SSH configuration

[+] Port 80  HTTP Server Headers Exposed
    Risk: Low
    Description: Server version disclosed in headers
    Recommendation: Configure server to hide version
```

## Output Formats

### JSON Output

```bash
hosthawk host 192.168.1.100 p 80,443 format json o scan_results.json
```

**Output Structure:**
```json
{
  "scan_info": {
    "target": "192.168.1.100",
    "start_time": "20241111T17:30:00Z",
    "end_time": "20241111T17:30:15Z",
    "duration": 15.2
  },
  "results": [
    {
      "port": 80,
      "protocol": "tcp",
      "state": "open",
      "service": "http",
      "version": "nginx 1.18.0",
      "banner": "nginx/1.18.0 (Ubuntu)"
    },
    {
      "port": 443,
      "protocol": "tcp",
      "state": "open",
      "service": "https",
      "version": "nginx 1.18.0",
      "ssl": {
        "enabled": true,
        "version": "TLSv1.3"
      }
    }
  ]
}
```

### CSV Output

```bash
hosthawk host 192.168.1.100 p 11024 format csv o scan_results.csv
```

**Output Example:**
```csv
host,port,protocol,state,service,version,banner
192.168.1.100,22,tcp,open,ssh,OpenSSH 8.2,SSH2.0OpenSSH_8.2p1
192.168.1.100,80,tcp,open,http,nginx 1.18.0,nginx/1.18.0
192.168.1.100,443,tcp,open,https,nginx 1.18.0,nginx/1.18.0
```

### HTML Report

```bash
hosthawk host 192.168.1.100 p 11024 format html o report.html
```

**Report Preview:**
```
┌────────────────────────────────────────────┐
│  HostHawk Scan Report                      │
│  Target: 192.168.1.100                     │
│  Date: 20241111 17:30:00                 │
├────────────────────────────────────────────┤
│  Summary                                   │
│  • Total Ports Scanned: 1024               │
│  • Open Ports: 5                           │
│  • Closed Ports: 1019                      │
│  • Scan Duration: 45.3s                    │
├────────────────────────────────────────────┤
│  Open Ports                                │
│  ┌──────┬─────────┬──────────────┐         │
│  │ Port │ Service │ Version      │         │
│  ├──────┼─────────┼──────────────┤         │
│  │  22  │ SSH     │ OpenSSH 8.2  │         │
│  │  80  │ HTTP    │ nginx 1.18.0 │         │
│  │  443 │ HTTPS   │ nginx 1.18.0 │         │
│  └──────┴─────────┴──────────────┘         │
└────────────────────────────────────────────┘
```

## Web Interface

### Starting the Web Interface

```bash
hosthawk web
```

Or using the Makefile:

```bash
make run
```

**Access:** http://localhost:5000

### Web Interface Features

```
┌─────────────────────────────────────────────────────────┐
│  HostHawk Web Interface                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Scan Configuration]                                   │
│  ┌─────────────────────────────────────────────┐       │
│  │ Target: [192.168.1.0/24        ]            │       │
│  │ Ports:  [11024                ]            │       │
│  │ Type:   [SYN Scan ▼]                        │       │
│  │         [Start Scan]                        │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  [Live Results]                                         │
│  ┌─────────────────────────────────────────────┐       │
│  │ 192.168.1.1    ✓ Active                     │       │
│  │   Port 80  → Open (nginx)                   │       │
│  │   Port 443 → Open (nginx)                   │       │
│  │                                              │       │
│  │ 192.168.1.10   ✓ Active                     │       │
│  │   Port 22  → Open (ssh)                     │       │
│  │   Port 80  → Open (apache)                  │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  [Export] [JSON] [CSV] [HTML] [PDF]                    │
└─────────────────────────────────────────────────────────┘
```

### API Endpoints

**Start a Scan:**
```bash
curl X POST http://localhost:5000/api/scan \
  H "ContentType: application/json" \
  d '{
    "type": "port_scan",
    "target": "192.168.1.100",
    "ports": "11024"
  }'
```

**Response:**
```json
{
  "scan_id": "abc123",
  "status": "started",
  "message": "Scan initiated successfully"
}
```

**Check Scan Status:**
```bash
curl http://localhost:5000/api/scan/abc123
```

**Response:**
```json
{
  "scan_id": "abc123",
  "status": "running",
  "progress": 45,
  "results": {
    "scanned": 460,
    "total": 1024,
    "open_ports": 3
  }
}
```

## Docker Usage

### Quick Start

```bash
dockercompose up d
```

**Container Architecture:**
```
┌─────────────────────────────────────────┐
│  Docker Host                            │
│  ┌───────────────────────────────────┐  │
│  │  HostHawk Container               │  │
│  │  ┌─────────────┐  ┌─────────────┐ │  │
│  │  │   Scanner   │  │  Web UI     │ │  │
│  │  │   Engine    │  │  (Flask)    │ │  │
│  │  └──────┬──────┘  └──────┬──────┘ │  │
│  │         │                │        │  │
│  │         └────────┬───────┘        │  │
│  │                  │                │  │
│  │         ┌────────▼────────┐       │  │
│  │         │   Reports Dir   │       │  │
│  │         └─────────────────┘       │  │
│  └───────────────────────────────────┘  │
│           │                             │
│           │ Port 5000                   │
└───────────┼─────────────────────────────┘
            │
    ┌───────▼────────┐
    │  Your Browser  │
    │  localhost:5000│
    └────────────────┘
```

### Custom Docker Scan

```bash
docker run it rm \
  network host \
  capadd=NET_ADMIN \
  hosthawk:latest \
  hosthawk network 192.168.1.0/24 p 11024
```

### Docker Compose Configuration

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

## RealWorld Scenarios

### Scenario 1: Internal Network Audit

**Objective:** Audit internal network for security compliance

```bash
hosthawk network 10.0.0.0/24 \
  p 165535 \
  scantype syn \
  servicedetection \
  vulnscan \
  format html \
  o audit_report.html \
  threads 200
```

**Timeline:**
```
00:00  Scan started
00:15  Network discovery complete (45 hosts found)
01:30  Port scanning 50% complete
03:00  Port scanning complete
03:15  Service detection complete
04:00  Vulnerability assessment complete
04:05  Report generated
```

### Scenario 2: Web Server Security Check

**Objective:** Check web server security posture

```bash
hosthawk host web.example.com \
  p 80,443,8080,8443 \
  servicedetection \
  vulnscan \
  sslcheck \
  format json \
  o webserver_audit.json
```

**Findings Example:**
```
[*] Web Server Security Assessment

Target: web.example.com (203.0.113.10)

[+] Open Ports:
    80/tcp    HTTP (nginx 1.18.0)
    443/tcp   HTTPS (nginx 1.18.0)

[+] SSL/TLS Configuration:
    Protocol: TLSv1.3
    Cipher: TLS_AES_256_GCM_SHA384
    Certificate: Valid (expires 20250615)
    Grade: A

[!] Security Issues:
     HTTP Strict Transport Security (HSTS) not enabled
     XFrameOptions header missing
     ContentSecurityPolicy not configured

[*] Recommendations:
    1. Enable HSTS with maxage=31536000
    2. Add XFrameOptions: DENY
    3. Implement ContentSecurityPolicy
```

### Scenario 3: Continuous Monitoring

**Objective:** Monitor network changes over time

```bash
while true; do
  hosthawk network 192.168.1.0/24 \
    format json \
    o "scan_$(date +%Y%m%d_%H%M%S).json"
  sleep 3600
done
```

**Change Detection:**
```
[*] Network Change Detection

Scan 1: 20241111 10:00:00
Scan 2: 20241111 11:00:00

[+] New Hosts Detected:
    192.168.1.150 (appeared at 10:45:00)

[!] Port Changes:
    192.168.1.100
     Port 3306 opened (MySQL)
    
[!] Service Changes:
    192.168.1.50
     nginx 1.18.0 → nginx 1.20.0 (upgraded)
```

### Scenario 4: MultiTarget Scanning

**Objective:** Scan multiple targets from a file

Create targets file:
```bash
cat > targets.txt << EOF
192.168.1.100
192.168.1.101
192.168.1.102
web.example.com
api.example.com
EOF
```

Run scan:
```bash
hosthawk targetsfile targets.txt \
  p 80,443,22,3306 \
  format csv \
  o multi_target_scan.csv
```

**Progress Visualization:**
```
[*] MultiTarget Scan Progress

Target 1/5: 192.168.1.100     [████████████████████] 100% ✓
Target 2/5: 192.168.1.101     [████████████████████] 100% ✓
Target 3/5: 192.168.1.102     [████████████░░░░░░░░]  65%
Target 4/5: web.example.com   [░░░░░░░░░░░░░░░░░░░░]   0%
Target 5/5: api.example.com   [░░░░░░░░░░░░░░░░░░░░]   0%

Overall Progress: 53% (2.5/5 targets)
Estimated completion: 5m 30s
```

## Performance Optimization

### Thread Tuning

```bash
hosthawk network 192.168.1.0/24 p 11024 threads 200
```

**Performance Comparison:**
```
Threads │ Scan Time │ CPU Usage │ Memory
────────┼───────────┼───────────┼────────
   10   │   180s    │    15%    │  50MB
   50   │    45s    │    45%    │  80MB
  100   │    25s    │    75%    │ 120MB
  200   │    18s    │    95%    │ 180MB
  500   │    15s    │   100%    │ 300MB
```

### Timeout Adjustment

```bash
hosthawk host 192.168.1.100 p 165535 timeout 0.5
```

**Timeout Impact:**
```
Timeout │ Accuracy │ Speed  │ False Negatives
────────┼──────────┼────────┼─────────────────
  0.5s  │   85%    │  Fast  │      High
  1.0s  │   92%    │  Good  │    Medium
  2.0s  │   98%    │  Slow  │       Low
  5.0s  │   99%    │  Slow  │   Very Low
```

## Troubleshooting

### Permission Issues

```bash
sudo hosthawk host 192.168.1.100 scantype syn
```

**Error:**
```
[!] Error: Permission denied
[*] SYN scans require root privileges
[*] Try: sudo hosthawk ...
```

### Network Unreachable

```bash
hosthawk host 192.168.1.100 verbose
```

**Debug Output:**
```
[DEBUG] Resolving target: 192.168.1.100
[DEBUG] Target resolved: 192.168.1.100
[DEBUG] Checking connectivity...
[ERROR] Network unreachable
[*] Possible causes:
     Target is down
     Firewall blocking ICMP
     Incorrect network configuration
[*] Try: ping 192.168.1.100
```
