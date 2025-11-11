from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from threading import Lock
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Import scanner modules
import sys
sys.path.append(str(Path(__file__).parent.parent))
from scanner.core.scanner import NetworkScanner
from scanner.plugins.vulnerability_scanner import VulnerabilityScanner
from scanner.plugins.snmp_scanner import SNMPScanner
from scanner.plugins.device_fingerprinter import DeviceFingerprinter
from scanner.reporting.report_generator import ReportGenerator

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, async_mode='threading')

# Global variables
scan_thread = None
thread_lock = Lock()
scan_results = {}
current_scan_id = None

# Initialize scanners
network_scanner = NetworkScanner(timeout=2, threads=50)
vuln_scanner = VulnerabilityScanner()
snmp_scanner = SNMPScanner()
device_fingerprinter = DeviceFingerprinter()
report_generator = ReportGenerator(output_dir='reports')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def start_scan():
    global current_scan_id
    
    data = request.json
    scan_type = data.get('type')
    target = data.get('target')
    ports = data.get('ports', '1-1024')
    scan_id = f"scan_{int(time.time())}"
    
    with thread_lock:
        if current_scan_id:
            return jsonify({
                'status': 'error',
                'message': 'A scan is already in progress'
            }), 400
        
        current_scan_id = scan_id
        scan_results[scan_id] = {
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'results': {},
            'progress': 0,
            'current_task': 'Initializing scan...'
        }
    
    # Start scan in background
    socketio.start_background_task(
        target=run_scan,
        scan_id=scan_id,
        scan_type=scan_type,
        target=target,
        ports=ports
    )
    
    return jsonify({
        'status': 'started',
        'scan_id': scan_id
    })

@app.route('/api/scan/<scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    with thread_lock:
        if scan_id not in scan_results:
            return jsonify({
                'status': 'error',
                'message': 'Scan not found'
            }), 404
            
        return jsonify(scan_results[scan_id])

@app.route('/api/scan/<scan_id>/report', methods=['GET'])
def get_scan_report(scan_id):
    format = request.args.get('format', 'html')
    
    with thread_lock:
        if scan_id not in scan_results or 'report_path' not in scan_results[scan_id]:
            return jsonify({
                'status': 'error',
                'message': 'Report not available'
            }), 404
            
        report_path = scan_results[scan_id]['report_path']
        
        if format == 'json':
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            return jsonify(report_data)
        else:
            return send_from_directory(
                os.path.dirname(report_path),
                os.path.basename(report_path),
                as_attachment=True
            )

# WebSocket events
@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected to scanner'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Scan functions
def run_scan(scan_id, scan_type, target, ports):
    try:
        results = {}
        
        with thread_lock:
            scan_results[scan_id]['current_task'] = f'Starting {scan_type} scan on {target}'
        
        socketio.emit('scan_update', {
            'scan_id': scan_id,
            'status': 'running',
            'message': f'Starting {scan_type} scan on {target}'
        })
        
        if scan_type == 'port_scan':
            results = run_port_scan(scan_id, target, ports)
        elif scan_type == 'vulnerability_scan':
            results = run_vulnerability_scan(scan_id, target, ports)
        elif scan_type == 'network_scan':
            results = run_network_scan(scan_id, target, ports)
        elif scan_type == 'snmp_scan':
            results = run_snmp_scan(scan_id, target)
        
        # Generate report
        with thread_lock:
            scan_results[scan_id]['current_task'] = 'Generating report...'
        
        report_path = generate_report(scan_id, results, scan_type)
        
        with thread_lock:
            scan_results[scan_id].update({
                'status': 'completed',
                'end_time': datetime.now().isoformat(),
                'results': results,
                'report_path': report_path,
                'progress': 100,
                'current_task': 'Scan completed'
            })
            
        socketio.emit('scan_complete', {
            'scan_id': scan_id,
            'status': 'completed',
            'report_path': f'/api/scan/{scan_id}/report?format=html'
        })
        
    except Exception as e:
        with thread_lock:
            if scan_id in scan_results:
                scan_results[scan_id].update({
                    'status': 'error',
                    'error': str(e),
                    'end_time': datetime.now().isoformat()
                })
        
        socketio.emit('scan_error', {
            'scan_id': scan_id,
            'error': str(e)
        })
        
    finally:
        with thread_lock:
            global current_scan_id
            current_scan_id = None

def run_port_scan(scan_id, target, ports):
    results = {
        'target': target,
        'scan_type': 'port_scan',
        'ports': {},
        'start_time': datetime.now().isoformat()
    }
    
    def progress_callback(progress, current, total, current_task):
        with thread_lock:
            if scan_id in scan_results:
                scan_results[scan_id].update({
                    'progress': progress,
                    'current_task': current_task
                })
        
        socketio.emit('scan_progress', {
            'scan_id': scan_id,
            'progress': progress,
            'current': current,
            'total': total,
            'current_task': current_task
        })
    
    # Run the port scan
    open_ports = network_scanner.scan_ports(target, ports, progress_callback=progress_callback)
    
    # Process results
    for port, status in open_ports:
        results['ports'][port] = {
            'status': status,
            'service': network_scanner._service_detection(target, port)
        }
    
    results['end_time'] = datetime.now().isoformat()
    return results

def run_vulnerability_scan(scan_id, target, ports):
    results = {
        'target': target,
        'scan_type': 'vulnerability_scan',
        'vulnerabilities': [],
        'start_time': datetime.now().isoformat()
    }
    
    # First, run a port scan
    port_results = run_port_scan(scan_id, target, ports)
    results['ports'] = port_results.get('ports', {})
    
    # Check for vulnerabilities on open ports
    for port, info in results['ports'].items():
        if info['status'] == 'open':
            vulns = vuln_scanner.scan_port(target, port, info.get('protocol', 'tcp'))
            if vulns:
                results['vulnerabilities'].extend(vulns)
    
    results['end_time'] = datetime.now().isoformat()
    return results

def run_network_scan(scan_id, network, ports):
    results = {
        'network': network,
        'scan_type': 'network_scan',
        'hosts': [],
        'start_time': datetime.now().isoformat()
    }
    
    # Discover hosts
    hosts = network_scanner.scan_network(network)
    
    for i, host in enumerate(hosts):
        host_ip = host[0] if isinstance(host, tuple) else host
        host_info = {
            'ip': host_ip,
            'status': 'up',
            'ports': {}
        }
        
        if isinstance(host, tuple):
            host_info['mac'] = host[1]
            host_info['vendor'] = device_fingerprinter._get_vendor_from_mac(host[1])
        
        # Port scan the host
        try:
            port_results = network_scanner.scan_ports(host_ip, ports)
            for port, status in port_results:
                host_info['ports'][port] = {
                    'status': status,
                    'service': network_scanner._service_detection(host_ip, port)
                }
        except Exception as e:
            host_info['error'] = str(e)
        
        results['hosts'].append(host_info)
        
        # Update progress
        progress = int((i + 1) / len(hosts) * 100)
        with thread_lock:
            if scan_id in scan_results:
                scan_results[scan_id].update({
                    'progress': progress,
                    'current_task': f'Scanned {host_ip} ({i+1}/{len(hosts)})'
                })
        
        socketio.emit('scan_progress', {
            'scan_id': scan_id,
            'progress': progress,
            'current': i + 1,
            'total': len(hosts),
            'current_task': f'Scanned {host_ip} ({i+1}/{len(hosts)})'
        })
    
    results['end_time'] = datetime.now().isoformat()
    return results

def run_snmp_scan(scan_id, target):
    results = {
        'target': target,
        'scan_type': 'snmp_scan',
        'community_strings': {},
        'system_info': {},
        'interfaces': {},
        'start_time': datetime.now().isoformat()
    }
    
    # Try common community strings
    communities = snmp_scanner.scan_community_strings(target)
    results['community_strings'] = communities
    
    if communities:
        # Use first valid community string to get more info
        community = list(communities.keys())[0]
        
        # Get system info
        results['system_info'] = snmp_scanner.get_system_info(target, community) or {}
        
        # Get interfaces
        results['interfaces'] = snmp_scanner.get_interfaces(target, community) or {}
    
    results['end_time'] = datetime.now().isoformat()
    return results

def generate_report(scan_id, results, scan_type):
    report_data = {
        'scan_id': scan_id,
        'scan_type': scan_type,
        'start_time': results.get('start_time'),
        'end_time': results.get('end_time'),
        'target': results.get('target') or results.get('network'),
        'results': results
    }
    
    # Generate HTML report by default
    report_path = report_generator.generate_report(
        report_data,
        format='html',
        filename=f"{scan_type}_{scan_id}"
    )
    
    return report_path

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('reports', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    
    # Run the app
    socketio.run(app, 
                host='0.0.0.0', 
                port=5000, 
                debug=True, 
                use_reloader=True,
                allow_unsafe_werkzeug=True)
