#!/usr/bin/env python

"""
SCADA Network Visualization
- Visualizes the SCADA network topology
- Shows traffic flows and potential attacks in real-time
- Provides a web interface for monitoring the network
"""

import os
import time
import json
import threading
import argparse
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from scapy.all import *

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"visualizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Create Flask app
app = Flask(__name__,
           static_folder="static",
           template_folder="templates")

# Define the SCADA network topology
TOPOLOGY = {
    "controllers": [{
        "id": "c0",
        "name": "SDN Controller",
        "ip": "127.0.0.1",
        "port": 6633,
        "type": "controller"
    }],
    "switches": [
        {
            "id": "s1", 
            "name": "Main Switch",
            "type": "switch"
        },
        {
            "id": "s2", 
            "name": "SCADA Network Switch",
            "type": "switch"
        }
    ],
    "hosts": [
        {
            "id": "kali1",
            "name": "Kali1 (Victim)",
            "ip": "10.0.0.10",
            "mac": "00:00:00:00:00:10",
            "type": "victim"
        },
        {
            "id": "mininet1",
            "name": "Mininet1 (Attacker)",
            "ip": "10.0.0.20",
            "mac": "00:00:00:00:00:20",
            "type": "attacker"
        },
        {
            "id": "kali2",
            "name": "Kali2 (Modbus Server)",
            "ip": "10.0.0.30",
            "mac": "00:00:00:00:00:30",
            "type": "scada_server"
        },
        {
            "id": "mininet2",
            "name": "Mininet2 (Modbus Client)",
            "ip": "10.0.0.40",
            "mac": "00:00:00:00:00:40",
            "type": "scada_client"
        },
        {
            "id": "scada1",
            "name": "SCADA Device 1",
            "ip": "10.0.0.50",
            "mac": "00:00:00:00:00:50",
            "type": "scada_device"
        },
        {
            "id": "scada2",
            "name": "SCADA Device 2",
            "ip": "10.0.0.60",
            "mac": "00:00:00:00:00:60",
            "type": "scada_device"
        }
    ],
    "links": [
        {"source": "kali1", "target": "s1"},
        {"source": "mininet1", "target": "s1"},
        {"source": "s1", "target": "s2"},
        {"source": "kali2", "target": "s2"},
        {"source": "mininet2", "target": "s2"},
        {"source": "scada1", "target": "s2"},
        {"source": "scada2", "target": "s2"},
        {"source": "c0", "target": "s1"},
        {"source": "c0", "target": "s2"}
    ]
}

# Store network traffic data
traffic_data = {
    "flows": [],
    "stats": {
        "total_packets": 0,
        "tcp_packets": 0,
        "udp_packets": 0,
        "icmp_packets": 0,
        "http_packets": 0,
        "modbus_packets": 0,
        "attacks": []
    },
    "history": {
        "timestamps": [],
        "pps": [],
        "tcp_pps": [],
        "udp_pps": [],
        "modbus_pps": []
    }
}

# Store device status information
device_status = {
    "kali1": {"status": "online", "last_seen": time.time()},
    "mininet1": {"status": "online", "last_seen": time.time()},
    "kali2": {"status": "online", "last_seen": time.time()},
    "mininet2": {"status": "online", "last_seen": time.time()},
    "scada1": {"status": "online", "last_seen": time.time()},
    "scada2": {"status": "online", "last_seen": time.time()}
}

# Traffic capture settings
capture_running = False
capture_thread = None

# Attack detection thresholds
THRESHOLDS = {
    'pps': 1000,         # Packets per second
    'tcp_syn_rate': 500, # TCP SYN packets per second
    'icmp_rate': 500,    # ICMP packets per second
    'udp_rate': 800,     # UDP packets per second
    'tcp_ack_rate': 800  # TCP ACK packets per second
}

# Generate HTML templates directory and files
def generate_templates():
    """Generate the necessary template files for the web interface"""
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    # Create index.html
    index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCADA Network Visualization</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.0/css/bootstrap.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.6.0/js/bootstrap.bundle.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            padding-top: 20px;
            background-color: #f5f5f5;
        }
        .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        #topology-container {
            background-color: #fff;
            border-radius: 5px;
            height: 500px;
        }
        .node circle {
            stroke: #fff;
            stroke-width: 2px;
        }
        .node text {
            font-size: 12px;
            font-weight: bold;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
        }
        .traffic-flow {
            stroke-opacity: 0.8;
            stroke-linecap: round;
        }
        .controller { fill: #e41a1c; }
        .switch { fill: #4292c6; }
        .victim { fill: #41ab5d; }
        .attacker { fill: #ff7f00; }
        .scada_server { fill: #984ea3; }
        .scada_client { fill: #a65628; }
        .scada_device { fill: #f781bf; }
        
        .status-online { color: #41ab5d; }
        .status-offline { color: #e41a1c; }
        .status-unknown { color: #999999; }
        
        .alert-container {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .table-fixed {
            table-layout: fixed;
        }
        .table-fixed td {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">SCADA Network Visualization</h1>
            </div>
        </div>
        
        <div class="row">
            <!-- Topology Visualization -->
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">Network Topology</h4>
                    </div>
                    <div class="card-body p-0">
                        <div id="topology-container"></div>
                    </div>
                </div>
                
                <!-- Traffic Statistics -->
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h4 class="mb-0">Traffic Statistics</h4>
                    </div>
                    <div class="card-body">
                        <div id="traffic-chart"></div>
                    </div>
                </div>
            </div>
            
            <!-- Right Column -->
            <div class="col-md-4">
                <!-- Device Status -->
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h4 class="mb-0">Device Status</h4>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered table-fixed">
                                <thead>
                                    <tr>
                                        <th>Device</th>
                                        <th>IP Address</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody id="device-status">
                                    <!-- Populated by JavaScript -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <!-- Attack Alerts -->
                <div class="card">
                    <div class="card-header bg-danger text-white">
                        <h4 class="mb-0">Attack Alerts</h4>
                    </div>
                    <div class="card-body p-0">
                        <div class="alert-container" id="attack-alerts">
                            <!-- Populated by JavaScript -->
                            <div class="p-3 text-center text-muted">No attacks detected</div>
                        </div>
                    </div>
                </div>
                
                <!-- Traffic Summary -->
                <div class="card">
                    <div class="card-header bg-warning">
                        <h4 class="mb-0">Traffic Summary</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <div class="card bg-light mb-2">
                                    <div class="card-body py-2 text-center">
                                        <h5 class="mb-0"><span id="total-pps">0</span> pps</h5>
                                        <small>Packets/sec</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="card bg-light mb-2">
                                    <div class="card-body py-2 text-center">
                                        <h5 class="mb-0"><span id="total-packets">0</span></h5>
                                        <small>Total Packets</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-4">
                                <div class="card bg-light mb-0">
                                    <div class="card-body py-2 text-center">
                                        <h6 class="mb-0"><span id="tcp-packets">0</span></h6>
                                        <small>TCP</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card bg-light mb-0">
                                    <div class="card-body py-2 text-center">
                                        <h6 class="mb-0"><span id="udp-packets">0</span></h6>
                                        <small>UDP</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card bg-light mb-0">
                                    <div class="card-body py-2 text-center">
                                        <h6 class="mb-0"><span id="modbus-packets">0</span></h6>
                                        <small>Modbus</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Topology visualization
        function renderTopology(topology, trafficData) {
            const width = document.getElementById('topology-container').offsetWidth;
            const height = document.getElementById('topology-container').offsetHeight;
            
            // Clear previous visualization
            d3.select("#topology-container").html("");
            
            const svg = d3.select("#topology-container")
                .append("svg")
                .attr("width", width)
                .attr("height", height);
                
            // Create arrow markers for links
            svg.append("defs").append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 20)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#999");
            
            // Combine all nodes
            const allNodes = [
                ...topology.controllers,
                ...topology.switches,
                ...topology.hosts
            ];
            
            // Create force simulation
            const simulation = d3.forceSimulation(allNodes)
                .force("link", d3.forceLink(topology.links)
                    .id(d => d.id)
                    .distance(100))
                .force("charge", d3.forceManyBody().strength(-400))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(60));
            
            // Create links
            const link = svg.append("g")
                .selectAll("line")
                .data(topology.links)
                .enter()
                .append("line")
                .attr("class", "link");
            
            // Create traffic flow lines (initially hidden)
            const trafficFlow = svg.append("g")
                .selectAll("line")
                .data(trafficData.flows)
                .enter()
                .append("line")
                .attr("class", "traffic-flow")
                .style("stroke", d => d.attack ? "red" : "green")
                .style("stroke-width", d => d.volume / 10 + 1);
            
            // Create nodes
            const node = svg.append("g")
                .selectAll("g")
                .data(allNodes)
                .enter()
                .append("g")
                .attr("class", "node")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
                    
            // Add circles to nodes
            node.append("circle")
                .attr("r", d => {
                    switch (d.type) {
                        case "controller": return 15;
                        case "switch": return 12;
                        default: return 10;
                    }
                })
                .attr("class", d => d.type);
                
            // Add labels to nodes
            node.append("text")
                .attr("dy", -15)
                .attr("text-anchor", "middle")
                .text(d => d.name || d.id);
            
            // Update positions on each tick
            simulation.on("tick", () => {
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                    
                trafficFlow
                    .attr("x1", d => findNode(d.source).x)
                    .attr("y1", d => findNode(d.source).y)
                    .attr("x2", d => findNode(d.target).x)
                    .attr("y2", d => findNode(d.target).y);
                
                node.attr("transform", d => `translate(${d.x},${d.y})`);
            });
            
            // Helper function to find node by id
            function findNode(id) {
                return allNodes.find(n => n.id === id) || { x: width/2, y: height/2 };
            }
            
            // Drag functions
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
        }
        
        // Traffic chart
        function renderTrafficChart(data) {
            const chartData = [
                {
                    x: data.history.timestamps,
                    y: data.history.pps,
                    type: 'scatter',
                    name: 'Total pps'
                },
                {
                    x: data.history.timestamps,
                    y: data.history.tcp_pps,
                    type: 'scatter',
                    name: 'TCP pps'
                },
                {
                    x: data.history.timestamps,
                    y: data.history.udp_pps,
                    type: 'scatter',
                    name: 'UDP pps'
                },
                {
                    x: data.history.timestamps,
                    y: data.history.modbus_pps,
                    type: 'scatter',
                    name: 'Modbus pps'
                }
            ];
            
            const layout = {
                height: 250,
                margin: {
                    l: 40,
                    r: 10,
                    b: 30,
                    t: 10,
                    pad: 4
                },
                showlegend: true,
                legend: {
                    orientation: 'h',
                    x: 0,
                    y: 1.1
                },
                xaxis: {
                    showgrid: false,
                    zeroline: false
                }
            };
            
            Plotly.newPlot('traffic-chart', chartData, layout, {responsive: true});
        }
        
        // Update device status table
        function updateDeviceStatus(devices) {
            const tbody = document.getElementById('device-status');
            tbody.innerHTML = '';
            
            Object.keys(devices).forEach(id => {
                const device = topology.hosts.find(h => h.id === id) || { name: id, ip: 'Unknown' };
                const status = devices[id];
                
                const tr = document.createElement('tr');
                
                const tdName = document.createElement('td');
                tdName.textContent = device.name;
                tr.appendChild(tdName);
                
                const tdIp = document.createElement('td');
                tdIp.textContent = device.ip;
                tr.appendChild(tdIp);
                
                const tdStatus = document.createElement('td');
                tdStatus.innerHTML = `<span class="status-${status.status}">${status.status}</span>`;
                tr.appendChild(tdStatus);
                
                tbody.appendChild(tr);
            });
        }
        
        // Update attack alerts
        function updateAttackAlerts(attacks) {
            const alertContainer = document.getElementById('attack-alerts');
            
            if (attacks.length === 0) {
                alertContainer.innerHTML = '<div class="p-3 text-center text-muted">No attacks detected</div>';
                return;
            }
            
            alertContainer.innerHTML = '';
            
            attacks.forEach(attack => {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger m-2 mb-2';
                alertDiv.innerHTML = `
                    <strong>${new Date(attack.timestamp).toLocaleTimeString()}</strong>
                    <p class="mb-0">${attack.message}</p>
                `;
                alertContainer.appendChild(alertDiv);
            });
        }
        
        // Update traffic summary
        function updateTrafficSummary(stats) {
            document.getElementById('total-pps').textContent = stats.pps.toFixed(0);
            document.getElementById('total-packets').textContent = stats.total_packets.toLocaleString();
            document.getElementById('tcp-packets').textContent = stats.tcp_packets.toLocaleString();
            document.getElementById('udp-packets').textContent = stats.udp_packets.toLocaleString();
            document.getElementById('modbus-packets').textContent = stats.modbus_packets.toLocaleString();
        }
        
        // Fetch data and update visualizations
        function updateData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    // Update visualizations
                    renderTopology(topology, data);
                    renderTrafficChart(data);
                    updateDeviceStatus(data.devices);
                    updateAttackAlerts(data.stats.attacks);
                    updateTrafficSummary(data.stats);
                })
                .catch(error => console.error('Error fetching data:', error));
        }
        
        // Initial data
        const topology = {{ topology|safe }};
        
        // Initial render
        document.addEventListener('DOMContentLoaded', () => {
            renderTopology(topology, { flows: [] });
            updateData();
            
            // Update data every 2 seconds
            setInterval(updateData, 2000);
        });
    </script>
</body>
</html>
    """
    
    with open("templates/index.html", "w") as f:
        f.write(index_html)
    
    logging.info("Generated template files")

# Flask routes
@app.route('/')
def index():
    """Render the main visualization page"""
    return render_template('index.html', topology=json.dumps(TOPOLOGY))

@app.route('/api/data')
def api_data():
    """Return current network data as JSON"""
    # Add current timestamp to history
    if len(traffic_data['history']['timestamps']) >= 50:
        # Remove oldest data point if we have more than 50
        traffic_data['history']['timestamps'] = traffic_data['history']['timestamps'][1:]
        traffic_data['history']['pps'] = traffic_data['history']['pps'][1:]
        traffic_data['history']['tcp_pps'] = traffic_data['history']['tcp_pps'][1:]
        traffic_data['history']['udp_pps'] = traffic_data['history']['udp_pps'][1:]
        traffic_data['history']['modbus_pps'] = traffic_data['history']['modbus_pps'][1:]
    
    # Add current timestamp
    current_time = time.strftime('%H:%M:%S')
    traffic_data['history']['timestamps'].append(current_time)
    
    # Calculate current rates (random values for demo)
    pps = traffic_data['stats']['total_packets'] / 10 if not capture_running else random.randint(100, 2000)
    tcp_pps = traffic_data['stats']['tcp_packets'] / 10 if not capture_running else random.randint(50, 1000)
    udp_pps = traffic_data['stats']['udp_packets'] / 10 if not capture_running else random.randint(20, 500)
    modbus_pps = traffic_data['stats']['modbus_packets'] / 10 if not capture_running else random.randint(5, 100)
    
    # Add to history
    traffic_data['history']['pps'].append(pps)
    traffic_data['history']['tcp_pps'].append(tcp_pps)
    traffic_data['history']['udp_pps'].append(udp_pps)
    traffic_data['history']['modbus_pps'].append(modbus_pps)
    
    # Update stats
    traffic_data['stats']['pps'] = pps
    
    # Return complete data
    return jsonify({
        'flows': traffic_data['flows'],
        'stats': traffic_data['stats'],
        'history': traffic_data['history'],
        'devices': device_status
    })

def process_packet(pkt):
    """Process captured packets and update traffic data"""
    global traffic_data, device_status
    
    try:
        # Only process IP packets
        if IP in pkt:
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            
            # Update total packet count
            traffic_data['stats']['total_packets'] += 1
            
            # Find source and destination hosts
            src_host = next((h['id'] for h in TOPOLOGY['hosts'] if h['ip'] == src_ip), None)
            dst_host = next((h['id'] for h in TOPOLOGY['hosts'] if h['ip'] == dst_ip), None)
            
            # Update device status based on traffic
            if src_host and src_host in device_status:
                device_status[src_host]['status'] = 'online'
                device_status[src_host]['last_seen'] = time.time()
            
            if dst_host and dst_host in device_status:
                device_status[dst_host]['status'] = 'online'
                device_status[dst_host]['last_seen'] = time.time()
            
            # Process TCP packets
            if TCP in pkt:
                traffic_data['stats']['tcp_packets'] += 1
                
                # Check for Modbus traffic (port 502)
                if pkt[TCP].dport == 502 or pkt[TCP].sport == 502:
                    traffic_data['stats']['modbus_packets'] += 1
                
                # Check for HTTP traffic
                if pkt[TCP].dport in [80, 8080, 443] or pkt[TCP].sport in [80, 8080, 443]:
                    traffic_data['stats']['http_packets'] += 1
                
                # Detect potential TCP SYN flood
                if pkt[TCP].flags & 0x02:  # SYN flag
                    syn_rate = traffic_data['stats']['tcp_packets'] / 10  # Approximate rate
                    if syn_rate > THRESHOLDS['tcp_syn_rate']:
                        # Add attack alert
                        traffic_data['stats']['attacks'].append({
                            'timestamp': time.time() * 1000,  # JavaScript timestamp
                            'message': f"Possible TCP SYN Flood detected ({syn_rate:.2f} SYNs/sec)",
                            'type': 'syn_flood',
                            'source': src_host or src_ip,
                            'target': dst_host or dst_ip
                        })
                        
                        # Add attack flow to visualization
                        add_traffic_flow(src_host or 'external', dst_host or 'external', 'tcp', True)
            
            # Process UDP packets
            elif UDP in pkt:
                traffic_data['stats']['udp_packets'] += 1
                
                # Detect potential UDP flood
                udp_rate = traffic_data['stats']['udp_packets'] / 10  # Approximate rate
                if udp_rate > THRESHOLDS['udp_rate']:
                    # Add attack alert
                    traffic_data['stats']['attacks'].append({
                        'timestamp': time.time() * 1000,  # JavaScript timestamp
                        'message': f"Possible UDP Flood detected ({udp_rate:.2f} UDP/sec)",
                        'type': 'udp_flood',
                        'source': src_host or src_ip,
                        'target': dst_host or dst_ip
                    })
                    
                    # Add attack flow to visualization
                    add_traffic_flow(src_host or 'external', dst_host or 'external', 'udp', True)
            
            # Process ICMP packets
            elif ICMP in pkt:
                traffic_data['stats']['icmp_packets'] += 1
                
                # Detect potential ICMP flood
                icmp_rate = traffic_data['stats']['icmp_packets'] / 10  # Approximate rate
                if icmp_rate > THRESHOLDS['icmp_rate']:
                    # Add attack alert
                    traffic_data['stats']['attacks'].append({
                        'timestamp': time.time() * 1000,  # JavaScript timestamp
                        'message': f"Possible ICMP Flood detected ({icmp_rate:.2f} ICMP/sec)",
                        'type': 'icmp_flood',
                        'source': src_host or src_ip,
                        'target': dst_host or dst_ip
                    })
                    
                    # Add attack flow to visualization
                    add_traffic_flow(src_host or 'external', dst_host or 'external', 'icmp', True)
            
            # Add normal traffic flow if hosts are identified
            if src_host and dst_host:
                protocol = 'tcp' if TCP in pkt else 'udp' if UDP in pkt else 'icmp' if ICMP in pkt else 'other'
                add_traffic_flow(src_host, dst_host, protocol, False)
        
    except Exception as e:
        logging.error(f"Error processing packet: {e}")

def add_traffic_flow(src, dst, protocol, is_attack=False):
    """Add a traffic flow to the visualization data"""
    global traffic_data
    
    # Limit the number of flows to prevent performance issues
    if len(traffic_data['flows']) >= 20:
        # Remove oldest flow
        traffic_data['flows'].pop(0)
    
    # Add new flow
    traffic_data['flows'].append({
        'source': src,
        'target': dst,
        'protocol': protocol,
        'attack': is_attack,
        'timestamp': time.time(),
        'volume': random.randint(1, 10)  # Random volume for visualization
    })

def update_device_status():
    """Update device status based on last seen time"""
    global device_status
    
    current_time = time.time()
    timeout = 30  # 30 seconds timeout
    
    for device_id, status in device_status.items():
        if current_time - status['last_seen'] > timeout:
            status['status'] = 'offline'

def packet_capture(interface=None, filter_exp=None):
    """Capture packets from the network"""
    global capture_running
    
    capture_running = True
    logging.info(f"Starting packet capture on interface {interface or 'default'}")
    
    try:
        if interface:
            if filter_exp:
                sniff(iface=interface, filter=filter_exp, prn=process_packet, store=0)
            else:
                sniff(iface=interface, prn=process_packet, store=0)
        else:
            if filter_exp:
                sniff(filter=filter_exp, prn=process_packet, store=0)
            else:
                sniff(prn=process_packet, store=0)
    except Exception as e:
        logging.error(f"Error in packet capture: {e}")
    
    capture_running = False

def simulate_traffic():
    """Simulate traffic for testing the visualization"""
    global traffic_data, device_status
    
    logging.info("Starting traffic simulation")
    
    while True:
        try:
            # Update packet stats
            traffic_data['stats']['total_packets'] += random.randint(50, 200)
            traffic_data['stats']['tcp_packets'] += random.randint(30, 150)
            traffic_data['stats']['udp_packets'] += random.randint(10, 50)
            traffic_data['stats']['http_packets'] += random.randint(5, 30)
            traffic_data['stats']['modbus_packets'] += random.randint(1, 10)
            
            # Randomly generate traffic flows
            hosts = [h['id'] for h in TOPOLOGY['hosts']]
            
            for _ in range(2):  # Add 2 flows per update
                src = random.choice(hosts)
                dst = random.choice(hosts)
                
                if src != dst:
                    protocol = random.choice(['tcp', 'udp', 'icmp'])
                    is_attack = random.random() < 0.05  # 5% chance of being an attack
                    
                    # Add flow
                    add_traffic_flow(src, dst, protocol, is_attack)
                    
                    # If it's an attack, add an alert
                    if is_attack:
                        attack_type = random.choice(['tcp_syn_flood', 'udp_flood', 'icmp_flood', 'http_flood'])
                        traffic_data['stats']['attacks'].append({
                            'timestamp': time.time() * 1000,
                            'message': f"Simulated {attack_type.upper()} attack detected",
                            'type': attack_type,
                            'source': src,
                            'target': dst
                        })
            
            # Limit the number of attacks shown
            if len(traffic_data['stats']['attacks']) > 10:
                traffic_data['stats']['attacks'] = traffic_data['stats']['attacks'][-10:]
            
            # Update device status
            update_device_status()
            
            # Sleep before next update
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"Error in traffic simulation: {e}")
            time.sleep(5)

def run_visualizer(interface=None, filter_exp=None, port=8080, simulate=False):
    """Run the network visualizer"""
    # Generate template files
    generate_templates()
    
    # Start packet capture thread if not in simulation mode
    if not simulate:
        global capture_thread
        capture_thread = threading.Thread(target=packet_capture, args=(interface, filter_exp))
        capture_thread.daemon = True
        capture_thread.start()
    else:
        # Start simulation thread
        sim_thread = threading.Thread(target=simulate_traffic)
        sim_thread.daemon = True
        sim_thread.start()
    
    # Start the device status update thread
    status_thread = threading.Thread(target=lambda: (
        time.sleep(10),  # Initial delay
        update_device_status(),
        time.sleep(5)  # Update every 5 seconds
    ))
    status_thread.daemon = True
    status_thread.start()
    
    # Start the Flask app
    logging.info(f"Starting web interface on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='SCADA Network Visualizer')
    parser.add_argument('-i', '--interface', help='Network interface to monitor')
    parser.add_argument('-f', '--filter', help='BPF filter expression')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Web server port (default: 8080)')
    parser.add_argument('-s', '--simulate', action='store_true', help='Simulate traffic (for testing)')
    parser.add_argument('--tcp', action='store_true', help='Monitor TCP traffic only')
    parser.add_argument('--udp', action='store_true', help='Monitor UDP traffic only')
    parser.add_argument('--icmp', action='store_true', help='Monitor ICMP traffic only')
    parser.add_argument('--modbus', action='store_true', help='Monitor Modbus traffic only')
    
    args = parser.parse_args()
    
    # Build filter expression
    filter_exp = args.filter
    if args.tcp:
        filter_exp = "tcp" if not filter_exp else f"{filter_exp} and tcp"
    if args.udp:
        filter_exp = "udp" if not filter_exp else f"{filter_exp} and udp"
    if args.icmp:
        filter_exp = "icmp" if not filter_exp else f"{filter_exp} and icmp"
    if args.modbus:
        modbus_exp = "tcp port 502"
        filter_exp = modbus_exp if not filter_exp else f"{filter_exp} and {modbus_exp}"
    
    # Start visualizer
    run_visualizer(args.interface, filter_exp, args.port, args.simulate)
