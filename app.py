from flask import Flask, render_template, jsonify, send_file
import os
from hardware_info import (
    get_cpu_info, get_gpu_info, get_memory_info,
    get_disk_info, get_network_info, get_system_info,
    get_system_health, get_power_info, get_performance_report
)
import json
from datetime import datetime
import psutil
from advanced_monitoring import AdvancedMonitoring
import threading

app = Flask(__name__)
advanced_monitor = AdvancedMonitoring()

# Start resource monitoring in background
advanced_monitor.start_resource_monitoring()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system')
def system_info():
    return jsonify(get_system_info())

@app.route('/api/cpu')
def cpu_info():
    return jsonify(get_cpu_info())

@app.route('/api/gpu')
def gpu_info():
    return jsonify(get_gpu_info())

@app.route('/api/memory')
def memory_info():
    return jsonify(get_memory_info())

@app.route('/api/disk')
def disk_info():
    return jsonify(get_disk_info())

@app.route('/api/network')
def network_info():
    return jsonify(get_network_info())

@app.route('/api/health')
def system_health():
    return jsonify(get_system_health())

@app.route('/api/power')
def power_info():
    return jsonify(get_power_info())

@app.route('/api/performance')
def performance_report():
    return jsonify(get_performance_report())

# New endpoints for advanced monitoring
@app.route('/api/network/packets')
def network_packets():
    return jsonify(advanced_monitor.get_network_packet_stats())

@app.route('/api/network/ports')
def network_ports():
    return jsonify(advanced_monitor.get_port_scan())

@app.route('/api/process/tree')
def process_tree():
    return jsonify(advanced_monitor.get_process_tree())

@app.route('/api/security/status')
def security_status():
    return jsonify(advanced_monitor.get_security_status())

@app.route('/api/hardware/disk-health')
def disk_health():
    return jsonify(advanced_monitor.get_disk_health())

@app.route('/api/hardware/fan-speed')
def fan_speed():
    return jsonify(advanced_monitor.get_fan_speed())

@app.route('/api/performance/cpu-profile')
def cpu_profile():
    return jsonify(advanced_monitor.get_cpu_profile())

@app.route('/api/performance/memory-profile')
def memory_profile():
    return jsonify(advanced_monitor.get_memory_profile())

@app.route('/api/system/startup')
def startup_programs():
    return jsonify(advanced_monitor.get_startup_programs())

@app.route('/api/system/optimization')
def optimization_tips():
    return jsonify(advanced_monitor.get_optimization_tips())

@app.route('/api/system/resource-history')
def resource_history():
    return jsonify(advanced_monitor.get_resource_history())

@app.route('/api/hardware_info')
def hardware_info():
    return jsonify({
        "cpu": get_cpu_info(),
        "gpu": get_gpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "network": get_network_info(),
        "system": get_system_info(),
        "power": get_power_info()
    })

@app.route('/api/generate_report')
def generate_report():
    report = get_performance_report()
    
    # Create reports directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"performance_report_{timestamp}.json"
    filepath = os.path.join('reports', filename)
    
    # Save report to file
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=4)
    
    return jsonify({
        "status": "success",
        "message": "Report generated successfully",
        "filename": filename,
        "report": report
    })

@app.route('/api/download_report/<filename>')
def download_report(filename):
    return send_file(
        os.path.join('reports', filename),
        as_attachment=True,
        download_name=filename
    )

def get_disk_health():
    try:
        # Get disk partitions
        partitions = psutil.disk_partitions()
        disk_info = []
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                # Calculate disk health percentage based on various factors
                # This is a simplified example - in reality, you'd want to use SMART data
                health_percent = 100 - (usage.percent * 0.5)  # Example calculation
                
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': format_size(usage.total),
                    'used': format_size(usage.used),
                    'free': format_size(usage.free),
                    'usage_percent': usage.percent,
                    'status': 'Healthy' if health_percent >= 90 else 'Warning' if health_percent >= 70 else 'Critical',
                    'health_percent': round(health_percent, 1)
                })
            except:
                continue
                
        return disk_info
    except Exception as e:
        print(f"Error getting disk health: {str(e)}")
        return []

if __name__ == '__main__':
    # Make sure templates and static directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Create template file if it doesn't exist
    template_path = os.path.join('templates', 'index.html')
    if not os.path.exists(template_path):
        with open(template_path, 'w') as f:
            f.write(INDEX_HTML)
    
    # Create script file if it doesn't exist
    script_path = os.path.join('static', 'js', 'script.js')
    if not os.path.exists(script_path):
        with open(script_path, 'w') as f:
            f.write(SCRIPT_JS)
    
    print("Starting Hardware Monitor on http://127.0.0.1:5000")
    app.run(debug=True)