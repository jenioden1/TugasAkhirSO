from flask import Flask, render_template, jsonify
import os
from hardware_info import (
    get_cpu_info, get_gpu_info, get_memory_info,
    get_disk_info, get_network_info, get_system_info
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hardware_info')
def hardware_info():
    info = {
        "cpu": get_cpu_info(),
        "gpu": get_gpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "network": get_network_info(),
        "system": get_system_info()
    }
    return jsonify(info)

if __name__ == '__main__':
    # Make sure templates and static directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
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