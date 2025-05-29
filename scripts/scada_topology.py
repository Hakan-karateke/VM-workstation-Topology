#!/usr/bin/env python3

"""
SCADA Network Topology with Mininet
- Creates a network with SDN Controller and multiple hosts
- Implements a SCADA network topology for attack simulation
- Compatible with Python 3.10
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import os
from time import sleep

def scadaNetworkTopology():
    # Create network with remote controller
    info('*** Creating SCADA network topology\n')
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)
    
    # Add controller
    info('*** Adding controller\n')
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    
    # Add switches
    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')  # Main switch
    s2 = net.addSwitch('s2')  # SCADA network switch
    
    # Add hosts
    info('*** Adding hosts\n')
    # Kali1 - Victim
    kali1 = net.addHost('kali1', ip='10.0.0.10/24', mac='00:00:00:00:00:10')
    
    # MinineNet1 - Attacker
    mininet1 = net.addHost('mininet1', ip='10.0.0.20/24', mac='00:00:00:00:00:20')
    
    # Kali2 - Modbus Server
    kali2 = net.addHost('kali2', ip='10.0.0.30/24', mac='00:00:00:00:00:30')
    
    # Mininet2 - Modbus Client
    mininet2 = net.addHost('mininet2', ip='10.0.0.40/24', mac='00:00:00:00:00:40')
    
    # Additional SCADA devices
    scada1 = net.addHost('scada1', ip='10.0.0.50/24', mac='00:00:00:00:00:50')
    scada2 = net.addHost('scada2', ip='10.0.0.60/24', mac='00:00:00:00:00:60')
    
    # Link hosts to switches
    info('*** Creating links\n')
    net.addLink(kali1, s1)
    net.addLink(mininet1, s1)
    net.addLink(s1, s2)  # Connect the two switches
    net.addLink(kali2, s2)
    net.addLink(mininet2, s2)
    net.addLink(scada1, s2)
    net.addLink(scada2, s2)
    
    # Start network
    info('*** Starting network\n')
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    
    # Configure routes
    info('*** Configuring routes\n')
    
    # Run post-configuration commands
    info('*** Running post-configuration commands\n')
      # Start Modbus server on kali2
    info('*** Starting Modbus server on kali2\n')
    kali2.cmd('python3 /home/ubuntu/scripts/modbus_server.py &')
    
    # Start Modbus client on mininet2
    info('*** Starting Modbus client on mininet2\n')
    mininet2.cmd('python3 /home/ubuntu/scripts/modbus_client.py &')
    
    info('*** Network is ready\n')
    
    # Run CLI
    CLI(net)
    
    # Stop network
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    scadaNetworkTopology()
