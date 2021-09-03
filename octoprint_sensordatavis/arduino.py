import serial
import serial.tools.list_ports

def get_arduino_ports():
    ports = serial.tools.list_ports.comports()
    devices = map(lambda p : p.device, ports)
    return list(devices)