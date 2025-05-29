#!/usr/bin/env python3

"""
SCADA Network Monitor
- Monitors network traffic in the SCADA network
- Detects potential attacks
- Logs traffic statistics
- Compatible with Python 3.10
"""

from scapy.all import *
import argparse
import time
import threading
import logging
from datetime import datetime
import os
import signal
import sys

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"network_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Global variables
packet_stats = {
    'total': 0,
    'tcp': 0,
    'udp': 0,
    'icmp': 0,
    'http': 0,
    'modbus': 0,  # Modbus TCP (port 502)
    'syn_flags': 0,
    'ack_flags': 0
}

# Traffic rates
traffic_rates = {
    'pps': 0,        # Packets per second
    'bps': 0,        # Bytes per second
    'tcp_pps': 0,    # TCP packets per second
    'udp_pps': 0,    # UDP packets per second
}

# Variables for rate calculation
last_time = time.time()
last_total = 0
last_bytes = 0
last_tcp = 0
last_udp = 0

# Attack detection thresholds
THRESHOLDS = {
    'pps': 1000,         # Packets per second
    'tcp_syn_rate': 500, # TCP SYN packets per second
    'icmp_rate': 500,    # ICMP packets per second
    'udp_rate': 800,     # UDP packets per second
    'tcp_ack_rate': 800  # TCP ACK packets per second
}

# Flag to control monitoring
stop_monitoring = False

def process_packet(pkt):
    """Process a single packet and update statistics"""
    global packet_stats, last_bytes
    
    # Update total count
    packet_stats['total'] += 1
    
    # Update bytes count
    if hasattr(pkt, 'len'):
        last_bytes += pkt.len
    
    # Process IP layer
    if IP in pkt:
        # TCP packet
        if TCP in pkt:
            packet_stats['tcp'] += 1
            
            # Check TCP flags
            tcp_flags = pkt[TCP].flags
            if tcp_flags & 0x02:  # SYN flag
                packet_stats['syn_flags'] += 1
            if tcp_flags & 0x10:  # ACK flag
                packet_stats['ack_flags'] += 1
            
            # Check for HTTP traffic (ports 80, 8080, 443)
            if pkt[TCP].dport in [80, 8080, 443] or pkt[TCP].sport in [80, 8080, 443]:
                packet_stats['http'] += 1
            
            # Check for Modbus traffic (port 502)
            if pkt[TCP].dport == 502 or pkt[TCP].sport == 502:
                packet_stats['modbus'] += 1
        
        # UDP packet
        elif UDP in pkt:
            packet_stats['udp'] += 1
        
        # ICMP packet
        elif ICMP in pkt:
            packet_stats['icmp'] += 1

def calculate_rates():
    """Calculate traffic rates based on packet statistics"""
    global traffic_rates, last_time, last_total, last_bytes, last_tcp, last_udp
    global packet_stats
    
    current_time = time.time()
    time_diff = current_time - last_time
    
    if time_diff > 0:
        # Calculate packets per second
        pkt_diff = packet_stats['total'] - last_total
        traffic_rates['pps'] = pkt_diff / time_diff
        
        # Calculate bytes per second
        traffic_rates['bps'] = last_bytes / time_diff
        
        # Calculate protocol-specific rates
        tcp_diff = packet_stats['tcp'] - last_tcp
        traffic_rates['tcp_pps'] = tcp_diff / time_diff
        
        udp_diff = packet_stats['udp'] - last_udp
        traffic_rates['udp_pps'] = udp_diff / time_diff
        
        # Update last values
        last_time = current_time
        last_total = packet_stats['total']
        last_bytes = 0  # Reset byte counter
        last_tcp = packet_stats['tcp']
        last_udp = packet_stats['udp']

def detect_attacks():
    """Detect potential attacks based on traffic rates"""
    attacks = []
    
    # TCP SYN Flood detection
    syn_rate = packet_stats['syn_flags'] / (time.time() - last_time)
    if syn_rate > THRESHOLDS['tcp_syn_rate']:
        attacks.append(f"Possible TCP SYN Flood detected ({syn_rate:.2f} SYNs/sec)")
    
    # ICMP Flood detection
    icmp_rate = packet_stats['icmp'] / (time.time() - last_time)
    if icmp_rate > THRESHOLDS['icmp_rate']:
        attacks.append(f"Possible ICMP Flood detected ({icmp_rate:.2f} ICMP/sec)")
    
    # UDP Flood detection
    if traffic_rates['udp_pps'] > THRESHOLDS['udp_rate']:
        attacks.append(f"Possible UDP Flood detected ({traffic_rates['udp_pps']:.2f} UDP/sec)")
    
    # TCP-ACK Flood detection
    ack_rate = packet_stats['ack_flags'] / (time.time() - last_time)
    if ack_rate > THRESHOLDS['tcp_ack_rate']:
        attacks.append(f"Possible TCP-ACK Flood detected ({ack_rate:.2f} ACKs/sec)")
    
    # General high traffic detection
    if traffic_rates['pps'] > THRESHOLDS['pps']:
        attacks.append(f"High traffic rate detected ({traffic_rates['pps']:.2f} packets/sec)")
    
    return attacks

def display_stats():
    """Display network statistics periodically"""
    global stop_monitoring
    
    while not stop_monitoring:
        try:
            time.sleep(1)  # Update every second
            
            # Calculate traffic rates
            calculate_rates()
            
            # Detect potential attacks
            attacks = detect_attacks()
            
            # Log statistics
            logging.info(f"Traffic Stats: "
                        f"{traffic_rates['pps']:.2f} pps, "
                        f"{traffic_rates['bps']/1024:.2f} KB/s, "
                        f"TCP: {packet_stats['tcp']}, "
                        f"UDP: {packet_stats['udp']}, "
                        f"ICMP: {packet_stats['icmp']}, "
                        f"HTTP: {packet_stats['http']}, "
                        f"Modbus: {packet_stats['modbus']}")
            
            # Display current traffic rates
            print(f"\r[*] Traffic: {traffic_rates['pps']:.2f} pps, "
                 f"{traffic_rates['bps']/1024:.2f} KB/s, "
                 f"TCP: {traffic_rates['tcp_pps']:.2f} pps, "
                 f"UDP: {traffic_rates['udp_pps']:.2f} pps", end="")
            
            # Log detected attacks
            for attack in attacks:
                logging.warning(attack)
                print(f"\n[!] {attack}")
            
            if attacks:
                # Move cursor back to the end of the line after printing attacks
                print("", end="")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error in display_stats: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C and other signals"""
    global stop_monitoring
    print("\n[*] Stopping network monitor...")
    stop_monitoring = True
    sys.exit(0)

def monitor_network(interface=None, filter_exp=None):
    """
    Start monitoring the network
    
    :param interface: Network interface to monitor
    :param filter_exp: BPF filter expression
    """
    global stop_monitoring
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    
    # Print monitoring information
    print(f"[*] Starting SCADA network monitor")
    print(f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if interface:
        print(f"[*] Interface: {interface}")
    if filter_exp:
        print(f"[*] Filter: {filter_exp}")
    print(f"[*] Log file: {log_file}")
    print("[*] Press Ctrl+C to stop monitoring")
    print("[*] Starting packet capture...")
    
    # Start statistics display thread
    stats_thread = threading.Thread(target=display_stats)
    stats_thread.daemon = True
    stats_thread.start()
    
    # Start packet sniffing
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
    
    # Mark monitoring as stopped
    stop_monitoring = True
    
    # Wait for stats thread to finish
    stats_thread.join()
    
    # Print summary
    print("\n[*] Monitoring stopped")
    print(f"[*] Total packets captured: {packet_stats['total']}")
    print(f"[*] TCP packets: {packet_stats['tcp']}")
    print(f"[*] UDP packets: {packet_stats['udp']}")
    print(f"[*] ICMP packets: {packet_stats['icmp']}")
    print(f"[*] HTTP packets: {packet_stats['http']}")
    print(f"[*] Modbus packets: {packet_stats['modbus']}")
    print(f"[*] Log saved to {log_file}")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='SCADA Network Monitor')
    parser.add_argument('-i', '--interface', help='Network interface to monitor')
    parser.add_argument('-f', '--filter', help='BPF filter expression')
    parser.add_argument('--tcp', action='store_true', help='Monitor TCP traffic only')
    parser.add_argument('--udp', action='store_true', help='Monitor UDP traffic only')
    parser.add_argument('--icmp', action='store_true', help='Monitor ICMP traffic only')
    parser.add_argument('--modbus', action='store_true', help='Monitor Modbus traffic only')
    parser.add_argument('--http', action='store_true', help='Monitor HTTP traffic only')
    parser.add_argument('-t', '--threshold', type=int, help='Custom packets per second threshold')
    
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
    if args.http:
        http_exp = "tcp port 80 or tcp port 8080 or tcp port 443"
        filter_exp = http_exp if not filter_exp else f"{filter_exp} and ({http_exp})"
    
    # Set custom threshold if specified
    if args.threshold:
        THRESHOLDS['pps'] = args.threshold
    
    # Start monitoring
    monitor_network(args.interface, filter_exp)
