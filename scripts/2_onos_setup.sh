#!/bin/bash
# ONOS SDN Controller Setup Script
# For VM-ONOS/Ubuntu

# Update and install dependencies
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo apt-get install -y python3-software-properties
sudo apt-get install -y curl unzip zip python3 python3-pip default-jdk

# Install ONOS dependencies
sudo apt-get install -y bridge-utils
sudo apt-get install -y maven git

# Download and install ONOS
cd ~
export ONOS_ROOT=~/onos
git clone https://github.com/opennetworkinglab/onos.git
cd onos
git checkout 2.2.0 # Use a stable version, update this as needed

# Build ONOS
mvn clean install -DskipTests

# Set environment variables for ONOS
echo 'export ONOS_ROOT=~/onos' >> ~/.bashrc
echo 'source $ONOS_ROOT/tools/dev/bash_profile' >> ~/.bashrc
source ~/.bashrc

# Configure network interface
# Assuming the interface on ONOS VM is ens33 - adjust if needed
sudo ip addr add 192.168.8.128/24 dev ens33

# Start ONOS service
cd $ONOS_ROOT
bazel run onos-local -- clean

echo "ONOS Controller has been installed and started"
echo "Access the ONOS Web UI at http://192.168.8.128:8181/onos/ui"
echo "Default credentials: username - onos, password - rocks"
