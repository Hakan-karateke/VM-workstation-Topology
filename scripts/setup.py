#!/usr/bin/env python

"""
SCADA Network Setup Helper Script
- Helps with the setup and configuration of the SCADA network topology
- Installs required dependencies
- Creates network configurations
"""

import os
import sys
import subprocess
import argparse
import platform
import re
from datetime import datetime

def print_banner():
    banner = """
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ SCADA Network Topology and Attack Simulation Setup   ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """
    print(banner)

def check_os():
    """Check if running on a supported OS"""
    system = platform.system().lower()
    if system == 'linux':
        # Check if this is Kali or Ubuntu
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'kali' in content.lower():
                    return 'kali'
                elif 'ubuntu' in content.lower():
                    return 'ubuntu'
                else:
                    return 'linux'
        except:
            return 'linux'
    else:
        return system

def run_command(cmd, verbose=True):
    """Run a shell command and return output"""
    if verbose:
        print(f"[*] Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        if verbose and result.stdout:
            print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"[!] Command failed with error: {e}")
            if e.stderr:
                print(f"[!] Error output: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        if verbose:
            print(f"[!] Error executing command: {e}")
        return False, str(e)

def check_dependencies_ubuntu():
    """Check and install dependencies for Ubuntu"""
    print("[*] Checking dependencies for Ubuntu...")
    
    # Check Python3
    print("[*] Checking Python installation...")
    success, output = run_command("python3 --version")
    if not success:
        print("[!] Python3 not found. Installing...")
        run_command("sudo apt-get update && sudo apt-get install -y python3 python3-pip")
    
    # Check Mininet
    print("[*] Checking Mininet installation...")
    success, output = run_command("sudo mn --version", verbose=False)
    if not success:
        print("[!] Mininet not found. Installing...")
        run_command("sudo apt-get update && sudo apt-get install -y mininet")
    
    # Check Ryu SDN Controller
    print("[*] Checking Ryu SDN Controller installation...")
    success, output = run_command("ryu-manager --version", verbose=False)
    if not success:
        print("[!] Ryu not found. Installing...")
        run_command("sudo pip3 install ryu")
    
    # Check PyModbus
    print("[*] Checking PyModbus installation...")
    success, output = run_command("pip3 list | grep pymodbus", verbose=False)
    if not success or "pymodbus" not in output.lower():
        print("[!] PyModbus not found. Installing...")
        run_command("sudo pip3 install pymodbus")
    
    # Check Scapy
    print("[*] Checking Scapy installation...")
    success, output = run_command("pip3 list | grep scapy", verbose=False)
    if not success or "scapy" not in output.lower():
        print("[!] Scapy not found. Installing...")
        run_command("sudo pip3 install scapy")
    
    # Additional dependencies for attack scripts
    print("[*] Installing additional dependencies...")
    run_command("sudo pip3 install requests beautifulsoup4 fake_useragent")
    
    print("[+] All dependencies for Ubuntu have been installed/verified.")

def check_dependencies_kali():
    """Check and install dependencies for Kali Linux"""
    print("[*] Checking dependencies for Kali Linux...")
    
    # Check Python3
    print("[*] Checking Python installation...")
    success, output = run_command("python3 --version")
    if not success:
        print("[!] Python3 not found. Installing...")
        run_command("sudo apt-get update && sudo apt-get install -y python3 python3-pip")
    
    # Check PyModbus (for Modbus server/client)
    print("[*] Checking PyModbus installation...")
    success, output = run_command("pip3 list | grep pymodbus", verbose=False)
    if not success or "pymodbus" not in output.lower():
        print("[!] PyModbus not found. Installing...")
        run_command("sudo pip3 install pymodbus")
    
    # Check Scapy
    print("[*] Checking Scapy installation...")
    success, output = run_command("pip3 list | grep scapy", verbose=False)
    if not success or "scapy" not in output.lower():
        print("[!] Scapy not found. Installing...")
        run_command("sudo pip3 install scapy")
    
    # Additional dependencies for attack scripts
    print("[*] Installing additional dependencies...")
    run_command("sudo pip3 install requests beautifulsoup4 fake_useragent")
    
    print("[+] All dependencies for Kali Linux have been installed/verified.")

def setup_network_config():
    """Set up network configuration for communication between VMs"""
    os_type = check_os()
    
    if os_type in ['ubuntu', 'kali', 'linux']:
        print("[*] Setting up network configuration...")
        
        # Back up current network configuration
        run_command("sudo cp /etc/network/interfaces /etc/network/interfaces.backup")
        
        # Get current network interfaces
        success, output = run_command("ip -o link show | awk -F': ' '{print $2}'", verbose=False)
        interfaces = output.strip().split('\n')
        
        # Filter out loopback and virtual interfaces
        physical_interfaces = [intf for intf in interfaces 
                              if not intf.startswith('lo') and 
                              not intf.startswith('virbr') and
                              not intf.startswith('docker')]
        
        if physical_interfaces:
            intf = physical_interfaces[0]
            print(f"[*] Using interface: {intf}")
            
            # Create network config
            if os_type == 'ubuntu':
                # For Ubuntu - will host Mininet
                network_config = f"""# Network configuration for SCADA simulation
auto {intf}
iface {intf} inet static
    address 10.0.0.100
    netmask 255.255.255.0
    gateway 10.0.0.1
"""
            else:
                # For Kali - victim or attacker
                if 'kali1' in platform.node().lower():
                    # Kali1 - Victim
                    ip = "10.0.0.10"
                elif 'kali2' in platform.node().lower():
                    # Kali2 - Modbus Server
                    ip = "10.0.0.30"
                else:
                    # Kali3 - Additional machine
                    ip = "10.0.0.50"
                    
                network_config = f"""# Network configuration for SCADA simulation
auto {intf}
iface {intf} inet static
    address {ip}
    netmask 255.255.255.0
    gateway 10.0.0.1
"""
            
            # Write configuration
            with open('network_config.txt', 'w') as f:
                f.write(network_config)
            
            print(f"[*] Network configuration saved to network_config.txt")
            print("[*] To apply this configuration, run:")
            print(f"    sudo cp network_config.txt /etc/network/interfaces.d/scada.conf")
            print(f"    sudo systemctl restart networking")
        else:
            print("[!] No suitable network interface found")
    else:
        print(f"[!] Network configuration not supported on {os_type}")

def configure_firewall():
    """Configure firewall to allow SCADA traffic"""
    os_type = check_os()
    
    if os_type in ['ubuntu', 'kali', 'linux']:
        print("[*] Configuring firewall...")
        
        # First check if firewall is active
        success, output = run_command("sudo ufw status", verbose=False)
        
        if "inactive" in output:
            print("[*] Firewall is inactive. No configuration needed.")
            return
            
        # Allow Modbus TCP (port 502)
        run_command("sudo ufw allow 502/tcp")
        
        # Allow SDN Controller (port 6633)
        run_command("sudo ufw allow 6633/tcp")
        
        # Allow HTTP/HTTPS (for HTTP flood attacks)
        run_command("sudo ufw allow 80/tcp")
        run_command("sudo ufw allow 443/tcp")
        
        print("[+] Firewall configured to allow SCADA traffic")
    else:
        print(f"[!] Firewall configuration not supported on {os_type}")

def setup_scripts_permissions():
    """Set correct permissions on all scripts"""
    print("[*] Setting execute permissions on scripts...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts = [f for f in os.listdir(script_dir) if f.endswith('.py')]
    
    for script in scripts:
        script_path = os.path.join(script_dir, script)
        run_command(f"chmod +x {script_path}")
    
    print(f"[+] Execute permissions set for {len(scripts)} scripts")

def start_scada_network():
    """Start the SCADA network topology in Mininet"""
    os_type = check_os()
    
    if os_type == 'ubuntu':
        print("[*] Starting SCADA network simulation...")
        
        # Start the SDN controller in the background
        script_dir = os.path.dirname(os.path.abspath(__file__))
        controller_script = os.path.join(script_dir, 'sdn_controller.py')
        
        print("[*] Starting SDN controller...")
        run_command(f"sudo python3 {controller_script} &")
        
        # Give the controller time to initialize
        import time
        time.sleep(3)
        
        # Start the Mininet topology
        topology_script = os.path.join(script_dir, 'scada_topology.py')
        print("[*] Starting Mininet topology...")
        run_command(f"sudo python3 {topology_script}")
    else:
        print(f"[!] SCADA network simulation can only be started on Ubuntu (Mininet host)")

def setup_modbus_server():
    """Set up and start the Modbus server on Kali2"""
    os_type = check_os()
    hostname = platform.node().lower()
    
    if 'kali2' in hostname or (os_type == 'kali' and input("Is this the Modbus server (Kali2)? (y/n): ").lower() == 'y'):
        print("[*] Setting up Modbus server...")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        server_script = os.path.join(script_dir, 'modbus_server.py')
        
        print("[*] Starting Modbus server...")
        run_command(f"python3 {server_script}")
    else:
        print(f"[!] This machine is not configured as the Modbus server (Kali2)")

def main():
    """Main function to handle all setup steps"""
    print_banner()
    
    parser = argparse.ArgumentParser(description='SCADA Network Setup Helper')
    parser.add_argument('--check', action='store_true', help='Check dependencies only')
    parser.add_argument('--network', action='store_true', help='Set up network configuration')
    parser.add_argument('--firewall', action='store_true', help='Configure firewall')
    parser.add_argument('--permissions', action='store_true', help='Set script permissions')
    parser.add_argument('--start-mininet', action='store_true', help='Start the Mininet topology (Ubuntu only)')
    parser.add_argument('--start-modbus', action='store_true', help='Start the Modbus server (Kali2 only)')
    parser.add_argument('--all', action='store_true', help='Run all setup steps')
    
    args = parser.parse_args()
    
    # Detect OS
    os_type = check_os()
    print(f"[*] Detected OS: {os_type}")
    
    # If no args specified, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Run requested actions
    if args.check or args.all:
        if os_type == 'ubuntu':
            check_dependencies_ubuntu()
        elif os_type == 'kali':
            check_dependencies_kali()
        else:
            print(f"[!] Dependency checking not supported on {os_type}")
    
    if args.network or args.all:
        setup_network_config()
    
    if args.firewall or args.all:
        configure_firewall()
    
    if args.permissions or args.all:
        setup_scripts_permissions()
    
    if args.start_mininet or args.all:
        if os_type == 'ubuntu':
            start_scada_network()
        else:
            print(f"[!] Mininet can only be started on Ubuntu")
    
    if args.start_modbus or args.all:
        setup_modbus_server()
    
    print("\n[+] Setup completed successfully!")
    print("[*] For more information on using these scripts, refer to the README.md file.")

if __name__ == "__main__":
    main()
