#!/bin/bash
# Master Setup Script for SDN Testbed
# This script guides you through setting up the entire SDN testbed

echo "======================================================"
echo "SDN Testbed Setup Guide"
echo "======================================================"
echo ""
echo "This guide will help you set up the SDN testbed as shown in the topology diagram."
echo ""
echo "Prerequisites:"
echo "1. VMware Workstation installed"
echo "2. 4 VMs created:"
echo "   - 1 Ubuntu VM for ONOS controller"
echo "   - 1 Ubuntu VM for OVS switch and Mininet"
echo "   - 1 Kali Linux VM for attacker machine"
echo "   - 1 Metasploitable 2 VM for target machine"
echo ""

read -p "Have you created all the VMs? (y/n): " vm_created

if [ "$vm_created" != "y" ]; then
    echo "Please create the VMs first and then run this script again."
    exit 1
fi

echo ""
echo "Step 1: Configure VMware Virtual Networks"
echo "----------------------------------------"
echo "Please follow the instructions in 1_vmware_network_setup.txt to set up the virtual networks."
echo ""

read -p "Have you configured the VMware networks? (y/n): " networks_configured

if [ "$networks_configured" != "y" ]; then
    echo "Please configure the networks first and then continue."
    exit 1
fi

echo ""
echo "Step 2: Configure ONOS Controller VM"
echo "----------------------------------------"
echo "Copy the 2_onos_setup.sh script to the ONOS VM and run it with:"
echo "chmod +x 2_onos_setup.sh && ./2_onos_setup.sh"
echo ""

read -p "Has the ONOS controller been configured? (y/n): " onos_configured

if [ "$onos_configured" != "y" ]; then
    echo "Please configure the ONOS controller first and then continue."
    exit 1
fi

echo ""
echo "Step 3: Configure OVS Switch and Mininet VM"
echo "----------------------------------------"
echo "Copy the 3_ovs_setup.sh script to the OVS/Mininet VM and run it with:"
echo "chmod +x 3_ovs_setup.sh && ./3_ovs_setup.sh"
echo ""

read -p "Has the OVS switch been configured? (y/n): " ovs_configured

if [ "$ovs_configured" != "y" ]; then
    echo "Please configure the OVS switch first and then continue."
    exit 1
fi

echo ""
echo "Step 4: Configure Mininet Hosts"
echo "----------------------------------------"
echo "Copy the 4_mininet_topology.py script to the OVS/Mininet VM and run it with:"
echo "sudo python3 4_mininet_topology.py"
echo ""

read -p "Have the Mininet hosts been configured? (y/n): " mininet_configured

if [ "$mininet_configured" != "y" ]; then
    echo "Please configure the Mininet hosts first and then continue."
    exit 1
fi

echo ""
echo "Step 5: Test Connectivity"
echo "----------------------------------------"
echo "From the Mininet CLI on the OVS/Mininet VM, test connectivity with:"
echo "h1 ping h2"
echo "h1 ping h3"
echo "h1 ping h4"
echo "h1 ping 192.168.3.130 (Metasploitable 2 VM)"
echo "h1 ping 200.175.2.130 (Kali Linux VM)"
echo ""

read -p "Is connectivity working properly? (y/n): " connectivity_ok

if [ "$connectivity_ok" != "y" ]; then
    echo "Please troubleshoot connectivity issues and then continue."
    echo "Common issues:"
    echo "1. Check IP addresses and subnet masks"
    echo "2. Verify bridge configurations"
    echo "3. Check that IP forwarding is enabled"
    echo "4. Ensure ONOS controller is running and accessible"
    exit 1
fi

echo ""
echo "======================================================"
echo "SDN Testbed Setup Complete!"
echo "======================================================"
echo ""
echo "You can now use the attack scripts provided to generate traffic and attacks:"
echo "- 5_dos_attacks.sh: DoS attacks"
echo "- 6_ddos_attacks.sh: DDoS attacks"
echo "- 7_web_attacks.sh: SQL Injection and XSS attacks"
echo "- 8_probe_scanning.sh: Network probing and scanning"
echo "- 9_botnet_attack.sh: Botnet simulation"
echo "- 10_u2r_exploitation.sh: User-to-Root exploitation attacks"
echo ""
echo "Example usage:"
echo "./5_dos_attacks.sh 192.168.20.134 tcp"
echo "./8_probe_scanning.sh 192.168.3.130 port"
echo ""
echo "Happy testing!"
