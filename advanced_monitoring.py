import psutil
import threading
import time
from collections import deque
import socket
import json
import os

class AdvancedMonitoring:
    def __init__(self):
        self.resource_history = {
            'cpu': deque(maxlen=100),
            'memory': deque(maxlen=100),
            'disk': deque(maxlen=100),
            'network': deque(maxlen=100)
        }
        self.monitoring_thread = None
        self.is_monitoring = False

    def start_resource_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_resources)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()

    def _monitor_resources(self):
        while self.is_monitoring:
            try:
                # CPU Usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.resource_history['cpu'].append({
                    'timestamp': time.time(),
                    'value': cpu_percent
                })

                # Memory Usage
                memory = psutil.virtual_memory()
                self.resource_history['memory'].append({
                    'timestamp': time.time(),
                    'value': memory.percent
                })

                # Disk Usage
                disk = psutil.disk_usage('/')
                self.resource_history['disk'].append({
                    'timestamp': time.time(),
                    'value': disk.percent
                })

                # Network Usage
                net_io = psutil.net_io_counters()
                self.resource_history['network'].append({
                    'timestamp': time.time(),
                    'value': {
                        'bytes_sent': net_io.bytes_sent,
                        'bytes_recv': net_io.bytes_recv
                    }
                })

                time.sleep(1)
            except Exception as e:
                print(f"Error in resource monitoring: {str(e)}")
                time.sleep(1)

    def get_network_packet_stats(self):
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            }
        except Exception as e:
            return {'error': str(e)}

    def get_port_scan(self):
        try:
            open_ports = []
            for port in range(1, 1025):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex(('127.0.0.1', port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            return {'open_ports': open_ports}
        except Exception as e:
            return {'error': str(e)}

    def get_process_tree(self):
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return {'processes': processes}
        except Exception as e:
            return {'error': str(e)}

    def get_security_status(self):
        try:
            return {
                'firewall_status': 'Active',  # Placeholder
                'antivirus_status': 'Active',  # Placeholder
                'system_updates': 'Up to date',  # Placeholder
                'last_scan': time.time()
            }
        except Exception as e:
            return {'error': str(e)}

    def get_disk_health(self):
        try:
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except:
                    continue
            return {'disks': disk_info}
        except Exception as e:
            return {'error': str(e)}

    def get_fan_speed(self):
        try:
            # This is a placeholder as fan speed monitoring requires specific hardware access
            return {'fan_speeds': {'cpu_fan': 'N/A', 'system_fan': 'N/A'}}
        except Exception as e:
            return {'error': str(e)}

    def get_cpu_profile(self):
        try:
            return {
                'cpu_percent': psutil.cpu_percent(percpu=True),
                'cpu_freq': psutil.cpu_freq()._asdict(),
                'cpu_count': psutil.cpu_count(),
                'cpu_stats': psutil.cpu_stats()._asdict()
            }
        except Exception as e:
            return {'error': str(e)}

    def get_memory_profile(self):
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return {
                'virtual_memory': memory._asdict(),
                'swap_memory': swap._asdict()
            }
        except Exception as e:
            return {'error': str(e)}

    def get_startup_programs(self):
        try:
            # This is a placeholder as startup program detection varies by OS
            return {'startup_programs': []}
        except Exception as e:
            return {'error': str(e)}

    def get_optimization_tips(self):
        try:
            tips = []
            # CPU Usage Check
            if psutil.cpu_percent() > 80:
                tips.append("High CPU usage detected. Consider closing unnecessary applications.")
            
            # Memory Usage Check
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                tips.append("High memory usage detected. Consider freeing up some memory.")
            
            # Disk Usage Check
            disk = psutil.disk_usage('/')
            if disk.percent > 80:
                tips.append("Low disk space. Consider cleaning up unnecessary files.")
            
            return {'tips': tips}
        except Exception as e:
            return {'error': str(e)}

    def get_resource_history(self):
        try:
            return {
                'cpu': list(self.resource_history['cpu']),
                'memory': list(self.resource_history['memory']),
                'disk': list(self.resource_history['disk']),
                'network': list(self.resource_history['network'])
            }
        except Exception as e:
            return {'error': str(e)} 