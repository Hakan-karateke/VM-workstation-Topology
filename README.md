# SDN Testbed Setup Guide

This repository contains scripts and documentation to set up a Software-Defined Networking (SDN) testbed with attack generation capabilities, as described in the research paper.

## Topology Overview

The testbed consists of:

1. **SDN Controller (ONOS)** - Controls the network infrastructure
2. **OVS Switch with Mininet** - Implements virtual network infrastructure
3. **Attack Network (Kali Linux)** - Source of various attacks
4. **Target Network (Metasploitable 2)** - Vulnerable hosts and services
5. **Mininet Hosts** - Four virtual hosts within the Mininet environment

## Network Architecture

The SDN testbed is organized into four separate subnets:
- VMnet1 (192.168.8.0/24) - SDN Controller network
- VMnet2 (192.168.3.0/24) - Target network (Metasploitable 2)
- VMnet3 (200.175.2.0/24) - Attack network (Kali Linux)
- VMnet4 (192.168.20.0/24) - Mininet hosts network

## Prerequisites

1. VMware Workstation
2. 4 Virtual Machines:
   - Ubuntu VM for ONOS controller
   - Ubuntu VM for OVS switch and Mininet
   - Kali Linux VM for attacker machine
   - Metasploitable 2 VM for target machine

## Setup Instructions

### Step 1: Configure VMware Networks

Follow the instructions in `1_vmware_network_setup.txt` to configure the VMware virtual networks.

### Step 2: Set up the ONOS Controller

1. Copy `2_onos_setup.sh` to the ONOS VM
2. Make it executable: `chmod +x 2_onos_setup.sh`
3. Run the script: `./2_onos_setup.sh`
4. Verify ONOS is running by accessing the web UI at `http://192.168.8.128:8181/onos/ui`

### Step 3: Set up the OVS Switch and Mininet

1. Copy `3_ovs_setup.sh` to the OVS/Mininet VM
2. Make it executable: `chmod +x 3_ovs_setup.sh`
3. Run the script: `./3_ovs_setup.sh`
4. Verify OVS bridges are created and connected to the controller

### Step 4: Set up Mininet Hosts

1. Copy `4_mininet_topology.py` to the OVS/Mininet VM
2. Run the script: `sudo python3 4_mininet_topology.py`
3. Verify hosts are created and connected

### Step 5: Test Connectivity

Use the Mininet CLI to test connectivity between all hosts and networks:
```
h1 ping h2
h1 ping h3
h1 ping h4
h1 ping 192.168.3.130  # Metasploitable 2 VM
h1 ping 200.175.2.130  # Kali Linux VM
```

## Attack Scenarios

The testbed supports various attack scenarios as described in the research paper:

1. **DoS Attacks**
   - TCP-ACK flood, UDP flood, HTTP flood, Slow-rate attacks
   - Run with: `./5_dos_attacks.sh <target_ip> <attack_type>`

2. **DDoS Attacks**
   - TCP-SYN flood, UDP flood, ICMP flood
   - Run with: `./6_ddos_attacks.sh <target_ip> <attack_type>`

3. **Web Application Attacks**
   - SQL Injection, XSS
   - Run with: `./7_web_attacks.sh <target_ip> <attack_type>`

4. **Probe/Scanning**
   - Version scan, port scan, service discovery, vulnerability scanning
   - Run with: `./8_probe_scanning.sh <target_ip> <scan_type>`

5. **Botnet Attacks**
   - Botnet simulation using Ares
   - Run with: `./9_botnet_attack.sh <c2_server_ip>`

6. **U2R (Exploitation) Attacks**
   - Exploiting vulnerable services (vsftpd, distcc, UnrealIRCd, Samba)
   - Run with: `./10_u2r_exploitation.sh <target_ip> <service>`

## Troubleshooting

If you encounter connectivity issues:

1. Verify IP addresses and subnet masks
2. Check bridge configurations on the OVS switch
3. Ensure IP forwarding is enabled: `sudo sysctl -w net.ipv4.ip_forward=1`
4. Verify ONOS controller is running and accessible
5. Check OVS connections to controller: `sudo ovs-vsctl show`
