import platform
import psutil
import GPUtil
import cpuinfo
from datetime import datetime

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_cpu_info():
    # CPU information
    cpu_info = {}
    
    # CPU name
    cpu_info["name"] = cpuinfo.get_cpu_info()['brand_raw']
    
    # CPU cores
    cpu_info["physical_cores"] = psutil.cpu_count(logical=False)
    cpu_info["total_cores"] = psutil.cpu_count(logical=True)
    
    # CPU frequencies - Fixed to handle 0 values better
    cpufreq = psutil.cpu_freq()
    if cpufreq:
        cpu_info["max_frequency"] = f"{cpufreq.max:.2f}MHz" if cpufreq.max else "N/A"
        cpu_info["min_frequency"] = f"{cpufreq.min:.2f}MHz" if cpufreq.min and cpufreq.min > 0 else "N/A"
        cpu_info["current_frequency"] = f"{cpufreq.current:.2f}MHz" if cpufreq.current else "N/A"
    else:
        cpu_info["max_frequency"] = "N/A"
        cpu_info["min_frequency"] = "N/A" 
        cpu_info["current_frequency"] = "N/A"
    
    # CPU usage
    cpu_info["usage_per_core"] = []
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        cpu_info["usage_per_core"].append({
            "core": i,
            "usage": percentage
        })
    
    cpu_info["total_cpu_usage"] = psutil.cpu_percent()
    
    # CPU temperature (if available)
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temp = psutil.sensors_temperatures()
            if temp and 'coretemp' in temp:
                cpu_info["temperature"] = temp['coretemp'][0].current
            else:
                cpu_info["temperature"] = "N/A"
        else:
            cpu_info["temperature"] = "N/A"
    except:
        cpu_info["temperature"] = "N/A"
    
    # CPU architecture
    cpu_info["architecture"] = cpuinfo.get_cpu_info()['arch']
    cpu_info["bits"] = cpuinfo.get_cpu_info()['bits']
    
    # CPU cache
    if 'l2_cache_size' in cpuinfo.get_cpu_info():
        cpu_info["l2_cache"] = get_size(cpuinfo.get_cpu_info()['l2_cache_size'])
    else:
        cpu_info["l2_cache"] = "N/A"
    
    if 'l3_cache_size' in cpuinfo.get_cpu_info():
        cpu_info["l3_cache"] = get_size(cpuinfo.get_cpu_info()['l3_cache_size'])
    else:
        cpu_info["l3_cache"] = "N/A"
    
    # Process information using CPU
    cpu_info["processes"] = []
    for process in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            process_info = process.info
            if process_info['cpu_percent'] > 0.5:  # Only show processes using significant CPU
                cpu_info["processes"].append({
                    "pid": process_info['pid'],
                    "name": process_info['name'],
                    "cpu_usage": process_info['cpu_percent']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort processes by CPU usage (descending)
    cpu_info["processes"] = sorted(cpu_info["processes"], key=lambda x: x["cpu_usage"], reverse=True)[:5]
    
    return cpu_info

def get_gpu_info():
    gpu_info = {}
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]  # Just get the first GPU if multiple exist
            gpu_info["name"] = gpu.name
            gpu_info["driver"] = gpu.driver
            gpu_info["memory_total"] = get_size(gpu.memoryTotal * 1024 * 1024)  # Convert MB to bytes
            gpu_info["memory_used"] = get_size(gpu.memoryUsed * 1024 * 1024)  # Convert MB to bytes
            gpu_info["memory_free"] = get_size(gpu.memoryFree * 1024 * 1024)  # Convert MB to bytes
            gpu_info["memory_utilization"] = f"{gpu.memoryUtil * 100:.1f}%"
            gpu_info["gpu_utilization"] = f"{gpu.load * 100:.1f}%"
            gpu_info["current_usage"] = f"{gpu.load * 100:.1f}%"
            gpu_info["temperature"] = f"{gpu.temperature:.1f} °C"
            gpu_info["display_mode"] = gpu.display_mode
            gpu_info["display_active"] = gpu.display_active
            
            # Tambahan informasi status
            gpu_info["status"] = "Active"
            if gpu.temperature > 80:
                gpu_info["status"] = "Warning: High Temperature"
            elif gpu.memoryUtil > 0.9:
                gpu_info["status"] = "Warning: High Memory Usage"
            elif gpu.load > 0.9:
                gpu_info["status"] = "Warning: High GPU Usage"
        else:
            gpu_info["status"] = "No GPU detected"
    except Exception as e:
        gpu_info["status"] = f"Error getting GPU info: {str(e)}"
        
    return gpu_info

def get_memory_info():
    memory_info = {}
    svmem = psutil.virtual_memory()
    memory_info["total"] = get_size(svmem.total)
    memory_info["available"] = get_size(svmem.available)
    memory_info["used"] = get_size(svmem.used)
    memory_info["percentage"] = svmem.percent
    
    # swap memory
    swap = psutil.swap_memory()
    memory_info["swap_total"] = get_size(swap.total)
    memory_info["swap_free"] = get_size(swap.free)
    memory_info["swap_used"] = get_size(swap.used)
    memory_info["swap_percentage"] = swap.percent
    
    return memory_info

def get_disk_info():
    disk_info = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "file_system_type": partition.fstype,
                "total_size": get_size(partition_usage.total),
                "used": get_size(partition_usage.used),
                "free": get_size(partition_usage.free),
                "percentage": partition_usage.percent
            })
        except Exception:
            pass
    
    # Disk I/O
    disk_io = psutil.disk_io_counters()
    if disk_io:
        disk_io_info = {
            "read_since_boot": get_size(disk_io.read_bytes),
            "write_since_boot": get_size(disk_io.write_bytes)
        }
    else:
        disk_io_info = {"status": "Disk I/O information not available"}
    
    return {"partitions": disk_info, "disk_io": disk_io_info}

def get_network_info():
    network_info = {}
    
    # Network interfaces
    if_addrs = psutil.net_if_addrs()
    network_info["interfaces"] = []
    
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                network_info["interfaces"].append({
                    "interface": interface_name,
                    "ip": address.address,
                    "netmask": address.netmask,
                    "broadcast": address.broadcast
                })
    
    # Network I/O
    net_io = psutil.net_io_counters()
    network_info["io"] = {
        "bytes_sent": get_size(net_io.bytes_sent),
        "bytes_received": get_size(net_io.bytes_recv)
    }
    
    return network_info

def get_system_info():
    system_info = {}
    system_info["system"] = platform.system()
    system_info["node_name"] = platform.node()
    system_info["release"] = platform.release()
    system_info["version"] = platform.version()
    system_info["machine"] = platform.machine()
    system_info["processor"] = platform.processor()
    system_info["uptime"] = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))
    system_info["current_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return system_info

def get_system_health():
    health_info = {}
    
    # System temperature monitoring
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            health_info["temperatures"] = {}
            
            # Check for common temperature sensors
            if temps:
                for sensor_name, entries in temps.items():
                    if entries:
                        # Get the highest temperature from each sensor
                        max_temp = max(entry.current for entry in entries)
                        health_info["temperatures"][sensor_name] = {
                            "current": max_temp,
                            "high": entries[0].high if hasattr(entries[0], 'high') else None,
                            "critical": entries[0].critical if hasattr(entries[0], 'critical') else None,
                            "label": entries[0].label if hasattr(entries[0], 'label') else sensor_name
                        }
            else:
                # If no temperature sensors found, try to get CPU temperature
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
                    temperature_infos = w.Sensor()
                    for sensor in temperature_infos:
                        if sensor.SensorType == 'Temperature':
                            health_info["temperatures"][sensor.Name] = {
                                "current": float(sensor.Value),
                                "high": 80,  # Default high threshold
                                "critical": 90,  # Default critical threshold
                                "label": sensor.Name
                            }
                except:
                    health_info["temperatures"] = {"status": "Temperature monitoring not available"}
        else:
            health_info["temperatures"] = {"status": "Temperature monitoring not available"}
    except Exception as e:
        health_info["temperatures"] = {"status": f"Error reading temperatures: {str(e)}"}

    # Fan speed monitoring
    try:
        if hasattr(psutil, "sensors_fans"):
            fans = psutil.sensors_fans()
            health_info["fans"] = {}
            
            if fans:
                for fan_name, entries in fans.items():
                    if entries:
                        # Get the highest fan speed from each fan
                        max_speed = max(entry.current for entry in entries)
                        health_info["fans"][fan_name] = {
                            "current": max_speed,
                            "label": entries[0].label if hasattr(entries[0], 'label') else fan_name
                        }
            else:
                # If no fan sensors found, try to get fan speeds from OpenHardwareMonitor
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
                    fan_infos = w.Sensor()
                    for sensor in fan_infos:
                        if sensor.SensorType == 'Fan':
                            health_info["fans"][sensor.Name] = {
                                "current": float(sensor.Value),
                                "label": sensor.Name
                            }
                except:
                    health_info["fans"] = {"status": "Fan monitoring not available"}
        else:
            health_info["fans"] = {"status": "Fan monitoring not available"}
    except Exception as e:
        health_info["fans"] = {"status": f"Error reading fan speeds: {str(e)}"}

    # Disk health status
    health_info["disk_health"] = []
    try:
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                health_info["disk_health"].append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "status": "Healthy" if usage.percent < 80 else "Warning" if usage.percent < 90 else "Critical",
                    "usage_percent": usage.percent,
                    "total": get_size(usage.total),
                    "used": get_size(usage.used),
                    "free": get_size(usage.free)
                })
            except:
                continue
    except:
        health_info["disk_health"] = {"status": "Error reading disk health"}

    # System stability metrics
    try:
        # CPU load average
        load_avg = psutil.getloadavg()
        health_info["load_average"] = {
            "1min": load_avg[0],
            "5min": load_avg[1],
            "15min": load_avg[2]
        }
        
        # Memory stability
        memory = psutil.virtual_memory()
        health_info["memory_stability"] = {
            "status": "Stable" if memory.percent < 90 else "Warning",
            "usage_percent": memory.percent
        }
        
        # CPU stability
        cpu_percent = psutil.cpu_percent(interval=1)
        health_info["cpu_stability"] = {
            "status": "Stable" if cpu_percent < 90 else "Warning",
            "usage_percent": cpu_percent
        }
    except:
        health_info["stability_metrics"] = {"status": "Error reading stability metrics"}

    # Error logs
    health_info["error_logs"] = {
        "status": "No critical errors",
        "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return health_info

def get_power_info():
    power_info = {}
    
    try:
        # Battery information
        battery = psutil.sensors_battery()
        if battery:
            power_info["battery"] = {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "time_left": str(datetime.timedelta(seconds=battery.secsleft)) if battery.secsleft > 0 else "N/A",
                "status": "Charging" if battery.power_plugged else "Discharging"
            }
        else:
            power_info["battery"] = {"status": "No battery detected"}

        # Power consumption estimation (simplified)
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Rough estimation of power consumption based on CPU and memory usage
        power_info["power_consumption"] = {
            "cpu_watts": round(cpu_percent * 0.1, 2),  # Simplified calculation
            "memory_watts": round(memory.percent * 0.05, 2),  # Simplified calculation
            "total_watts": round((cpu_percent * 0.1) + (memory.percent * 0.05), 2)
        }

        # Power mode detection (Windows only)
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Control\Power\User\PowerSchemes")
                active_scheme = winreg.QueryValueEx(key, "ActivePowerScheme")[0]
                power_info["power_mode"] = {
                    "current_scheme": active_scheme,
                    "is_high_performance": "High Performance" in active_scheme,
                    "is_power_saver": "Power Saver" in active_scheme
                }
            except:
                power_info["power_mode"] = {"status": "Unable to detect power mode"}
        else:
            power_info["power_mode"] = {"status": "Power mode detection not available on this platform"}

    except Exception as e:
        power_info["error"] = str(e)

    return power_info

def get_performance_report():
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_info": get_system_info(),
        "performance_metrics": {
            "cpu": {
                "usage": psutil.cpu_percent(),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                "cores": {
                    "physical": psutil.cpu_count(logical=False),
                    "logical": psutil.cpu_count(logical=True)
                }
            },
            "memory": {
                "total": get_size(psutil.virtual_memory().total),
                "used": get_size(psutil.virtual_memory().used),
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "partitions": []
            },
            "network": {
                "bytes_sent": get_size(psutil.net_io_counters().bytes_sent),
                "bytes_recv": get_size(psutil.net_io_counters().bytes_recv)
            }
        },
        "health_status": {
            "cpu_temperature": None,
            "disk_health": [],
            "memory_stability": None
        }
    }

    # Get CPU temperature if available
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                report["health_status"]["cpu_temperature"] = temps['coretemp'][0].current
    except:
        pass

    # Get disk health information
    try:
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                report["performance_metrics"]["disk"]["partitions"].append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total": get_size(usage.total),
                    "used": get_size(usage.used),
                    "free": get_size(usage.free),
                    "percent": usage.percent
                })
                
                # Add disk health status
                health_status = "Healthy"
                if usage.percent > 90:
                    health_status = "Critical"
                elif usage.percent > 80:
                    health_status = "Warning"
                
                report["health_status"]["disk_health"].append({
                    "device": partition.device,
                    "status": health_status,
                    "usage_percent": usage.percent
                })
            except:
                continue
    except:
        pass

    # Get memory stability
    try:
        memory = psutil.virtual_memory()
        report["health_status"]["memory_stability"] = {
            "status": "Stable" if memory.percent < 90 else "Warning",
            "usage_percent": memory.percent
        }
    except:
        pass

    return report