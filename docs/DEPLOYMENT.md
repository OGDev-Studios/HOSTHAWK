# Deployment Guide

This guide covers deploying HostHawk in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#localdevelopment)
3. [Docker Deployment](#dockerdeployment)
4. [Production Deployment](#productiondeployment)
5. [Environment Configuration](#environmentconfiguration)
6. [Security Considerations](#securityconsiderations)

## Prerequisites

### System Requirements

* Python 3.8 or higher
* Root/Administrator privileges (for certain scan types)
* Network access to target systems
* 2GB RAM minimum (4GB recommended)
* 1GB disk space

### Dependencies

Install system dependencies:

**Ubuntu/Debian:**
```bash
sudo aptget update
sudo aptget install python3pip libpcapdev tcpdump nmap
```

**macOS:**
```bash
brew install python libpcap nmap
```

**Windows:**
* Install Python from python.org
* Install Npcap from npcap.com
* Install Nmap from nmap.org

## Local Development

### Quick Start

```bash
git clone https://github.com/yourusername/hosthawk.git
cd hosthawk
python m venv venv
source venv/bin/activate
pip install e ".[dev]"
```

### Running Tests

```bash
make test
```

### Running the Web Interface

```bash
python m web.app
```

Access at http://localhost:5000

## Docker Deployment

### Build and Run

```bash
dockercompose up d
```

### Custom Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your settings, then:

```bash
dockercompose up d
```

### View Logs

```bash
dockercompose logs f
```

### Stop Services

```bash
dockercompose down
```

## Production Deployment

### Using Gunicorn

Install Gunicorn:

```bash
pip install gunicorn
```

Run the application:

```bash
gunicorn w 4 b 0.0.0.0:5000 web.app:app
```

### Using Nginx as Reverse Proxy

Nginx configuration example:

```nginx
server {
    listen 80;
    server_name hosthawk.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header XRealIP $remote_addr;
        proxy_set_header XForwardedFor $proxy_add_x_forwarded_for;
    }
}
```

### Systemd Service

Create `/etc/systemd/system/hosthawk.service`:

```ini
[Unit]
Description=HostHawk Network Scanner
After=network.target

[Service]
Type=simple
User=hosthawk
WorkingDirectory=/opt/hosthawk
Environment="PATH=/opt/hosthawk/venv/bin"
ExecStart=/opt/hosthawk/venv/bin/gunicorn w 4 b 127.0.0.1:5000 web.app:app
Restart=always

[Install]
WantedBy=multiuser.target
```

Enable and start:

```bash
sudo systemctl enable hosthawk
sudo systemctl start hosthawk
```

## Environment Configuration

### Required Variables

```bash
HOSTHAWK_LOG_LEVEL=INFO
HOSTHAWK_THREADS=50
HOSTHAWK_TIMEOUT=2.0
```

### Optional Variables

```bash
HOSTHAWK_OUTPUT_DIR=/var/lib/hosthawk/output
HOSTHAWK_REPORTS_DIR=/var/lib/hosthawk/reports
HOSTHAWK_MAX_RETRIES=3
HOSTHAWK_RATE_LIMIT=100
```

### Flask Configuration

```bash
FLASK_SECRET_KEY=yoursecretkeyhere
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

## Security Considerations

### Network Security

* Use firewall rules to restrict access
* Enable HTTPS with valid certificates
* Implement rate limiting
* Use VPN for remote access

### Application Security

* Change default secret keys
* Use strong authentication
* Enable audit logging
* Regular security updates

### Privilege Management

* Run with minimal required privileges
* Use capabilitybased permissions when possible
* Avoid running as root in production

### Data Protection

* Encrypt sensitive scan results
* Implement access controls
* Regular backups
* Secure log storage

## Monitoring

### Health Checks

```bash
curl http://localhost:5000/health
```

### Log Monitoring

```bash
tail f logs/hosthawk.log
```

### Metrics Collection

Monitor these metrics:

* Scan completion rate
* Error rate
* Response time
* Resource usage

## Troubleshooting

### Permission Errors

If you encounter permission errors:

```bash
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/python3
```

### Port Conflicts

Check if port 5000 is in use:

```bash
lsof i :5000
```

### Database Issues

Reset the database:

```bash
rm rf data/
python m scanner.db.init
```

## Scaling

### Horizontal Scaling

Use a load balancer to distribute traffic across multiple instances.

### Vertical Scaling

Increase resources:

* CPU cores for parallel scanning
* RAM for large network scans
* Disk space for reports and logs

### Performance Tuning

Optimize settings:

```bash
HOSTHAWK_THREADS=100
HOSTHAWK_TIMEOUT=1.0
HOSTHAWK_RATE_LIMIT=200
```

## Backup and Recovery

### Backup Strategy

Backup these directories:

* `reports/`  Scan reports
* `logs/`  Application logs
* `config.json`  Configuration

### Automated Backups

```bash
#!/bin/bash
tar czf backup$(date +%Y%m%d).tar.gz reports/ logs/ config.json
```

## Updates

### Update Process

```bash
git pull origin main
pip install e . upgrade
sudo systemctl restart hosthawk
```

### Database Migrations

```bash
python m scanner.db.migrate
```

## Support

For deployment issues:

* Email: support@hosthawk.io
* Documentation: https://hosthawk.readthedocs.io
* GitHub Issues: https://github.com/yourusername/hosthawk/issues
