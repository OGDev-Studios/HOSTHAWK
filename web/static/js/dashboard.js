// Dashboard functionality for HostHawk
class Dashboard {
    constructor() {
        this.socket = io();
        this.scanHistory = [];
        this.initEventListeners();
        this.loadInitialData();
    }

    initEventListeners() {
        // Real-time updates from WebSocket
        this.socket.on('scan_update', (data) => {
            this.updateDashboard(data);
        });

        // Periodically refresh dashboard data
        setInterval(() => this.refreshDashboard(), 30000);
    }

    async loadInitialData() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            this.updateDashboard(data);
            this.scanHistory = data.scanHistory || [];
            this.updateTrends();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async refreshDashboard() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            this.updateDashboard(data);
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
        }
    }

    updateDashboard(data) {
        // Update network scans
        this.updateCounter('networkScansCount', data.networkScans || 0);
        document.getElementById('lastNetworkScan').textContent = 
            `Last scan: ${data.lastNetworkScan ? new Date(data.lastNetworkScan).toLocaleString() : 'Never'}`;

        // Update vulnerability scans
        this.updateCounter('vulnScansCount', data.vulnerabilityScans || 0);
        document.getElementById('criticalVulns').textContent = data.criticalVulnerabilities || 0;
        document.getElementById('highVulns').textContent = data.highVulnerabilities || 0;
        
        // Update vulnerability severity bar
        this.updateVulnerabilityBar(data);

        // Update hosts
        this.updateCounter('hostsCount', data.totalHosts || 0);
        document.getElementById('hostsUp').textContent = data.hostsUp || 0;
        document.getElementById('hostsDown').textContent = data.hostsDown || 0;
        document.getElementById('hostsUnknown').textContent = data.hostsUnknown || 0;

        // Update ports
        this.updateCounter('openPortsCount', data.openPorts || 0);
        document.getElementById('topPort').textContent = data.topPort || '-';
        document.getElementById('uniqueServices').textContent = data.uniqueServices || 0;

        // Update scan history
        if (data.scanHistory) {
            this.scanHistory = data.scanHistory;
            this.updateTrends();
        }

        // Update charts if they exist
        if (window.updateCharts) {
            window.updateCharts(data);
        }
    }

    updateCounter(elementId, value) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const current = parseInt(element.textContent) || 0;
        const target = value;
        const duration = 1000; // ms
        const stepTime = 20; // ms
        const steps = duration / stepTime;
        const valueIncrement = (target - current) / steps;
        let currentValue = current;

        const counter = setInterval(() => {
            currentValue += valueIncrement;
            if ((valueIncrement >= 0 && currentValue >= target) || 
                (valueIncrement < 0 && currentValue <= target)) {
                element.textContent = target.toLocaleString();
                clearInterval(counter);
            } else {
                element.textContent = Math.round(currentValue).toLocaleString();
            }
        }, stepTime);
    }

    updateVulnerabilityBar(data) {
        const critical = data.criticalVulnerabilities || 0;
        const high = data.highVulnerabilities || 0;
        const medium = data.mediumVulnerabilities || 0;
        const low = data.lowVulnerabilities || 0;
        const total = critical + high + medium + low;
        
        if (total === 0) {
            document.getElementById('vulnSeverityBar').style.width = '0%';
            return;
        }
        
        // Calculate width based on critical and high severity
        const criticalPercent = (critical / total) * 100;
        const highPercent = (high / total) * 100;
        
        document.getElementById('vulnSeverityBar').style.width = `${criticalPercent + highPercent}%`;
    }

    updateTrends() {
        if (this.scanHistory.length < 2) return;

        const current = this.scanHistory[this.scanHistory.length - 1];
        const previous = this.scanHistory[this.scanHistory.length - 2];

        // Calculate trends
        this.calculateAndDisplayTrend('networkScansTrend', current.networkScans, previous.networkScans);
        this.calculateAndDisplayTrend('vulnScansTrend', current.vulnerabilityScans, previous.vulnerabilityScans);
        this.calculateAndDisplayTrend('hostsTrend', current.totalHosts, previous.totalHosts);
        this.calculateAndDisplayTrend('portsTrend', current.openPorts, previous.openPorts);
    }

    calculateAndDisplayTrend(elementId, currentValue, previousValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const trendIcon = element.previousElementSibling;
        
        if (previousValue === 0) {
            element.textContent = 'New';
            element.classList.add('font-bold');
            return;
        }
        
        const change = ((currentValue - previousValue) / previousValue) * 100;
        const changeRounded = Math.round(change * 10) / 10;
        
        if (change > 0) {
            element.textContent = `+${changeRounded}%`;
            element.classList.remove('text-red-600', 'text-gray-600');
            element.classList.add('text-green-600');
            trendIcon.className = 'fas fa-arrow-up text-sm';
        } else if (change < 0) {
            element.textContent = `${changeRounded}%`;
            element.classList.remove('text-green-600', 'text-gray-600');
            element.classList.add('text-red-600');
            trendIcon.className = 'fas fa-arrow-down text-sm';
        } else {
            element.textContent = '0%';
            element.classList.remove('text-green-600', 'text-red-600');
            element.classList.add('text-gray-600');
            trendIcon.className = 'fas fa-equals text-sm';
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
