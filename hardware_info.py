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
            gpu_info["driver"] = "N/A"  # GPUtil doesn't provide driver info
            gpu_info["memory_total"] = f"{gpu.memoryTotal} MB"
            gpu_info["memory_used"] = f"{gpu.memoryUsed} MB"
            gpu_info["memory_free"] = f"{gpu.memoryFree} MB"
            gpu_info["memory_utilization"] = f"{gpu.memoryUtil * 100:.2f}%"
            gpu_info["gpu_utilization"] = f"{gpu.load * 100:.2f}%"
            gpu_info["temperature"] = f"{gpu.temperature} °C"
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