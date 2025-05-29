#!/usr/bin/env python

"""
Modbus Client for SCADA simulation
This script implements a basic Modbus TCP client that connects to a SCADA server
"""

from pymodbus.client.sync import ModbusTcpClient
import time
import logging

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

# Server details
SERVER_HOST = "10.0.0.30"  # IP of kali2 (Modbus server)
SERVER_PORT = 502

def process_data(temperature, pressure, flow_rate, valve_state):
    """Process the data received from the server"""
    # In a real application, you might do something with this data
    # For now, we'll just log it
    log.info(f"Data received: Temp={temperature:.2f}°C, Press={pressure:.2f}bar, " +
             f"Flow={flow_rate:.2f}L/s, Valve={'Open' if valve_state else 'Closed'}")

def main():
    # Create Modbus client
    client = ModbusTcpClient(SERVER_HOST, port=SERVER_PORT)
    
    try:
        # Connect to server
        connection = client.connect()
        if connection:
            log.info(f"Connected to Modbus server at {SERVER_HOST}:{SERVER_PORT}")
        else:
            log.error(f"Failed to connect to {SERVER_HOST}:{SERVER_PORT}")
            return

        # Main loop - read data continuously
        while True:
            try:
                # Read holding registers (temperature, pressure, flow rate)
                temp_reg = client.read_holding_registers(0, 1)
                press_reg = client.read_holding_registers(1, 1)
                flow_reg = client.read_holding_registers(2, 1)
                
                # Read coils (valve state)
                valve_reg = client.read_coils(0, 1)
                
                if not temp_reg.isError() and not press_reg.isError() and \
                   not flow_reg.isError() and not valve_reg.isError():
                    
                    # Convert the raw values to actual measurements
                    temperature = temp_reg.registers[0] / 100.0  # Convert to Celsius
                    pressure = press_reg.registers[0] / 100.0    # Convert to bar
                    flow_rate = flow_reg.registers[0] / 100.0    # Convert to L/s
                    valve_state = valve_reg.bits[0]              # Boolean
                    
                    # Process the data
                    process_data(temperature, pressure, flow_rate, valve_state)
                else:
                    log.error("Error reading data from server")
            except Exception as e:
                log.error(f"Error in communication: {e}")
                # Try to reconnect
                client.close()
                time.sleep(1)
                client.connect()
                
            time.sleep(1)  # Poll every second
            
    except KeyboardInterrupt:
        log.info("Client stopped by user")
    finally:
        client.close()
        log.info("Connection closed")

if __name__ == "__main__":
    main()
