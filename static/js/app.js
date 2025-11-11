// Global variables
let socket;
let currentScanId = null;
let scanResults = {};

// DOM Elements
const scanForm = document.getElementById('scanForm');
const scanTypeSelect = document.getElementById('scanType');
const targetInput = document.getElementById('target');
const portsGroup = document.getElementById('portsGroup');
const portsInput = document.getElementById('ports');
const scanResultsSection = document.getElementById('scanResults');
const dashboardOverview = document.getElementById('dashboardOverview');
const resultsContainer = document.getElementById('resultsContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const progressCount = document.getElementById('progressCount');
const currentTask = document.getElementById('currentTask');
const recentScansList = document.getElementById('recentScans');
const recentActivity = document.getElementById('recentActivity');

// Stats counters
const networkScansCount = document.getElementById('networkScansCount');
const vulnScansCount = document.getElementById('vulnScansCount');
const hostsCount = document.getElementById('hostsCount');
const vulnsCount = document.getElementById('vulnsCount');

// Modal elements
const reportModal = document.getElementById('reportModal');
const reportFrame = document.getElementById('reportFrame');
const closeModal = document.getElementById('closeModal');
const printReportBtn = document.getElementById('printReport');
const downloadReportBtn = document.getElementById('downloadReport');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Setup event listeners
    setupEventListeners();
    
    // Update UI based on scan type
    updateScanTypeUI(scanTypeSelect.value);
    
    // Load recent scans from localStorage
    loadRecentScans();
});

// Initialize WebSocket connection
function initializeWebSocket() {
    // Connect to the WebSocket server
    socket = io();
    
    // Connection established
    socket.on('connect', () => {
        console.log('Connected to WebSocket server');
        addActivity('Connected to scanner', 'info');
    });
    
    // Handle scan updates
    socket.on('scan_update', (data) => {
        console.log('Scan update:', data);
        updateScanProgress(data);
    });
    
    // Handle scan completion
    socket.on('scan_complete', (data) => {
        console.log('Scan complete:', data);
        handleScanComplete(data);
    });
    
    // Handle scan errors
    socket.on('scan_error', (error) => {
        console.error('Scan error:', error);
        handleScanError(error);
    });
    
    // Handle connection errors
    socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error);
        addActivity('Connection error: ' + error.message, 'error');
    });
}

// Setup event listeners
function setupEventListeners() {
    // Scan type change
    scanTypeSelect.addEventListener('change', (e) => {
        updateScanTypeUI(e.target.value);
    });
    
    // Form submission
    scanForm.addEventListener('submit', (e) => {
        e.preventDefault();
        startScan();
    });
    
    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const scanType = e.currentTarget.dataset.scanType;
            scanTypeSelect.value = scanType;
            updateScanTypeUI(scanType);
            targetInput.focus();
        });
    });
    
    // Modal controls
    closeModal.addEventListener('click', () => {
        reportModal.classList.add('hidden');
        reportFrame.src = '';
    });
    
    printReportBtn.addEventListener('click', () => {
        if (reportFrame.contentWindow) {
            reportFrame.contentWindow.print();
        }
    });
    
    downloadReportBtn.addEventListener('click', () => {
        if (currentScanId) {
            window.location.href = `/api/scan/${currentScanId}/report`;
        }
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === reportModal) {
            reportModal.classList.add('hidden');
            reportFrame.src = '';
        }
    });
}

// Update UI based on selected scan type
function updateScanTypeUI(scanType) {
    // Show/hide ports input
    if (['port_scan', 'vulnerability_scan', 'network_scan'].includes(scanType)) {
        portsGroup.classList.remove('hidden');
    } else {
        portsGroup.classList.add('hidden');
    }
    
    // Update target placeholder and label
    switch (scanType) {
        case 'port_scan':
            targetInput.placeholder = 'e.g., 192.168.1.1 or example.com';
            document.getElementById('targetLabel').textContent = 'Target Host';
            break;
        case 'vulnerability_scan':
            targetInput.placeholder = 'e.g., 192.168.1.1 or example.com';
            document.getElementById('targetLabel').textContent = 'Target Host';
            break;
        case 'network_scan':
            targetInput.placeholder = 'e.g., 192.168.1.0/24 or 192.168.1.1-100';
            document.getElementById('targetLabel').textContent = 'Network Range';
            break;
        case 'snmp_scan':
            targetInput.placeholder = 'e.g., 192.168.1.1';
            document.getElementById('targetLabel').textContent = 'Target IP';
            break;
    }
}

// Start a new scan
function startScan() {
    const scanType = scanTypeSelect.value;
    const target = targetInput.value.trim();
    const ports = portsInput.value.trim();
    
    // Validate input
    if (!target) {
        alert('Please enter a target');
        return;
    }
    
    // Prepare scan data
    const scanData = {
        type: scanType,
        target: target
    };
    
    if (ports) {
        scanData.ports = ports;
    }
    
    // Show loading state
    showLoading(true);
    
    // Send scan request to server
    fetch('/api/scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(scanData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'started') {
            currentScanId = data.scan_id;
            scanResults[data.scan_id] = {
                status: 'running',
                start_time: new Date().toISOString(),
                type: scanType,
                target: target
            };
            
            // Update UI
            showScanResults();
            addActivity(`Started ${formatScanType(scanType)} on ${target}`, 'scan');
            saveRecentScan(scanResults[data.scan_id]);
        }
    })
    .catch(error => {
        console.error('Error starting scan:', error);
        addActivity('Failed to start scan: ' + error.message, 'error');
        showLoading(false);
    });
}

// Update scan progress
function updateScanProgress(data) {
    if (currentScanId !== data.scan_id) return;
    
    // Update progress bar
    const progress = parseInt(data.progress) || 0;
    progressBar.style.width = `${progress}%`;
    progressText.textContent = `${progress}%`;
    
    // Update progress count
    if (data.current !== undefined && data.total !== undefined) {
        progressCount.textContent = `${data.current}/${data.total}`;
    }
    
    // Update current task
    if (data.current_task) {
        currentTask.textContent = data.current_task;
    }
    
    // Update scan results in memory
    if (scanResults[data.scan_id]) {
        scanResults[data.scan_id].progress = progress;
        scanResults[data.scan_id].current_task = data.current_task;
        
        // Update the UI with partial results if available
        if (data.results) {
            scanResults[data.scan_id].results = data.results;
            updateResultsUI(data.scan_id);
        }
    }
}

// Handle scan completion
function handleScanComplete(data) {
    if (currentScanId !== data.scan_id) return;
    
    // Update scan results
    if (scanResults[data.scan_id]) {
        scanResults[data.scan_id].status = 'completed';
        scanResults[data.scan_id].end_time = new Date().toISOString();
        scanResults[data.scan_id].report_path = data.report_path;
        
        // Save to recent scans
        saveRecentScan(scanResults[data.scan_id]);
        
        // Show completion message
        addActivity(`Scan completed: ${scanResults[data.scan_id].target}`, 'success');
        
        // Update UI
        updateResultsUI(data.scan_id);
        updateDashboardStats();
        
        // Show report button
        const viewReportBtn = document.createElement('button');
        viewReportBtn.className = 'mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700';
        viewReportBtn.innerHTML = '<i class="fas fa-file-alt mr-2"></i>View Full Report';
        viewReportBtn.onclick = () => viewReport(data.scan_id);
        
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'mt-6 pt-4 border-t border-gray-200 flex justify-end';
        actionsDiv.appendChild(viewReportBtn);
        
        resultsContainer.appendChild(actionsDiv);
    }
    
    showLoading(false);
}

// Handle scan errors
function handleScanError(error) {
    if (currentScanId && scanResults[currentScanId]) {
        scanResults[currentScanId].status = 'error';
        scanResults[currentScanId].error = error.message || 'Unknown error';
        
        // Show error in UI
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-50 border-l-4 border-red-500 p-4 mb-4';
        errorDiv.innerHTML = `
            <div class="flex">
                <div class="flex-shrink-0">
                    <i class="fas fa-exclamation-circle text-red-500"></i>
                </div>
                <div class="ml-3">
                    <p class="text-sm text-red-700">
                        ${error.message || 'An error occurred during the scan'}
                    </p>
                </div>
            </div>
        `;
        
        resultsContainer.appendChild(errorDiv);
        addActivity(`Scan failed: ${error.message || 'Unknown error'}`, 'error');
    }
    
    showLoading(false);
}

// Update the results UI
function updateResultsUI(scanId) {
    if (!scanResults[scanId] || !scanResults[scanId].results) return;
    
    const scan = scanResults[scanId];
    let html = '';
    
    switch (scan.type) {
        case 'port_scan':
            html = renderPortScanResults(scan.results);
            break;
        case 'vulnerability_scan':
            html = renderVulnerabilityScanResults(scan.results);
            break;
        case 'network_scan':
            html = renderNetworkScanResults(scan.results);
            break;
        case 'snmp_scan':
            html = renderSnmpScanResults(scan.results);
            break;
        default:
            html = '<p>No results to display</p>';
    }
    
    resultsContainer.innerHTML = html;
}

// Render port scan results
function renderPortScanResults(results) {
    if (!results.ports || Object.keys(results.ports).length === 0) {
        return '<p>No open ports found.</p>';
    }
    
    let html = `
        <div class="mb-6">
            <h3 class="text-lg font-medium text-gray-900 mb-3">Open Ports</h3>
            <div class="bg-white shadow overflow-hidden sm:rounded-md">
                <ul class="divide-y divide-gray-200">
    `;
    
    for (const [port, info] of Object.entries(results.ports)) {
        const service = info.service || {};
        
        html += `
            <li class="px-4 py-4 sm:px-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <div class="min-w-0 flex-1">
                            <div class="text-sm font-medium text-indigo-600 truncate">
                                Port ${port}/${info.protocol || 'tcp'}
                                <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    ${info.status}
                                </span>
                            </div>
                            <div class="mt-1 flex items-center text-sm text-gray-500">
                                ${service.name ? `<span>${service.name}</span>` : ''}
                                ${service.version ? `<span class="ml-2">${service.version}</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            ${service.product || 'Unknown service'}
                        </span>
                    </div>
                </div>
            </li>
        `;
    }
    
    html += `
                </ul>
            </div>
        </div>
    `;
    
    return html;
}

// Render vulnerability scan results
function renderVulnerabilityScanResults(results) {
    let html = '';
    
    // Show port scan results if available
    if (results.ports && Object.keys(results.ports).length > 0) {
        html += renderPortScanResults(results);
    }
    
    // Show vulnerabilities if found
    if (results.vulnerabilities && results.vulnerabilities.length > 0) {
        html += `
            <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-3">Vulnerabilities Found</h3>
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul class="divide-y divide-gray-200">
        `;
        
        results.vulnerabilities.forEach(vuln => {
            const severityClass = {
                'critical': 'bg-red-100 text-red-800',
                'high': 'bg-orange-100 text-orange-800',
                'medium': 'bg-yellow-100 text-yellow-800',
                'low': 'bg-blue-100 text-blue-800',
                'info': 'bg-gray-100 text-gray-800'
            }[vuln.severity?.toLowerCase()] || 'bg-gray-100 text-gray-800';
            
            html += `
                <li class="px-4 py-4 sm:px-6">
                    <div class="flex items-center justify-between">
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center">
                                <p class="text-sm font-medium text-gray-900 truncate">
                                    ${vuln.name || 'Unnamed Vulnerability'}
                                </p>
                                <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityClass}">
                                    ${vuln.severity || 'Unknown'}
                                </span>
                            </div>
                            <div class="mt-1 text-sm text-gray-500">
                                ${vuln.description || 'No description available.'}
                            </div>
                            ${vuln.solution ? `
                                <div class="mt-2">
                                    <span class="text-xs font-medium text-gray-500">Solution:</span>
                                    <p class="text-sm text-gray-700">${vuln.solution}</p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </li>
            `;
        });
        
        html += `
                    </ul>
                </div>
            </div>
        `;
    } else if (results.ports && Object.keys(results.ports).length > 0) {
        html += `
            <div class="rounded-md bg-green-50 p-4">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <i class="h-5 w-5 text-green-400 fas fa-check-circle"></i>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-green-800">
                            No vulnerabilities found on the scanned ports.
                        </p>
                    </div>
                </div>
            </div>
        `;
    }
    
    return html || '<p>No vulnerabilities found.</p>';
}

// Render network scan results
function renderNetworkScanResults(results) {
    if (!results.hosts || results.hosts.length === 0) {
        return '<p>No hosts found.</p>';
    }
    
    let html = `
        <div class="mb-6">
            <h3 class="text-lg font-medium text-gray-900 mb-3">Discovered Hosts (${results.hosts.length})</h3>
            <div class="bg-white shadow overflow-hidden sm:rounded-md">
    `;
    
    results.hosts.forEach(host => {
        const openPorts = host.ports ? Object.values(host.ports).filter(p => p.status === 'open').length : 0;
        
        html += `
            <div class="border-b border-gray-200">
                <div class="px-4 py-4 sm:px-6">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="min-w-0 flex-1">
                                <div class="flex items-center">
                                    <p class="text-sm font-medium text-indigo-600 truncate">
                                        ${host.ip}
                                    </p>
                                    ${host.mac ? `
                                        <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                            ${host.mac}
                                        </span>
                                    ` : ''}
                                </div>
                                <div class="mt-1 flex items-center text-sm text-gray-500">
                                    ${host.vendor || ''}
                                    ${openPorts ? `<span class="ml-2">${openPorts} open ports</span>` : ''}
                                </div>
                            </div>
                        </div>
                        <div class="ml-2 flex-shrink-0 flex">
                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                Online
                            </span>
                        </div>
                    </div>
        `;
        
        // Show open ports if available
        if (openPorts > 0) {
            html += `
                <div class="mt-3">
                    <h4 class="text-sm font-medium text-gray-500">Open Ports:</h4>
                    <div class="mt-1 flex flex-wrap gap-1">
            `;
            
            for (const [port, info] of Object.entries(host.ports)) {
                if (info.status === 'open') {
                    html += `
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                            ${port}/${info.protocol || 'tcp'}
                        </span>
                    `;
                }
            }
            
            html += `
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    return html;
}

// Render SNMP scan results
function renderSnmpScanResults(results) {
    let html = '';
    
    // Community strings
    if (results.community_strings && Object.keys(results.community_strings).length > 0) {
        html += `
            <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-3">SNMP Community Strings</h3>
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul class="divide-y divide-gray-200">
        `;
        
        for (const [community, banner] of Object.entries(results.community_strings)) {
            html += `
                <li class="px-4 py-4 sm:px-6">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="min-w-0 flex-1">
                                <div class="text-sm font-medium text-indigo-600 truncate">
                                    ${community}
                                </div>
                                ${banner ? `
                                    <div class="mt-1 text-sm text-gray-500 font-mono text-xs bg-gray-50 p-2 rounded">
                                        ${banner}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                        <div>
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Accessible
                            </span>
                        </div>
                    </div>
                </li>
            `;
        }
        
        html += `
                    </ul>
                </div>
            </div>
        `;
    }
    
    // System information
    if (results.system_info && Object.keys(results.system_info).length > 0) {
        html += `
            <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-3">System Information</h3>
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <div class="px-4 py-5 sm:p-6">
                        <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
        `;
        
        for (const [key, value] of Object.entries(results.system_info)) {
            html += `
                <div class="sm:col-span-1">
                    <dt class="text-sm font-medium text-gray-500">
                        ${formatKey(key)}
                    </dt>
                    <dd class="mt-1 text-sm text-gray-900 break-all">
                        ${value || 'N/A'}
                    </dd>
                </div>
            `;
        }
        
        html += `
                        </dl>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Interfaces
    if (results.interfaces && Object.keys(results.interfaces).length > 0) {
        html += `
            <div class="mb-6">
                <h3 class="text-lg font-medium text-gray-900 mb-3">Network Interfaces</h3>
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul class="divide-y divide-gray-200">
        `;
        
        for (const [ifIndex, iface] of Object.entries(results.interfaces)) {
            html += `
                <li class="px-4 py-4 sm:px-6">
                    <div class="flex items-center justify-between">
                        <div class="min-w-0 flex-1">
                            <div class="flex items-center">
                                <p class="text-sm font-medium text-indigo-600 truncate">
                                    ${iface.description || `Interface ${ifIndex}`}
                                </p>
                                <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                    ${iface.type || 'Unknown'}
                                </span>
                            </div>
                            <div class="mt-1 text-sm text-gray-500">
                                ${iface.phys_address ? `MAC: ${iface.phys_address}` : ''}
                                ${iface.speed ? ` | Speed: ${formatSpeed(iface.speed)}` : ''}
                                ${iface.mtu ? ` | MTU: ${iface.mtu}` : ''}
                            </div>
                            <div class="mt-1">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    iface.oper_status === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }">
                                    ${iface.oper_status || 'unknown'}
                                </span>
                                <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    iface.admin_status === 'up' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
                                }">
                                    Admin: ${iface.admin_status || 'unknown'}
                                </span>
                            </div>
                        </div>
                    </div>
                </li>
            `;
        }
        
        html += `
                    </ul>
                </div>
            </div>
        `;
    }
    
    return html || '<p>No SNMP information available.</p>';
}

// View report in modal
function viewReport(scanId) {
    if (!scanId || !scanResults[scanId]?.report_path) return;
    
    reportFrame.src = `/api/scan/${scanId}/report?format=html`;
    reportModal.classList.remove('hidden');
}

// Show/hide loading state
function showLoading(show) {
    if (show) {
        scanResultsSection.classList.remove('hidden');
        dashboardOverview.classList.add('hidden');
        resultsContainer.innerHTML = `
            <div class="text-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500 mx-auto"></div>
                <p class="mt-4 text-gray-600">Scanning in progress...</p>
            </div>
        `;
    } else {
        // Show scan results or dashboard based on context
        if (currentScanId && scanResults[currentScanId]?.status === 'completed') {
            scanResultsSection.classList.remove('hidden');
            dashboardOverview.classList.add('hidden');
        } else {
            scanResultsSection.classList.add('hidden');
            dashboardOverview.classList.remove('hidden');
        }
    }
}

// Show scan results
function showScanResults() {
    scanResultsSection.classList.remove('hidden');
    dashboardOverview.classList.add('hidden');
    
    // Reset progress
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    progressCount.textContent = '0/0';
    currentTask.textContent = 'Initializing scan...';
    
    // Clear previous results
    resultsContainer.innerHTML = '';
}

// Add activity to the activity feed
function addActivity(message, type = 'info') {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    
    const iconClass = {
        'info': 'fa-info-circle text-blue-500',
        'success': 'fa-check-circle text-green-500',
        'error': 'fa-exclamation-circle text-red-500',
        'warning': 'fa-exclamation-triangle text-yellow-500',
        'scan': 'fa-search text-indigo-500'
    }[type] || 'fa-info-circle text-gray-500';
    
    const activityItem = document.createElement('div');
    activityItem.className = 'flex items-start';
    activityItem.innerHTML = `
        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-${type === 'error' ? 'red' : 'indigo'}-100 flex items-center justify-center text-${type === 'error' ? 'red' : 'indigo'}-600">
            <i class="fas ${iconClass}"></i>
        </div>
        <div class="ml-4">
            <p class="text-sm text-gray-600">${message}</p>
            <p class="text-xs text-gray-400">${timeString}</p>
        </div>
    `;
    
    // Add to the top of the activity list
    if (recentActivity.firstChild) {
        recentActivity.insertBefore(activityItem, recentActivity.firstChild);
    } else {
        recentActivity.appendChild(activityItem);
    }
    
    // Limit to 10 activities
    if (recentActivity.children.length > 10) {
        recentActivity.removeChild(recentActivity.lastChild);
    }
}

// Save recent scan to localStorage
function saveRecentScan(scan) {
    let recentScans = JSON.parse(localStorage.getItem('recentScans') || '[]');
    
    // Add new scan to the beginning
    recentScans.unshift({
        id: currentScanId,
        type: scan.type,
        target: scan.target,
        status: scan.status,
        start_time: scan.start_time,
        end_time: scan.end_time || new Date().toISOString()
    });
    
    // Keep only the 5 most recent scans
    recentScans = recentScans.slice(0, 5);
    
    // Save to localStorage
    localStorage.setItem('recentScans', JSON.stringify(recentScans));
    
    // Update UI
    loadRecentScans();
}

// Load recent scans from localStorage
function loadRecentScans() {
    const recentScans = JSON.parse(localStorage.getItem('recentScans') || '[]');
    
    if (recentScans.length === 0) {
        recentScansList.innerHTML = `
            <div class="text-center text-gray-500 py-4">
                <p>No recent scans</p>
            </div>
        `;
        return;
    }
    
    let html = '<ul class="space-y-3">';
    
    recentScans.forEach(scan => {
        const statusClass = {
            'completed': 'bg-green-100 text-green-800',
            'running': 'bg-yellow-100 text-yellow-800',
            'error': 'bg-red-100 text-red-800'
        }[scan.status] || 'bg-gray-100 text-gray-800';
        
        const timeAgo = formatTimeAgo(scan.end_time || scan.start_time);
        
        html += `
            <li class="bg-gray-50 p-3 rounded-md hover:bg-gray-100 cursor-pointer" 
                onclick="loadScan('${scan.id}')">
                <div class="flex justify-between items-start">
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">
                            ${formatScanType(scan.type)}: ${scan.target}
                        </p>
                        <p class="text-xs text-gray-500">${timeAgo}</p>
                    </div>
                    <span class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClass}">
                        ${scan.status}
                    </span>
                </div>
            </li>
        `;
    });
    
    html += '</ul>';
    recentScansList.innerHTML = html;
    
    // Update dashboard stats
    updateDashboardStats();
}

// Load a previous scan
function loadScan(scanId) {
    if (!scanId || !scanResults[scanId]) {
        alert('Scan data not found. It may have expired.');
        return;
    }
    
    currentScanId = scanId;
    const scan = scanResults[scanId];
    
    // Update UI
    scanTypeSelect.value = scan.type;
    targetInput.value = scan.target;
    updateScanTypeUI(scan.type);
    
    // Show results
    showScanResults();
    
    if (scan.status === 'completed') {
        // Show completed scan
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
        currentTask.textContent = 'Scan completed';
        
        // Show results
        updateResultsUI(scanId);
        
        // Add view report button if available
        if (scan.report_path) {
            const viewReportBtn = document.createElement('button');
            viewReportBtn.className = 'mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700';
            viewReportBtn.innerHTML = '<i class="fas fa-file-alt mr-2"></i>View Full Report';
            viewReportBtn.onclick = () => viewReport(scanId);
            
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'mt-6 pt-4 border-t border-gray-200 flex justify-end';
            actionsDiv.appendChild(viewReportBtn);
            
            resultsContainer.appendChild(actionsDiv);
        }
    } else if (scan.status === 'running') {
        // Show in-progress scan
        progressBar.style.width = `${scan.progress || 0}%`;
        progressText.textContent = `${scan.progress || 0}%`;
        currentTask.textContent = scan.current_task || 'Scan in progress...';
        
        // Show partial results if available
        if (scan.results) {
            updateResultsUI(scanId);
        }
    } else if (scan.status === 'error') {
        // Show error
        handleScanError({ message: scan.error || 'Unknown error' });
    }
    
    // Add to recent scans if not already there
    const recentScans = JSON.parse(localStorage.getItem('recentScans') || '[]');
    if (!recentScans.some(s => s.id === scanId)) {
        saveRecentScan(scan);
    }
}

// Update dashboard statistics
function updateDashboardStats() {
    const recentScans = JSON.parse(localStorage.getItem('recentScans') || '[]');
    
    // Count scan types
    const scanCounts = recentScans.reduce((acc, scan) => {
        acc[scan.type] = (acc[scan.type] || 0) + 1;
        return acc;
    }, {});
    
    // Update counters
    networkScansCount.textContent = scanCounts.network_scan || 0;
    vulnScansCount.textContent = scanCounts.vulnerability_scan || 0;
    
    // Count unique hosts and vulnerabilities (simplified)
    const uniqueHosts = new Set();
    let totalVulns = 0;
    
    Object.values(scanResults).forEach(scan => {
        if (scan.results) {
            // Count hosts
            if (scan.results.hosts) {
                scan.results.hosts.forEach(host => {
                    if (host.ip) uniqueHosts.add(host.ip);
                });
            } else if (scan.results.target) {
                uniqueHosts.add(scan.results.target);
            }
            
            // Count vulnerabilities
            if (scan.results.vulnerabilities) {
                totalVulns += scan.results.vulnerabilities.length;
            }
        }
    });
    
    hostsCount.textContent = uniqueHosts.size;
    vulnsCount.textContent = totalVulns;
}

// Helper function to format time ago
function formatTimeAgo(timestamp) {
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    
    let interval = Math.floor(seconds / 31536000);
    if (interval > 1) return `${interval} years ago`;
    if (interval === 1) return '1 year ago';
    
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) return `${interval} months ago`;
    if (interval === 1) return '1 month ago';
    
    interval = Math.floor(seconds / 86400);
    if (interval > 1) return `${interval} days ago`;
    if (interval === 1) return 'yesterday';
    
    interval = Math.floor(seconds / 3600);
    if (interval > 1) return `${interval} hours ago`;
    if (interval === 1) return '1 hour ago';
    
    interval = Math.floor(seconds / 60);
    if (interval > 1) return `${interval} minutes ago`;
    if (interval === 1) return '1 minute ago';
    
    return 'just now';
}

// Helper function to format scan type
function formatScanType(scanType) {
    const types = {
        'port_scan': 'Port Scan',
        'vulnerability_scan': 'Vulnerability Scan',
        'network_scan': 'Network Scan',
        'snmp_scan': 'SNMP Scan'
    };
    
    return types[scanType] || scanType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Helper function to format key names
function formatKey(key) {
    return key
        .replace(/([A-Z])/g, ' $1')
        .replace(/_/g, ' ')
        .replace(/^\w/, c => c.toUpperCase());
}

// Helper function to format speed
function formatSpeed(speed) {
    if (speed >= 1000000000) {
        return `${(speed / 1000000000).toFixed(1)} Gbps`;
    } else if (speed >= 1000000) {
        return `${(speed / 1000000).toFixed(1)} Mbps`;
    } else if (speed >= 1000) {
        return `${(speed / 1000).toFixed(1)} Kbps`;
    } else {
        return `${speed} bps`;
    }
}

// Make functions available globally
window.loadScan = loadScan;
