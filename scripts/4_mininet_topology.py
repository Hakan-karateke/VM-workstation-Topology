#!/usr/bin/python3
# Mininet Custom Topology Script

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf

def myNetwork():
    net = Mininet(topo=None, build=False, ipBase='192.168.20.0/24')
    
    info('*** Adding controller\n')
    # Use remote controller (ONOS)
    c0 = net.addController('c0', controller=RemoteController, ip='192.168.8.128', port=6653)
    
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='192.168.20.131/24', defaultRoute='via 192.168.20.129')
    h2 = net.addHost('h2', cls=Host, ip='192.168.20.132/24', defaultRoute='via 192.168.20.129')
    h3 = net.addHost('h3', cls=Host, ip='192.168.20.133/24', defaultRoute='via 192.168.20.129')
    h4 = net.addHost('h4', cls=Host, ip='192.168.20.134/24', defaultRoute='via 192.168.20.129')
    
    info('*** Adding switch\n')
    # No need to add switch here as we're using the existing OVS bridges
    # We'll connect hosts to the s1 bridge
    
    info('*** Creating links\n')
    # Create links between hosts and switch
    # These will be connected to the s1 bridge
    
    info('*** Starting network\n')
    net.build()
    
    # Connect hosts to s1 OVS bridge
    info('*** Connecting hosts to s1 bridge\n')
    for h in [h1, h2, h3, h4]:
        Intf(h.name + '-eth0', node=h)
        cmd = 'ovs-vsctl add-port s1 {0}-eth0'.format(h.name)
        info('*** Running: ' + cmd + '\n')
        import subprocess
        subprocess.call(cmd, shell=True)
    
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()
    
    info('*** Running CLI\n')
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
