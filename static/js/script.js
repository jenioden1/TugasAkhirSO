// Format numbers with commas as thousands separators
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format dates
function formatUptime(uptimeStr) {
    // Parse the uptime string which is in format like "1 day, 3:45:12.345678"
    const parts = uptimeStr.split(', ');
    let days = 0;
    let timeStr = '';
    
    if (parts.length > 1) {
        days = parseInt(parts[0].split(' ')[0]);
        timeStr = parts[1];
    } else {
        timeStr = parts[0];
    }
    
    const timeComponents = timeStr.split(':');
    const hours = parseInt(timeComponents[0]);
    const minutes = parseInt(timeComponents[1]);
    
    // Format the result
    let result = '';
    if (days > 0) {
        result += `${days} day${days > 1 ? 's' : ''} `;
    }
    if (hours > 0 || days > 0) {
        result += `${hours} hour${hours > 1 ? 's' : ''} `;
    }
    result += `${minutes} minute${minutes > 1 ? 's' : ''}`;
    
    return result;
}

// Update current time
function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleString();
}

// Determine color based on percentage
function getColorClass(percentage) {
    if (percentage < 50) return 'text-green-400';
    if (percentage < 80) return 'text-yellow-400';
    return 'text-red-400';
}

// Fetch hardware information and update the UI
function fetchHardwareInfo() {
    fetch('/api/hardware_info')
        .then(response => response.json())
        .then(data => {
            updateSystemInfo(data.system);
            updateCpuInfo(data.cpu);
            updateGpuInfo(data.gpu);
            updateMemoryInfo(data.memory);
            updateDiskInfo(data.disk);
            updateNetworkInfo(data.network);
        })
        .catch(error => {
            console.error('Error fetching hardware info:', error);
        });
}

// Update system information
function updateSystemInfo(system) {
    document.getElementById('system-name').textContent = `${system.node_name} (${system.system} ${system.machine})`;
    document.getElementById('system-info').textContent = `${system.release} ${system.version}`;
    document.getElementById('uptime').textContent = formatUptime(system.uptime);
}

// Update CPU information
function updateCpuInfo(cpu) {
    // CPU basic info
    document.getElementById('cpu-name').textContent = cpu.name;
    document.getElementById('physical-cores').textContent = cpu.physical_cores;
    document.getElementById('logical-cores').textContent = cpu.total_cores;
    document.getElementById('min-freq').textContent = cpu.min_frequency;
    document.getElementById('max-freq').textContent = cpu.max_frequency;
    document.getElementById('cpu-arch').textContent = `${cpu.architecture} ${cpu.bits}-bit`;
    
    // CPU usage
    const cpuUsage = cpu.total_cpu_usage;
    document.getElementById('cpu-usage-percent').textContent = `${cpuUsage.toFixed(1)}%`;
    document.getElementById('cpu-usage-percent').className = getColorClass(cpuUsage);
    document.getElementById('cpu-usage-bar').style.width = `${cpuUsage}%`;
    
    // Update color of the bar based on usage
    const usageBar = document.getElementById('cpu-usage-bar');
    if (cpuUsage < 50) {
        usageBar.className = "bg-gradient-to-r from-green-400 to-blue-500 h-4 rounded-full transition-all duration-500";
    } else if (cpuUsage < 80) {
        usageBar.className = "bg-gradient-to-r from-yellow-400 to-orange-500 h-4 rounded-full transition-all duration-500";
    } else {
        usageBar.className = "bg-gradient-to-r from-orange-500 to-red-600 h-4 rounded-full transition-all duration-500";
    }
    
    // Per-core usage
    const coresContainer = document.getElementById('cpu-cores-usage');
    coresContainer.innerHTML = '';
    
    cpu.usage_per_core.forEach(core => {
        const coreUsage = core.usage;
        const colorClass = getColorClass(coreUsage);
        
        const coreElement = document.createElement('div');
        coreElement.innerHTML = `
            <div class="text-xs flex justify-between mb-1">
                <span>Core ${core.core}</span>
                <span class="${colorClass}">${coreUsage.toFixed(1)}%</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
                <div class="bg-blue-500 h-2 rounded-full" style="width: ${coreUsage}%"></div>
            </div>
        `;
        coresContainer.appendChild(coreElement);
    });
    
    // CPU processes
    const processesTable = document.getElementById('cpu-processes');
    processesTable.innerHTML = '';
    
    cpu.processes.forEach(process => {
        const row = document.createElement('tr');
        row.className = 'border-t border-gray-600';
        row.innerHTML = `
            <td class="py-2 px-3 text-sm">${process.name}</td>
            <td class="py-2 px-3 text-sm">${process.pid}</td>
            <td class="py-2 px-3 text-sm ${getColorClass(process.cpu_usage)}">${process.cpu_usage.toFixed(1)}%</td>
        `;
        processesTable.appendChild(row);
    });
}

// Update GPU information
function updateGpuInfo(gpu) {
    const gpuInfoContainer = document.getElementById('gpu-info-container');
    const noGpuMessage = document.getElementById('no-gpu-message');
    
    if (gpu.status && gpu.status.includes('No GPU')) {
        gpuInfoContainer.classList.add('hidden');
        noGpuMessage.classList.remove('hidden');
        return;
    }
    
    gpuInfoContainer.classList.remove('hidden');
    noGpuMessage.classList.add('hidden');
    
    // GPU name
    document.getElementById('gpu-name').textContent = gpu.name;
    
    // GPU memory
    const memoryPercent = parseFloat(gpu.memory_utilization);
    document.getElementById('gpu-memory-percent').textContent = gpu.memory_utilization;
    document.getElementById('gpu-memory-bar').style.width = `${memoryPercent}%`;
    document.getElementById('gpu-memory-used').textContent = gpu.memory_used;
    document.getElementById('gpu-memory-total').textContent = gpu.memory_total;
    
    // GPU utilization
    const utilPercent = parseFloat(gpu.gpu_utilization);
    document.getElementById('gpu-util-percent').textContent = gpu.gpu_utilization;
    document.getElementById('gpu-util-bar').style.width = `${utilPercent}%`;
    
    // GPU temperature
    document.getElementById('gpu-temp').textContent = gpu.temperature;
    
    // Set temperature color based on value
    const tempValue = parseFloat(gpu.temperature);
    let tempColorClass = 'text-green-400';
    if (tempValue > 70) {
        tempColorClass = 'text-red-500';
    } else if (tempValue > 60) {
        tempColorClass = 'text-yellow-500';
    }
    document.getElementById('gpu-temp').className = `text-3xl font-bold ${tempColorClass}`;
}

// Update memory information
function updateMemoryInfo(memory) {
    // RAM usage
    document.getElementById('ram-percent').textContent = `${memory.percentage.toFixed(1)}%`;
    document.getElementById('ram-usage-bar').style.width = `${memory.percentage}%`;
    document.getElementById('ram-used').textContent = memory.used;
    document.getElementById('ram-total').textContent = memory.total;
    document.getElementById('ram-available').textContent = memory.available;
    document.getElementById('ram-used-detail').textContent = memory.used;
    
    // Swap usage
    document.getElementById('swap-percent').textContent = `${memory.swap_percentage.toFixed(1)}%`;
    document.getElementById('swap-usage-bar').style.width = `${memory.swap_percentage}%`;
    document.getElementById('swap-used').textContent = memory.swap_used;
    document.getElementById('swap-total').textContent = memory.swap_total;
    document.getElementById('swap-free').textContent = memory.swap_free;
    document.getElementById('swap-used-detail').textContent = memory.swap_used;
    
    // Update color of the bars based on usage
    const ramUsageBar = document.getElementById('ram-usage-bar');
    if (memory.percentage < 50) {
        ramUsageBar.className = "bg-gradient-to-r from-green-400 to-teal-500 h-3 rounded-full transition-all duration-500";
    } else if (memory.percentage < 80) {
        ramUsageBar.className = "bg-gradient-to-r from-yellow-400 to-orange-500 h-3 rounded-full transition-all duration-500";
    } else {
        ramUsageBar.className = "bg-gradient-to-r from-orange-500 to-red-600 h-3 rounded-full transition-all duration-500";
    }
    
    const swapUsageBar = document.getElementById('swap-usage-bar');
    if (memory.swap_percentage < 50) {
        swapUsageBar.className = "bg-gradient-to-r from-teal-400 to-cyan-500 h-3 rounded-full transition-all duration-500";
    } else if (memory.swap_percentage < 80) {
        swapUsageBar.className = "bg-gradient-to-r from-yellow-400 to-orange-500 h-3 rounded-full transition-all duration-500";
    } else {
        swapUsageBar.className = "bg-gradient-to-r from-orange-500 to-red-600 h-3 rounded-full transition-all duration-500";
    }
}

// Update disk information
function updateDiskInfo(disk) {
    // Disk partitions
    const partitionsContainer = document.getElementById('disk-partitions');
    partitionsContainer.innerHTML = '';
    
    disk.partitions.forEach(partition => {
        const partitionElement = document.createElement('div');
        partitionElement.className = 'mb-3';
        
        let colorClass = 'text-green-400';
        if (partition.percentage > 80) {
            colorClass = 'text-red-500';
        } else if (partition.percentage > 60) {
            colorClass = 'text-yellow-500';
        }
        
        partitionElement.innerHTML = `
            <div class="flex justify-between items-center mb-1">
                <span class="text-gray-300">${partition.mountpoint} (${partition.device})</span>
                <span class="${colorClass}">${partition.percentage}%</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
                <div class="bg-amber-500 h-2 rounded-full" style="width: ${partition.percentage}%"></div>
            </div>
            <div class="flex justify-between text-xs mt-1">
                <span>Used: ${partition.used}</span>
                <span>Free: ${partition.free}</span>
                <span>Total: ${partition.total_size}</span>
            </div>
        `;
        partitionsContainer.appendChild(partitionElement);
    });
    
    // Disk I/O
    if (disk.disk_io.status) {
        document.getElementById('disk-read').textContent = 'N/A';
        document.getElementById('disk-write').textContent = 'N/A';
    } else {
        document.getElementById('disk-read').textContent = disk.disk_io.read_since_boot;
        document.getElementById('disk-write').textContent = disk.disk_io.write_since_boot;
    }
}

// Update network information
function updateNetworkInfo(network) {
    // Network interfaces
    const interfacesContainer = document.getElementById('network-interfaces');
    interfacesContainer.innerHTML = '';
    
    network.interfaces.forEach(iface => {
        const ifaceElement = document.createElement('div');
        ifaceElement.className = 'bg-gray-700 p-3 rounded mb-2';
        ifaceElement.innerHTML = `
            <div class="flex justify-between items-center">
                <span class="font-semibold">${iface.interface}</span>
                <span class="text-sm text-green-400">${iface.ip}</span>
            </div>
            <div class="text-xs text-gray-400 mt-1">
                <div>Netmask: ${iface.netmask}</div>
                <div>Broadcast: ${iface.broadcast || 'N/A'}</div>
            </div>
        `;
        interfacesContainer.appendChild(ifaceElement);
    });
    
    // Network I/O
    document.getElementById('net-sent').textContent = network.io.bytes_sent;
    document.getElementById('net-recv').textContent = network.io.bytes_received;
}

// Initialize the application
function initApp() {
    // Update the time immediately and then every second
    updateTime();
    setInterval(updateTime, 1000);
    
    // Fetch hardware info immediately and then every 3 seconds
    fetchHardwareInfo();
    setInterval(fetchHardwareInfo, 3000);
}

// Start the application when the page loads
document.addEventListener('DOMContentLoaded', initApp);