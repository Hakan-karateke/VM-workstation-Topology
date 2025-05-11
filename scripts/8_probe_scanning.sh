#!/bin/bash
# Probe & Scanning Script
# For Kali Linux VM (Attacker Machine)

if [ $# -ne 2 ]; then
    echo "Usage: $0 <target_ip> <scan_type>"
    echo "Scan types: version, port, service, vuln"
    exit 1
fi

TARGET_IP=$1
SCAN_TYPE=$2

echo "Starting $SCAN_TYPE scan against $TARGET_IP"

case $SCAN_TYPE in
    version)
        echo "Running OS version detection scan..."
        sudo nmap -O $TARGET_IP
        ;;
    port)
        echo "Running comprehensive port scan..."
        sudo nmap -p- -sS $TARGET_IP
        ;;
    service)
        echo "Running service discovery scan..."
        sudo nmap -sV $TARGET_IP
        ;;
    vuln)
        echo "Running vulnerability scan..."
        sudo nmap --script vuln $TARGET_IP
        ;;
    *)
        echo "Unknown scan type: $SCAN_TYPE"
        exit 1
        ;;
esac

echo "Scan completed!"
