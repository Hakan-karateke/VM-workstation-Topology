#!/usr/bin/env python3

"""
Port Scanning Tool
- Scans for open ports on target hosts
- Multiple scanning techniques: TCP Connect, SYN, UDP, and FIN scanning
- Compatible with Python 3.10
"""

from scapy.all import *
import argparse
import socket
import threading
import time
from datetime import datetime
import sys

# Global variables
open_ports = []
closed_ports = []
filtered_ports = []
stop_event = threading.Event()

def tcp_connect_scan(target, port, timeout=2):
    """
    Perform a TCP connect scan on the target port
    
    :param target: Target IP address or hostname
    :param port: Port number to scan
    :param timeout: Socket timeout in seconds
    :return: (port, state) where state is 'open', 'closed', or 'filtered'
    """
    try:
        # Create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        
        # Try to connect
        result = s.connect_ex((target, port))
        
        # Close the socket
        s.close()
        
        # Check the result
        if result == 0:
            return port, 'open'
        else:
            return port, 'closed'
            
    except socket.timeout:
        return port, 'filtered'
    except:
        return port, 'error'

def tcp_syn_scan(target, port, timeout=2):
    """
    Perform a TCP SYN scan on the target port
    
    :param target: Target IP address
    :param port: Port number to scan
    :param timeout: Response timeout in seconds
    :return: (port, state) where state is 'open', 'closed', or 'filtered'
    """
    try:
        # Send SYN packet and get response
        ans, unans = sr(IP(dst=target)/TCP(dport=port, flags="S"), timeout=timeout, verbose=0)
        
        # Check if we got a response
        if len(ans) > 0:
            for s, r in ans:
                # Check TCP flags in the response
                if r.haslayer(TCP):
                    tcp_flags = r[TCP].flags
                    
                    # SYN-ACK means port is open
                    if tcp_flags == 0x12:  # SYN-ACK
                        # Send RST packet to close connection
                        send(IP(dst=target)/TCP(dport=port, flags="R"), verbose=0)
                        return port, 'open'
                    
                    # RST means port is closed
                    elif tcp_flags == 0x14:  # RST-ACK
                        return port, 'closed'
                    
                    # Any other response
                    else:
                        return port, 'filtered'
                        
        # No response means filtered
        return port, 'filtered'
        
    except:
        return port, 'error'

def tcp_fin_scan(target, port, timeout=2):
    """
    Perform a TCP FIN scan on the target port
    
    :param target: Target IP address
    :param port: Port number to scan
    :param timeout: Response timeout in seconds
    :return: (port, state) where state is 'open', 'closed', or 'filtered'
    """
    try:
        # Send FIN packet and get response
        ans, unans = sr(IP(dst=target)/TCP(dport=port, flags="F"), timeout=timeout, verbose=0)
        
        # Check if we got a response
        if len(ans) > 0:
            for s, r in ans:
                # RST response means closed port
                if r.haslayer(TCP) and r[TCP].flags & 0x4:  # RST flag
                    return port, 'closed'
                else:
                    return port, 'filtered'
        
        # No response typically means open/filtered
        return port, 'open|filtered'
        
    except:
        return port, 'error'

def udp_scan(target, port, timeout=2):
    """
    Perform a UDP scan on the target port
    
    :param target: Target IP address
    :param port: Port number to scan
    :param timeout: Response timeout in seconds
    :return: (port, state) where state is 'open', 'closed', or 'filtered'
    """
    try:
        # Send UDP packet and get response
        ans, unans = sr(IP(dst=target)/UDP(dport=port), timeout=timeout, verbose=0)
        
        # Check if we got a response
        if len(ans) > 0:
            for s, r in ans:
                # ICMP Port Unreachable means closed
                if r.haslayer(ICMP):
                    if r[ICMP].type == 3 and r[ICMP].code == 3:
                        return port, 'closed'
                    else:
                        return port, 'filtered'
                else:
                    return port, 'open'
        
        # No response typically means open/filtered
        return port, 'open|filtered'
        
    except:
        return port, 'error'

def service_scan(target, port):
    """
    Try to identify the service running on a port
    
    :param target: Target IP address
    :param port: Port number to scan
    :return: Service name or None
    """
    try:
        service = socket.getservbyport(port)
        return service
    except:
        # Some common ports that might not be in the service database
        common_ports = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            123: 'NTP',
            143: 'IMAP',
            161: 'SNMP',
            443: 'HTTPS',
            465: 'SMTPS',
            587: 'SMTP Submission',
            993: 'IMAPS',
            995: 'POP3S',
            1433: 'SQL Server',
            1723: 'PPTP',
            3306: 'MySQL',
            3389: 'RDP',
            5900: 'VNC',
            8080: 'HTTP Proxy',
            8443: 'HTTPS Alt',
            27017: 'MongoDB'
        }
        
        if port in common_ports:
            return common_ports[port]
        
        return None

def banner_grab(target, port, timeout=2):
    """
    Attempt to grab service banners
    
    :param target: Target IP address
    :param port: Port number
    :param timeout: Socket timeout in seconds
    :return: Banner string or None
    """
    try:
        # Create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        
        # Connect to the port
        s.connect((target, port))
        
        # Send data to trigger a response
        triggers = {
            21: b"HELP\r\n",
            22: b"\r\n",
            23: b"\r\n",
            25: b"HELO scan.local\r\n",
            80: b"HEAD / HTTP/1.0\r\n\r\n",
            110: b"QUIT\r\n",
            143: b"A1 CAPABILITY\r\n",
            443: b"HEAD / HTTP/1.0\r\n\r\n"
        }
        
        # Use a protocol-specific trigger if available, otherwise send a newline
        if port in triggers:
            s.send(triggers[port])
        else:
            s.send(b"\r\n")
        
        # Receive the banner
        banner = s.recv(1024)
        s.close()
        
        # Try to decode the banner to string
        try:
            return banner.decode('utf-8', errors='ignore').strip()
        except:
            return str(banner)
            
    except:
        return None

def scan_worker(target, ports, scan_type, results, lock):
    """
    Worker function for threaded port scanning
    
    :param target: Target IP address
    :param ports: List of ports to scan
    :param scan_type: Type of scan to perform
    :param results: Shared results dictionary
    :param lock: Thread lock
    """
    for port in ports:
        # Check if we should stop
        if stop_event.is_set():
            break
            
        # Perform the scan based on type
        if scan_type == 'connect':
            port, state = tcp_connect_scan(target, port)
        elif scan_type == 'syn':
            port, state = tcp_syn_scan(target, port)
        elif scan_type == 'fin':
            port, state = tcp_fin_scan(target, port)
        elif scan_type == 'udp':
            port, state = udp_scan(target, port)
        else:
            port, state = tcp_connect_scan(target, port)
        
        # Store the result
        with lock:
            results[port] = state
            # Print progress every 10 ports
            if len(results) % 10 == 0:
                sys.stdout.write(f"\r[*] Scanned {len(results)}/{len(ports)} ports")
                sys.stdout.flush()

def port_scan(target, port_range="1-1000", scan_type="connect", threads=10, banner=False, verbose=True):
    """
    Perform a port scan on the target
    
    :param target: Target IP address or hostname
    :param port_range: Range of ports to scan (e.g., "1-1000", "21,22,80,443", "1-100,443,8080")
    :param scan_type: Type of scan (connect, syn, fin, udp)
    :param threads: Number of threads to use
    :param banner: Whether to attempt banner grabbing
    :param verbose: Whether to print verbose output
    """
    # Resolve hostname to IP if needed
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"[!] Could not resolve hostname: {target}")
        return
    
    if target_ip != target:
        print(f"[*] Resolved {target} to {target_ip}")
    
    print(f"[*] Starting {scan_type.upper()} scan on {target_ip}")
    print(f"[*] Port range: {port_range}")
    print(f"[*] Using {threads} threads")
    print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Parse port range
    try:
        ports = []
        for part in port_range.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        ports = sorted(list(set(ports)))  # Remove duplicates
    except:
        print("[!] Invalid port range")
        return
    
    # Check if we need root for SYN/FIN/UDP scans
    if scan_type in ['syn', 'fin', 'udp'] and os.geteuid() != 0:
        print(f"[!] WARNING: {scan_type.upper()} scan requires root privileges. Results may be unreliable.")
    
    # Prepare for threaded scanning
    lock = threading.Lock()
    results = {}
    start_time = time.time()
    
    # Divide ports among threads
    chunk_size = len(ports) // threads
    if chunk_size == 0:
        chunk_size = 1
    
    thread_list = []
    for i in range(0, len(ports), chunk_size):
        port_chunk = ports[i:i+chunk_size]
        t = threading.Thread(
            target=scan_worker,
            args=(target_ip, port_chunk, scan_type, results, lock)
        )
        t.daemon = True
        thread_list.append(t)
    
    # Start all threads
    for t in thread_list:
        t.start()
    
    try:
        # Wait for all threads to finish
        for t in thread_list:
            t.join()
            
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        stop_event.set()
        for t in thread_list:
            t.join(1)
    
    # Process and categorize results
    open_ports = []
    closed_ports = []
    filtered_ports = []
    
    for port, state in results.items():
        if state == 'open':
            open_ports.append(port)
        elif state == 'closed':
            closed_ports.append(port)
        elif 'filtered' in state:
            filtered_ports.append(port)
    
    # Print results
    scan_time = time.time() - start_time
    print(f"\n[*] Scan completed in {scan_time:.2f} seconds")
    print(f"[*] Results for {target_ip}:")
    print(f"[*] Open ports: {len(open_ports)}")
    print(f"[*] Closed ports: {len(closed_ports)}")
    print(f"[*] Filtered ports: {len(filtered_ports)}")
    
    if open_ports:
        print("\nPORT\tSTATE\tSERVICE\tBANNER")
        print("-" * 60)
        
        for port in sorted(open_ports):
            service = service_scan(target_ip, port)
            service_str = service if service else "unknown"
            
            if banner:
                banner_str = banner_grab(target_ip, port)
                banner_preview = ""
                if banner_str:
                    # Limit banner preview to 40 chars
                    banner_preview = banner_str.replace("\n", "\\n").replace("\r", "\\r")[:40]
                    if len(banner_str) > 40:
                        banner_preview += "..."
                print(f"{port}/tcp\topen\t{service_str}\t{banner_preview}")
            else:
                print(f"{port}/tcp\topen\t{service_str}")
    
    # If in verbose mode, also show filtered ports
    if verbose and filtered_ports:
        print("\nFiltered ports:")
        for port in sorted(filtered_ports):
            service = service_scan(target_ip, port)
            service_str = service if service else "unknown"
            print(f"{port}/tcp\tfiltered\t{service_str}")
    
    print(f"\n[*] Scan finished at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    # Check if we are running as root (needed for some scan types)
    if os.geteuid() != 0:
        print("[!] Some scan types require root privileges for accurate results")
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Port Scanner')
    parser.add_argument('-t', '--target', required=True, help='Target IP address or hostname')
    parser.add_argument('-p', '--ports', default="1-1000", help='Port range to scan (e.g., "1-1000", "21,22,80,443")')
    parser.add_argument('-s', '--scan', choices=['connect', 'syn', 'fin', 'udp'], default='connect', help='Scan type (default: connect)')
    parser.add_argument('-n', '--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('-b', '--banner', action='store_true', help='Attempt banner grabbing')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Import os module for root check
    import os
    
    # Execute scan
    port_scan(args.target, args.ports, args.scan, args.threads, args.banner, args.verbose)
