from json.decoder import JSONDecodeError
from octoprint_sensordatavis import data_collector
import serial
import serial.tools.list_ports
import threading
import json
import time

class Data():
    def __init__(self) -> None:
        self.conn = None
        self.thread = None
        self.terminate_lock = threading.Lock()
        self.terminate = False
        self.logger = None

_dat = Data()

def stream_loop(msgQueue):
    _dat.logger.debug('[Arduino] Started Streaming...')
    if _dat.conn is None:
        _dat.logger.error('[Arduino] Not connected to an arduino...')
        return

    while True:
        with _dat.terminate_lock:
            if _dat.terminate:
                break
        
        line = _dat.conn.readline()
        if len(line) > 0:
            try:
                decoded_line = line.decode()
            except UnicodeDecodeError:
                _dat.logger.debug(f'[Arduino] Failed to decode utf-8: {line}')
                continue

            try:
                data = json.loads(decoded_line)
                # _dat.logger.debug(f'[Arduino] Successfully decoded json: {decoded_line}')
                for sensor in data['sensors']:
                    if 'lims_field' in sensor.keys():
                        data_collector.record_metric(sensor['lims_field'], sensor['value'])
                    if 'values' in sensor.keys():
                        for value in sensor['values']:
                            data_collector.record_metric(value['lims_field'], value['value'])
            except JSONDecodeError as err:
                _dat.logger.debug(f'[Arduino] Failed to decode json: {decoded_line}')
        
    _dat.conn.close()
    _dat.conn = None

def get_ports():
    ports = serial.tools.list_ports.comports()
    devices = map(lambda p : p.device, ports)
    return list(devices)

def start_streaming(port, baud, msgQueue, sensors, logger):
    if _dat.conn is not None:
        return
    _dat.logger = logger
    
    _dat.logger.debug(f'[Arduino] Attempting to connect to Arduino at: {port} : {baud}')
    _dat.conn = serial.Serial(port, baudrate=baud)
    if not _dat.conn.is_open:
        _dat.logger.debug(f'[Arduino] Failed to connect to port: {port}')

    with _dat.terminate_lock:
        _dat.terminate = False

    _dat.thread = threading.Thread(target=stream_loop, args=[msgQueue])
    _dat.thread.start()

def stop_streaming():
    if _dat.conn is None:
        return
    
    with _dat.terminate_lock:
        if not _dat.terminate:
            _dat.terminate = True