#!/usr/bin/env python

"""
Modbus Server for SCADA simulation
This script implements a basic Modbus TCP server that simulates a SCADA device
"""

from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import logging
import threading
import time
import random

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

# Define global variables for SCADA system simulation
temperature = 25.0
pressure = 3.0
flow_rate = 10.0
valve_state = 1  # 1 = open, 0 = closed

def update_process():
    """Simulates the changes in the SCADA process"""
    global temperature, pressure, flow_rate
    
    while True:
        # Simulate process variable changes
        temperature += random.uniform(-0.5, 0.5)
        if temperature < 20:
            temperature = 20
        if temperature > 40:
            temperature = 40
            
        pressure += random.uniform(-0.1, 0.1)
        if pressure < 2.5:
            pressure = 2.5
        if pressure > 3.5:
            pressure = 3.5
            
        flow_rate += random.uniform(-0.5, 0.5)
        if flow_rate < 8:
            flow_rate = 8
        if flow_rate > 12:
            flow_rate = 12
            
        # Update the values in the ModbusContext
        store.setValues(3, 0, [int(temperature * 100)])
        store.setValues(3, 1, [int(pressure * 100)])
        store.setValues(3, 2, [int(flow_rate * 100)])
        
        log.info(f"SCADA Process: Temp={temperature:.2f}°C, Press={pressure:.2f}bar, Flow={flow_rate:.2f}L/s")
        time.sleep(1)

def run_server():
    """Run the Modbus server"""
    log.info("Starting Modbus Server")
    StartTcpServer(context, address=("0.0.0.0", 502))
    
if __name__ == "__main__":
    # Create datastore
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),  # Discrete Inputs
        co=ModbusSequentialDataBlock(0, [0]*100),  # Coils
        hr=ModbusSequentialDataBlock(0, [0]*100),  # Holding Registers
        ir=ModbusSequentialDataBlock(0, [0]*100)   # Input Registers
    )
    
    # Initialize with some values
    store.setValues(3, 0, [int(temperature * 100)])  # temperature in holding register 0
    store.setValues(3, 1, [int(pressure * 100)])     # pressure in holding register 1
    store.setValues(3, 2, [int(flow_rate * 100)])    # flow_rate in holding register 2
    store.setValues(1, 0, [valve_state])             # valve state in coil 0
    
    context = ModbusServerContext(slaves=store, single=True)
    
    # Start the simulation thread
    simulation_thread = threading.Thread(target=update_process)
    simulation_thread.daemon = True
    simulation_thread.start()
    
    # Run the server
    run_server()
