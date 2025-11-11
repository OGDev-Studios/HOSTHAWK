from pysnmp.hlapi import *
import binascii
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class SNMPScanner:
    COMMON_COMMUNITIES = [
        'public', 'private', 'manager', 'admin', 'read', 'write', 'monitor',
        'snmp', 'snmpd', 'cisco', 'default', 'dilbert', 'enable', 'mngt',
        'read-write', 'read-only', 'root', 'router', 'rw', 'snmptrap', 'solaris',
        'switch', 'system', 'tech', 'tivoli', 'tiv0li', 'world', 'write', 'xyzzy'
    ]
    
    COMMON_OIDS = {
        'sysDescr': '1.3.6.1.2.1.1.1.0',
        'sysName': '1.3.6.1.2.1.1.5.0',
        'sysContact': '1.3.6.1.2.1.1.4.0',
        'sysLocation': '1.3.6.1.2.1.1.6.0',
        'sysServices': '1.3.6.1.2.1.1.7.0',
        'ifNumber': '1.3.6.1.2.1.2.1.0',
        'ifDescr': '1.3.6.1.2.1.2.2.1.2',
        'ifType': '1.3.6.1.2.1.2.2.1.3',
        'ifMtu': '1.3.6.1.2.1.2.2.1.4',
        'ifSpeed': '1.3.6.1.2.1.2.2.1.5',
        'ifPhysAddress': '1.3.6.1.2.1.2.2.1.6',
        'ifAdminStatus': '1.3.6.1.2.1.2.2.1.7',
        'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',
        'ipAdEntAddr': '1.3.6.1.2.1.4.20.1.1',
        'ipAdEntIfIndex': '1.3.6.1.2.1.4.20.1.2',
        'ipAdEntNetMask': '1.3.6.1.2.1.4.20.1.3',
        'ipAdEntBcastAddr': '1.3.6.1.2.1.4.20.1.4',
        'ipAdEntReasmMaxSize': '1.3.6.1.2.1.4.20.1.5',
        'ipRouteDest': '1.3.6.1.2.1.4.21.1.1',
        'ipRouteIfIndex': '1.3.6.1.2.1.4.21.1.2',
        'ipRouteMetric1': '1.3.6.1.2.1.4.21.1.3',
        'ipRouteNextHop': '1.3.6.1.2.1.4.21.1.7',
        'ipRouteType': '1.3.6.1.2.1.4.21.1.8',
        'ipRouteProto': '1.3.6.1.2.1.4.21.1.9',
        'ipRouteMask': '1.3.6.1.2.1.4.21.1.11',
        'tcpConnState': '1.3.6.1.2.1.6.13.1.1',
        'udpLocalAddress': '1.3.6.1.2.1.7.5.1.1',
        'hrSWRunName': '1.3.6.1.2.1.25.4.2.1.2',
        'hrSWRunPath': '1.3.6.1.2.1.25.4.2.1.4',
        'hrSWRunParameters': '1.3.6.1.2.1.25.4.2.1.5',
        'hrSWRunType': '1.3.6.1.2.1.25.4.2.1.6',
        'hrSWRunStatus': '1.3.6.1.2.1.25.4.2.1.7',
        'hrSWRunPerfCPU': '1.3.6.1.2.1.25.5.1.1.1',
        'hrSWRunPerfMem': '1.3.6.1.2.1.25.5.1.1.2',
        'hrSystemUptime': '1.3.6.1.2.1.25.1.1.0',
        'hrSystemNumUsers': '1.3.6.1.2.1.25.1.5.0',
        'hrSystemProcesses': '1.3.6.1.2.1.25.1.6.0',
        'hrSystemMaxProcesses': '1.3.6.1.2.1.25.1.7.0',
        'hrStorageIndex': '1.3.6.1.2.1.25.2.3.1.1',
        'hrStorageType': '1.3.6.1.2.1.25.2.3.1.2',
        'hrStorageDescr': '1.3.6.1.2.1.25.2.3.1.3',
        'hrStorageAllocationUnits': '1.3.6.1.2.1.25.2.3.1.4',
        'hrStorageSize': '1.3.6.1.2.1.25.2.3.1.5',
        'hrStorageUsed': '1.3.6.1.2.1.25.2.3.1.6',
        'hrStorageAllocationFailures': '1.3.6.1.2.1.25.2.3.1.7'
    }

    def __init__(self, timeout=2, threads=10):
        self.timeout = timeout
        self.threads = threads
        self.lock = threading.Lock()
        self.results = {}
        self.stop_event = threading.Event()

    def _snmp_get(self, target, oid, community='public', port=161, version=1):
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community, mpModel=0 if version == 1 else 1),
                   UdpTransportTarget((target, port), timeout=self.timeout, retries=0),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if error_indication:
            return None
        elif error_status:
            return None
        else:
            for var_bind in var_binds:
                return str(var_bind[1])
        return None

    def _snmp_walk(self, target, oid, community='public', port=161, version=1):
        result = []
        try:
            for (error_indication, error_status, error_index, var_binds) in nextCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=0 if version == 1 else 1),
                UdpTransportTarget((target, port), timeout=self.timeout, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False
            ):
                if error_indication:
                    break
                elif error_status:
                    break
                else:
                    for var_bind in var_binds:
                        result.append(str(var_bind[1]))
        except Exception:
            pass
        return result if result else None

    def _check_community(self, target, community, port=161):
        sys_descr = self._snmp_get(target, self.COMMON_OIDS['sysDescr'], 
                                 community=community, port=port)
        if sys_descr:
            return community, sys_descr
        return None

    def scan_community_strings(self, target, port=161, custom_communities=None):
        communities = self.COMMON_COMMUNITIES.copy()
        if custom_communities:
            communities.extend(custom_communities)
        
        results = {}
        
        def worker(community):
            if self.stop_event.is_set():
                return None
                
            result = self._check_community(target, community, port)
            if result:
                with self.lock:
                    results[community] = result[1]
                return community
            return None

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(worker, community) for community in communities]
            for future in as_completed(futures):
                if self.stop_event.is_set():
                    break
                future.result()
        
        return results

    def get_system_info(self, target, community='public', port=161, version=1):
        info = {}
        
        for name, oid in [
            ('sysDescr', self.COMMON_OIDS['sysDescr']),
            ('sysName', self.COMMON_OIDS['sysName']),
            ('sysContact', self.COMMON_OIDS['sysContact']),
            ('sysLocation', self.COMMON_OIDS['sysLocation']),
            ('sysServices', self.COMMON_OIDS['sysServices']),
            ('hrSystemUptime', self.COMMON_OIDS['hrSystemUptime']),
            ('hrSystemNumUsers', self.COMMON_OIDS['hrSystemNumUsers']),
            ('hrSystemProcesses', self.COMMON_OIDS['hrSystemProcesses'])
        ]:
            value = self._snmp_get(target, oid, community, port, version)
            if value:
                info[name] = value
        
        return info if info else None

    def get_interfaces(self, target, community='public', port=161, version=1):
        interfaces = {}
        
        if_indices = self._snmp_walk(target, self.COMMON_OIDS['ifDescr'], 
                                   community, port, version)
        
        if not if_indices:
            return None
            
        for idx, if_descr in enumerate(if_indices, 1):
            iface = {'index': idx, 'description': if_descr}
            
            for oid_name, oid in [
                ('type', self.COMMON_OIDS['ifType']),
                ('mtu', self.COMMON_OIDS['ifMtu']),
                ('speed', self.COMMON_OIDS['ifSpeed']),
                ('phys_address', self.COMMON_OIDS['ifPhysAddress']),
                ('admin_status', self.COMMON_OIDS['ifAdminStatus']),
                ('oper_status', self.COMMON_OIDS['ifOperStatus'])
            ]:
                value = self._snmp_get(target, f"{oid}.{idx}", community, port, version)
                if value:
                    if oid_name == 'phys_address' and value.startswith('0x'):
                        try:
                            value = binascii.hexlify(bytes.fromhex(value[2:])).decode('ascii')
                            value = ':'.join(value[i:i+2] for i in range(0, len(value), 2))
                        except:
                            pass
                    iface[oid_name] = value
            
            interfaces[idx] = iface
        
        return interfaces if interfaces else None

    def get_routing_table(self, target, community='public', port=161, version=1):
        routes = []
        
        dests = self._snmp_walk(target, self.COMMON_OIDS['ipRouteDest'], 
                              community, port, version)
        
        if not dests:
            return None
            
        for idx, dest in enumerate(dests, 1):
            route = {'destination': dest}
            
            for oid_name, oid in [
                ('next_hop', self.COMMON_OIDS['ipRouteNextHop']),
                ('type', self.COMMON_OIDS['ipRouteType']),
                ('protocol', self.COMMON_OIDS['ipRouteProto']),
                ('mask', self.COMMON_OIDS['ipRouteMask'])
            ]:
                value = self._snmp_get(target, f"{oid}.{idx}", community, port, version)
                if value:
                    route[oid_name] = value
            
            if route.get('next_hop'):
                routes.append(route)
        
        return routes if routes else None

    def get_installed_software(self, target, community='public', port=161, version=1):
        software = []
        
        names = self._snmp_walk(target, self.COMMON_OIDS['hrSWRunName'], 
                              community, port, version)
        
        if not names:
            return None
            
        for idx, name in enumerate(names, 1):
            sw = {'name': name}
            
            for oid_name, oid in [
                ('path', self.COMMON_OIDS['hrSWRunPath']),
                ('parameters', self.COMMON_OIDS['hrSWRunParameters']),
                ('type', self.COMMON_OIDS['hrSWRunType']),
                ('status', self.COMMON_OIDS['hrSWRunStatus']),
                ('cpu_usage', self.COMMON_OIDS['hrSWRunPerfCPU']),
                ('memory_usage', self.COMMON_OIDS['hrSWRunPerfMem'])
            ]:
                value = self._snmp_get(target, f"{oid}.{idx}", community, port, version)
                if value:
                    sw[oid_name] = value
            
            software.append(sw)
        
        return software if software else None

    def get_storage_info(self, target, community='public', port=161, version=1):
        storage = []
        
        types = self._snmp_walk(target, self.COMMON_OIDS['hrStorageType'], 
                              community, port, version)
        
        if not types:
            return None
            
        for idx, stype in enumerate(types, 1):
            store = {'type': stype}
            
            for oid_name, oid in [
                ('description', self.COMMON_OIDS['hrStorageDescr']),
                ('allocation_units', self.COMMON_OIDS['hrStorageAllocationUnits']),
                ('size', self.COMMON_OIDS['hrStorageSize']),
                ('used', self.COMMON_OIDS['hrStorageUsed']),
                ('allocation_failures', self.COMMON_OIDS['hrStorageAllocationFailures'])
            ]:
                value = self._snmp_get(target, f"{oid}.{idx}", community, port, version)
                if value:
                    store[oid_name] = value
            
            storage.append(store)
        
        return storage if storage else None

    def stop_scan(self):
        self.stop_event.set()
