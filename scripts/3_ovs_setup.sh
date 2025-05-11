#!/bin/bash
# OVS Switch & Mininet Setup Script
# For VM-Mininet/Ubuntu

# Update and install dependencies
sudo apt-get update
sudo apt-get install -y git python3 python3-pip

# Install Open vSwitch
sudo apt-get install -y openvswitch-switch openvswitch-common

# Install Mininet
cd ~
git clone https://github.com/mininet/mininet.git
cd mininet
git checkout 2.3.0 # Use a stable version, update as needed
./util/install.sh -a

# Configure network interfaces
# These names (ens38, ens39, etc.) should match your VM's interfaces
# If different, adjust accordingly

# Check interface names (outputs available interface names)
echo "Available interfaces:"
ip addr | grep -E "^[0-9]+: " | awk '{print $2}'

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

# Create OVS bridges
sudo ovs-vsctl add-br br1
sudo ovs-vsctl add-br br2
# S1 bridge is created by default in OVS

# Configure interfaces - Remove IP addresses
sudo ip addr flush dev ens38
sudo ip addr flush dev ens39
sudo ip addr flush dev ens40
sudo ip addr flush dev ens41

# Assign interfaces to bridges
sudo ovs-vsctl add-port br1 ens40
sudo ovs-vsctl add-port br2 ens38
sudo ovs-vsctl add-port s1 ens41

# Assign IP addresses to bridges
sudo ip addr add 200.175.2.129/24 dev br1
sudo ip addr add 192.168.3.129/24 dev br2
sudo ip addr add 192.168.20.129/24 dev s1

# Connect bridges to ONOS controller
sudo ovs-vsctl set-controller br1 tcp:192.168.8.128:6653
sudo ovs-vsctl set-controller br2 tcp:192.168.8.128:6653
sudo ovs-vsctl set-controller s1 tcp:192.168.8.128:6653

echo "OVS bridges have been configured and connected to the ONOS controller"
