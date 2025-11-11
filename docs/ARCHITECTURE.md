# HostHawk Architecture

## System Overview

HostHawk is built with a modular, pluginbased architecture designed for extensibility and performance.

```
┌─────────────────────────────────────────────────────────────────┐
│                        HostHawk System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐         ┌──────────────┐                    │
│  │   CLI Layer   │◄────────┤  Web Layer   │                    │
│  │   (cli.py)    │         │   (app.py)   │                    │
│  └───────┬───────┘         └──────┬───────┘                    │
│          │                        │                            │
│          └────────────┬───────────┘                            │
│                       │                                        │
│          ┌────────────▼────────────┐                           │
│          │    Core Scanner Engine  │                           │
│          │    (scanner/core/)      │                           │
│          └────────────┬────────────┘                           │
│                       │                                        │
│          ┌────────────┴────────────┐                           │
│          │                         │                           │
│    ┌─────▼──────┐          ┌──────▼──────┐                    │
│    │  Plugins   │          │   Output    │                    │
│    │  System    │          │   System    │                    │
│    └────────────┘          └─────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Scanner Engine

The heart of HostHawk, responsible for all scanning operations.

```
scanner/core/
├── scanner.py          # Main NetworkScanner class
├── port_scanner.py     # Port scanning implementations
├── host_discovery.py   # Network discovery
└── service_detector.py # Service identification

┌──────────────────────────────────────────┐
│         NetworkScanner                   │
├──────────────────────────────────────────┤
│  + scan_network()                        │
│  + scan_ports()                          │
│  + detect_services()                     │
│  + fingerprint_os()                      │
└──────────────────────────────────────────┘
         │
         ├─────► PortScanner
         │       ├── TCP Connect Scan
         │       ├── SYN Scan
         │       └── UDP Scan
         │
         ├─────► HostDiscovery
         │       ├── ICMP Ping
         │       ├── ARP Scan
         │       └── TCP Ping
         │
         └─────► ServiceDetector
                 ├── Banner Grabbing
                 ├── Protocol Analysis
                 └── Version Detection
```

### 2. Plugin System

Extensible plugin architecture for additional functionality.

```
scanner/plugins/
├── vulnerability_scanner.py
├── snmp_scanner.py
├── dns_enum.py
└── web_crawler.py

┌────────────────────────────────────────┐
│         Plugin Base Class              │
├────────────────────────────────────────┤
│  + initialize()                        │
│  + execute()                           │
│  + cleanup()                           │
└────────────────────────────────────────┘
         │
         ├─────► VulnerabilityScanner
         │       └── CVE Database Integration
         │
         ├─────► SNMPScanner
         │       └── SNMP Enumeration
         │
         ├─────► DNSEnumerator
         │       └── DNS Record Discovery
         │
         └─────► WebCrawler
                 └── Website Structure Analysis
```

### 3. Output System

Multiple output formats for different use cases.

```
scanner/output/
├── formatters/
│   ├── json_formatter.py
│   ├── csv_formatter.py
│   ├── xml_formatter.py
│   └── html_formatter.py
└── report_generator.py

Data Flow:
┌──────────┐    ┌────────────┐    ┌──────────┐
│  Scan    │───►│  Formatter │───►│  Output  │
│  Results │    │  (JSON/CSV)│    │   File   │
└──────────┘    └────────────┘    └──────────┘
```

### 4. Configuration System

Flexible configuration management.

```
scanner/config.py

┌─────────────────────────────────────────┐
│         Configuration Sources           │
├─────────────────────────────────────────┤
│  1. Environment Variables               │
│     ↓                                   │
│  2. Config File (JSON)                  │
│     ↓                                   │
│  3. Command Line Arguments              │
│     ↓                                   │
│  4. Default Values                      │
└─────────────────────────────────────────┘
```

## Data Flow

### Scanning Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Scan Execution Flow                      │
└─────────────────────────────────────────────────────────────┘

1. Input Validation
   ┌──────────────┐
   │ User Input   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Validators  │
   │   IP/CIDR   │
   │   Ports     │
   │   Options   │
   └──────┬───────┘
          │
          ▼

2. Target Preparation
   ┌──────────────┐
   │  Resolve     │
   │  Targets     │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Generate    │
   │  Port List   │
   └──────┬───────┘
          │
          ▼

3. Scanning Phase
   ┌──────────────┐
   │  Thread Pool │
   │  Manager     │
   └──────┬───────┘
          │
          ├─────► Worker 1 ──┐
          ├─────► Worker 2 ──┤
          ├─────► Worker 3 ──┼──► Scan Tasks
          ├─────► Worker N ──┘
          │
          ▼

4. Results Collection
   ┌──────────────┐
   │  Aggregate   │
   │  Results     │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Post       │
   │  Processing  │
   └──────┬───────┘
          │
          ▼

5. Output Generation
   ┌──────────────┐
   │  Format      │
   │  Results     │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Save/       │
   │  Display     │
   └──────────────┘
```

## Threading Model

### Thread Pool Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Thread Pool Manager                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Main Thread                                            │
│  ┌────────────────────────────────────────────┐        │
│  │  • Initialize Scanner                      │        │
│  │  • Create Thread Pool                      │        │
│  │  • Distribute Tasks                        │        │
│  │  • Collect Results                         │        │
│  └────────────────────────────────────────────┘        │
│                      │                                  │
│                      ▼                                  │
│  ┌──────────────────────────────────────────┐          │
│  │         Task Queue                       │          │
│  │  [Task1][Task2][Task3]...[TaskN]        │          │
│  └──────────────────────────────────────────┘          │
│           │      │      │           │                  │
│           ▼      ▼      ▼           ▼                  │
│  ┌────────┐┌────────┐┌────────┐┌────────┐            │
│  │Worker 1││Worker 2││Worker 3││Worker N│            │
│  └────┬───┘└────┬───┘└────┬───┘└────┬───┘            │
│       │         │         │         │                 │
│       └─────────┴─────────┴─────────┘                 │
│                      │                                  │
│                      ▼                                  │
│  ┌──────────────────────────────────────────┐          │
│  │         Results Queue                    │          │
│  │  [Result1][Result2][Result3]...[ResultN]│          │
│  └──────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Concurrency Strategy

```
Scan Type          │ Threads │ Strategy
───────────────────┼─────────┼──────────────────────────
Network Discovery  │   10    │ Conservative (ICMP)
Port Scan (TCP)    │   50    │ Balanced
Port Scan (SYN)    │  100    │ Aggressive (requires root)
Service Detection  │   20    │ Conservative (timeouts)
Vulnerability Scan │   10    │ Conservative (heavy ops)
```

## Network Communication

### Packet Structure

```
TCP SYN Scan Packet:
┌────────────────────────────────────────┐
│         IP Header                      │
├────────────────────────────────────────┤
│  Source IP:      192.168.1.50          │
│  Dest IP:        192.168.1.100         │
│  Protocol:       TCP (6)               │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│         TCP Header                     │
├────────────────────────────────────────┤
│  Source Port:    Random (>1024)        │
│  Dest Port:      80                    │
│  Flags:          SYN                   │
│  Seq Number:     Random                │
└────────────────────────────────────────┘

Response Analysis:
┌────────────────────────────────────────┐
│  SYNACK Received  →  Port OPEN        │
│  RST Received      →  Port CLOSED      │
│  No Response       →  Port FILTERED    │
└────────────────────────────────────────┘
```

### Protocol Support

```
┌─────────────────────────────────────────────────────┐
│              Supported Protocols                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Layer 3 (Network)                                  │
│  ├── ICMP (Ping, Echo Request/Reply)               │
│  └── ARP (Address Resolution)                      │
│                                                     │
│  Layer 4 (Transport)                                │
│  ├── TCP                                            │
│  │   ├── Connect Scan                              │
│  │   ├── SYN Scan                                  │
│  │   └── ACK Scan                                  │
│  └── UDP                                            │
│      └── UDP Scan                                   │
│                                                     │
│  Layer 7 (Application)                              │
│  ├── HTTP/HTTPS                                     │
│  ├── SSH                                            │
│  ├── FTP                                            │
│  ├── SMTP                                           │
│  ├── DNS                                            │
│  ├── SNMP                                           │
│  └── Custom Protocol Detection                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Security Architecture

### Input Validation Pipeline

```
┌─────────────────────────────────────────────────────┐
│           Input Validation Flow                     │
└─────────────────────────────────────────────────────┘

User Input
    │
    ▼
┌──────────────┐
│  Sanitize    │  → Remove dangerous characters
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Validate    │  → Check format and ranges
│  Format      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Validate    │  → Verify network accessibility
│  Target      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Rate        │  → Apply rate limiting
│  Limiting    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Execute     │
│  Scan        │
└──────────────┘
```

### Permission Model

```
┌─────────────────────────────────────────────────────┐
│           Privilege Requirements                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User Privileges (No root required)                 │
│  ├── TCP Connect Scan                              │
│  ├── Service Detection                             │
│  ├── Banner Grabbing                               │
│  └── Output Generation                             │
│                                                     │
│  Root Privileges (sudo required)                    │
│  ├── SYN Scan (raw sockets)                        │
│  ├── ICMP Ping (raw sockets)                       │
│  ├── ARP Scan (raw sockets)                        │
│  └── OS Fingerprinting (raw sockets)               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Web Interface Architecture

### FrontendBackend Communication

```
┌─────────────────────────────────────────────────────┐
│              Web Interface Stack                    │
└─────────────────────────────────────────────────────┘

Browser
   │
   │ HTTP/WebSocket
   ▼
┌──────────────┐
│   Flask      │
│   Server     │
└──────┬───────┘
       │
       ├──► Static Files (HTML/CSS/JS)
       │
       ├──► REST API Endpoints
       │    ├── /api/scan (POST)
       │    ├── /api/scan/:id (GET)
       │    └── /api/report/:id (GET)
       │
       └──► WebSocket (Realtime updates)
            └── Scan progress
            └── Live results

┌─────────────────────────────────────────────────────┐
│              Request Flow                           │
└─────────────────────────────────────────────────────┘

1. User submits scan via web form
   │
   ▼
2. Flask receives POST /api/scan
   │
   ▼
3. Validate input parameters
   │
   ▼
4. Create scan job (async)
   │
   ▼
5. Return scan_id to client
   │
   ▼
6. Client polls /api/scan/:id
   │
   ▼
7. Scanner executes in background
   │
   ▼
8. Results streamed via WebSocket
   │
   ▼
9. Final report generated
```

### API Response Structure

```json
{
  "scan": {
    "id": "abc123",
    "status": "completed",
    "progress": 100,
    "start_time": "20241111T17:30:00Z",
    "end_time": "20241111T17:32:15Z",
    "duration": 135.2
  },
  "target": {
    "type": "network",
    "value": "192.168.1.0/24",
    "hosts_found": 12
  },
  "results": {
    "hosts": [
      {
        "ip": "192.168.1.100",
        "hostname": "server1.local",
        "status": "up",
        "ports": [
          {
            "port": 80,
            "protocol": "tcp",
            "state": "open",
            "service": "http",
            "version": "nginx 1.18.0"
          }
        ]
      }
    ]
  },
  "statistics": {
    "total_hosts": 256,
    "active_hosts": 12,
    "total_ports_scanned": 12288,
    "open_ports": 45,
    "closed_ports": 12243
  }
}
```

## Database Schema (Future)

### Scan History Storage

```
┌─────────────────────────────────────────────────────┐
│              Database Schema                        │
└─────────────────────────────────────────────────────┘

scans
├── id (PRIMARY KEY)
├── target
├── scan_type
├── start_time
├── end_time
├── status
└── user_id

scan_results
├── id (PRIMARY KEY)
├── scan_id (FOREIGN KEY)
├── host
├── port
├── service
├── version
└── timestamp

vulnerabilities
├── id (PRIMARY KEY)
├── scan_result_id (FOREIGN KEY)
├── cve_id
├── severity
├── description
└── recommendation

Relationships:
scans (1) ──────► (N) scan_results
scan_results (1) ──────► (N) vulnerabilities
```

## Performance Optimization

### Caching Strategy

```
┌─────────────────────────────────────────────────────┐
│              Cache Layers                           │
└─────────────────────────────────────────────────────┘

1. DNS Resolution Cache
   ├── TTL: 300 seconds
   └── Size: 1000 entries

2. Service Signature Cache
   ├── TTL: 3600 seconds
   └── Size: 500 entries

3. Vulnerability Database Cache
   ├── TTL: 86400 seconds
   └── Size: 10000 entries

Cache Hit Rates:
┌────────────────┬──────────┬──────────┐
│ Cache Type     │ Hit Rate │ Speedup  │
├────────────────┼──────────┼──────────┤
│ DNS            │   85%    │   10x    │
│ Service Sig    │   70%    │    5x    │
│ Vuln DB        │   95%    │   50x    │
└────────────────┴──────────┴──────────┘
```

### Memory Management

```
Memory Usage by Component:
┌────────────────────────────────────────┐
│  Thread Pool:        100 MB            │
│  Result Buffer:       50 MB            │
│  Cache:               30 MB            │
│  Scanner Engine:      20 MB            │
│  Plugins:             15 MB            │
│  ─────────────────────────             │
│  Total:              215 MB            │
└────────────────────────────────────────┘

Scaling:
 Base memory: 215 MB
 Per thread: +1 MB
 Per 1000 results: +5 MB
```

## Error Handling

### Exception Hierarchy

```
HostHawkException
├── ScannerException
│   ├── NetworkScanException
│   │   ├── HostUnreachableException
│   │   └── NetworkTimeoutException
│   ├── PortScanException
│   │   ├── PortTimeoutException
│   │   └── ConnectionRefusedException
│   └── PermissionException
│       ├── RootRequiredException
│       └── FirewallBlockedException
├── ValidationException
│   ├── InvalidTargetException
│   ├── InvalidPortRangeException
│   └── InvalidConfigException
└── OutputException
    ├── FileWriteException
    └── FormatException

Error Flow:
┌──────────────┐
│  Exception   │
│  Raised      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Catch &     │
│  Log         │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  User        │
│  Notification│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Graceful    │
│  Recovery    │
└──────────────┘
```

## Deployment Architecture

### Docker Container Structure

```
┌─────────────────────────────────────────────────────┐
│              Docker Container                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Alpine Linux Base                          │   │
│  └─────────────────────────────────────────────┘   │
│                     │                               │
│  ┌─────────────────▼───────────────────────────┐   │
│  │  Python 3.9 Runtime                         │   │
│  └─────────────────────────────────────────────┘   │
│                     │                               │
│  ┌─────────────────▼───────────────────────────┐   │
│  │  System Dependencies                        │   │
│  │   libpcap                                  │   │
│  │   nmap                                     │   │
│  │   nettools                                │   │
│  └─────────────────────────────────────────────┘   │
│                     │                               │
│  ┌─────────────────▼───────────────────────────┐   │
│  │  HostHawk Application                       │   │
│  │  /app/scanner/                              │   │
│  └─────────────────────────────────────────────┘   │
│                     │                               │
│  ┌─────────────────▼───────────────────────────┐   │
│  │  Volumes                                    │   │
│  │   /app/reports (output)                    │   │
│  │   /app/logs (logs)                         │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘

Container Size: ~150 MB
```

## Extensibility

### Plugin Development

```
┌─────────────────────────────────────────────────────┐
│           Plugin Interface                          │
└─────────────────────────────────────────────────────┘

from scanner.plugins.base import BasePlugin

class CustomPlugin(BasePlugin):
    
    def __init__(self, config):
        super().__init__(config)
        self.name = "CustomPlugin"
    
    def initialize(self):
        pass
    
    def execute(self, target, **kwargs):
        return results
    
    def cleanup(self):
        pass

Plugin Lifecycle:
┌──────────────┐
│ Initialize   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Execute      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Cleanup      │
└──────────────┘
```

## Future Enhancements

### Planned Features

```
┌─────────────────────────────────────────────────────┐
│              Roadmap                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Phase 1 (Current)                                  │
│  ├── Core scanning functionality                   │
│  ├── Basic plugins                                 │
│  └── CLI and Web interface                         │
│                                                     │
│  Phase 2 (Next)                                     │
│  ├── Database integration                          │
│  ├── Scan history and comparison                   │
│  ├── Advanced reporting                            │
│  └── API authentication                            │
│                                                     │
│  Phase 3 (Future)                                   │
│  ├── Distributed scanning                          │
│  ├── Machine learning integration                  │
│  ├── Realtime alerting                            │
│  └── Cloud deployment support                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```
