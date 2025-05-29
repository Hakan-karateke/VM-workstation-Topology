# SCADA Network Topology and Attack Simulation

This repository contains scripts for setting up a SCADA (Supervisory Control and Data Acquisition) network topology in VMware Workstation with Mininet, as well as scripts for simulating various network attacks.

## Network Topology

The topology consists of 4 virtual machines:
- **Kali1**: Victim machine
- **Kali2**: Modbus Server
- **Kali3**: (Additional machine for monitoring/attacks)
- **Ubuntu**: Hosts the Mininet simulation

The Mininet topology includes:
- SDN Controller
- Two switches (s1 and s2)
- Multiple hosts including Modbus client and server

## File Structure

### Network Setup
- `scada_topology.py`: Creates the Mininet network topology
- `sdn_controller.py`: Ryu-based SDN controller
- `modbus_server.py`: Modbus TCP server for SCADA simulation
- `modbus_client.py`: Modbus TCP client that communicates with the server
- `setup.py`: Helper script for setting up dependencies and configurations
- `network_monitor.py`: Network traffic monitoring tool
- `visualizer.py`: Web-based network visualization tool

### Attack Scripts
- `tcp_ack_flood.py`: TCP-ACK flood attack
- `udp_flood.py`: UDP flood attack
- `http_flood.py`: HTTP flood attack
- `slow_rate.py`: Slow-rate attack
- `slowloris.py`: Slowloris attack
- `tcp_syn_flood.py`: TCP-SYN flood attack
- `icmp_flood.py`: ICMP Flood attack
- `sql_injection.py`: SQL Injection attack
- `port_scan.py`: Port scanning tool

## Setup Instructions

### 1. VMware Workstation Setup
1. Install VMware Workstation
2. Create 4 virtual machines:
   - Kali Linux (kali1) - Victim
   - Kali Linux (kali2) - Modbus Server
   - Kali Linux (kali3) - Additional machine
   - Ubuntu - For Mininet

3. Configure networking to allow communication between VMs

### 2. Using the Setup Helper Script
The setup script can help you configure the environment on each VM:

```bash
# Check and install dependencies
python3 setup.py --check

# Configure network settings
python3 setup.py --network

# Configure firewall rules
python3 setup.py --firewall

# Set script permissions
python3 setup.py --permissions

# Start Mininet (Ubuntu VM only)
python3 setup.py --start-mininet

# Start Modbus Server (Kali2 VM only)
python3 setup.py --start-modbus

# Or run all applicable setup steps
python3 setup.py --all
```

### 3. Manual Ubuntu VM Setup (Mininet Host)
If you prefer manual setup:

```bash
# Install Mininet
sudo apt-get update
sudo apt-get install mininet

# Install Ryu Controller
sudo apt-get install python3-pip
sudo pip3 install ryu

# Install Modbus dependencies
sudo pip3 install pymodbus

# Install network monitoring dependencies
sudo pip3 install scapy requests flask

# Copy scripts to Ubuntu VM
mkdir -p /home/ubuntu/scripts/
# Copy all scripts to this directory

# Set execution permissions
chmod +x /home/ubuntu/scripts/*.py
```

### 4. Start the Network Topology
```bash
# Start the SDN controller
sudo python3 /home/ubuntu/scripts/sdn_controller.py &

# Start the Mininet topology
sudo python3 /home/ubuntu/scripts/scada_topology.py
```

### 5. Start Network Monitoring
To monitor network traffic during attacks:

```bash
# Basic monitoring
sudo python3 network_monitor.py -i eth0

# Monitor specific protocols
sudo python3 network_monitor.py -i eth0 --tcp --modbus

# Monitor with visualization
sudo python3 visualizer.py -i eth0 -p 8080
```

Access the visualization at http://localhost:8080 in a web browser.

## Attack Simulations

### TCP-ACK Flood
```bash
sudo python3 tcp_ack_flood.py -t 10.0.0.10 -p 80 -d 30
```

### UDP Flood
```bash
sudo python3 udp_flood.py -t 10.0.0.10 -p 53 -d 30 -s 1024
```

### HTTP Flood
```bash
python3 http_flood.py -t http://10.0.0.10 -d 30 -n 10 -m GET
```

### Slow-Rate Attack
```bash
python3 slow_rate.py -t 10.0.0.10 -p 80 -s 150 -d 60
```

### Slowloris Attack
```bash
python3 slowloris.py -t 10.0.0.10 -p 80 -s 100 -d 60
```

### TCP-SYN Flood
```bash
sudo python3 tcp_syn_flood.py -t 10.0.0.10 -p 80 -d 30 -m distributed
```

### ICMP Flood
```bash
sudo python3 icmp_flood.py -t 10.0.0.10 -d 30 -s 56
```

### SQL Injection
```bash
python3 sql_injection.py -u http://10.0.0.10/login.php -p username
```

### Port Scan
```bash
sudo python3 port_scan.py -t 10.0.0.10 -p 1-1000 -s syn -b
```

## Monitoring & Visualization

### Network Monitor
The `network_monitor.py` script provides real-time monitoring of network traffic:

```bash
# Basic monitoring on default interface
sudo python3 network_monitor.py

# Monitor specific interface with filter
sudo python3 network_monitor.py -i eth0 -f "tcp port 502"

# Monitor specific protocols
sudo python3 network_monitor.py --tcp --modbus

# Set custom threshold for attack detection
sudo python3 network_monitor.py -t 2000  # 2000 packets/second threshold
```

### Network Visualizer
The `visualizer.py` script provides a web-based visualization of the network topology and traffic:

```bash
# Start the visualizer with traffic capture
sudo python3 visualizer.py -i eth0 -p 8080

# Start in simulation mode (for testing without actual traffic)
python3 visualizer.py -s -p 8080

# Monitor specific protocols
sudo python3 visualizer.py -i eth0 --tcp --modbus
```

Access the visualization at http://localhost:8080 in a web browser.

## Notes on Modbus Communication

The Modbus communication simulates a SCADA system where:
- Kali2 acts as the Modbus server (10.0.0.30)
- Mininet2 acts as the Modbus client (10.0.0.40)

The Modbus server simulates various process values:
- Temperature
- Pressure
- Flow rate
- Valve state

## Security Considerations

These scripts are intended for educational purposes and security testing in controlled environments only. Unauthorized use of these tools against systems without explicit permission is illegal and unethical.

## Requirements

- Python 3.6+
- Scapy
- PyModbus
- Requests
- BeautifulSoup4
- Flask (for visualization)
- Mininet
- Ryu Controller
