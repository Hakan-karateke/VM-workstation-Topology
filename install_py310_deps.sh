#!/bin/bash

# Installation script for Python 3.10 dependencies
# This script installs all necessary dependencies for the SCADA network simulation

echo "===== Installing Python 3.10 Dependencies for SCADA Network Simulation ====="
echo ""

# Check if Python 3.10 is installed
if command -v python3.10 &>/dev/null; then
    echo "[+] Python 3.10 is already installed"
    PYTHON_CMD="python3.10"
elif command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    if [[ "$PYTHON_VERSION" == 3.10* ]]; then
        echo "[+] Python $PYTHON_VERSION is already installed"
        PYTHON_CMD="python3"
    else
        echo "[!] Warning: Python 3.10 is not installed. Found Python $PYTHON_VERSION"
        echo "[*] Installing Python 3.10..."
        sudo apt-get update
        sudo apt-get install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update
        sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
        PYTHON_CMD="python3.10"
    fi
else
    echo "[!] Python 3.x not found. Installing Python 3.10..."
    sudo apt-get update
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
    PYTHON_CMD="python3.10"
fi

# Make sure pip is installed for Python 3.10
if ! command -v "$PYTHON_CMD -m pip" &>/dev/null; then
    echo "[*] Installing pip for $PYTHON_CMD..."
    sudo apt-get install -y curl
    curl -sS https://bootstrap.pypa.io/get-pip.py | sudo $PYTHON_CMD
fi

# Create a virtual environment (optional but recommended)
echo "[*] Creating a Python virtual environment..."
$PYTHON_CMD -m venv scada_venv
source scada_venv/bin/activate

# Install required packages
echo "[*] Installing required Python packages..."
pip install --upgrade pip
pip install pymodbus>=3.0.0
pip install scapy>=2.5.0
pip install requests>=2.28.0
pip install beautifulsoup4>=4.11.0
pip install fake-useragent>=1.1.0
pip install flask>=2.2.0
pip install plotly>=5.10.0
pip install ryu>=4.34
pip install paramiko>=3.0.0
pip install netaddr>=0.8.0
pip install python-nmap>=0.7.1

# If needed for SDN simulation, install mininet
if ! command -v mn &>/dev/null; then
    echo "[*] Mininet not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y mininet
fi

# Create activation script for future use
cat > activate_scada_env.sh << 'EOF'
#!/bin/bash
source scada_venv/bin/activate
echo "[+] SCADA environment activated. You can now run the scripts."
EOF

chmod +x activate_scada_env.sh

echo ""
echo "===== Installation Complete ====="
echo "To activate the environment, run: source activate_scada_env.sh"
echo "To run a script, use: python3 scripts/script_name.py"
echo ""
