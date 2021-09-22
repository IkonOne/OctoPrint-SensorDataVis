import serial
import serial.tools.list_ports
import threading
import json

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
        return

    while True:
        with _dat.terminate_lock:
            if _dat.terminate:
                break
        
        line = _dat.conn.readline()
        data = json.loads(line)
        msgQueue.put(data['sensors'])
        # _dat.logger.debug(f'Arduino: {data}')
        
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
    
    _dat.logger.debug('Attempting to connect to Arduino at: {0} : {1}'.format(port, baud))
    _dat.conn = serial.Serial(port, baudrate=baud, timeout=5)

    formatted_sensors = dict({'sensors': sensors})
    _dat.logger.debug('[Arduino] Sending sensor config: {0}'.format(formatted_sensors))
    _dat.conn.write(str(formatted_sensors).encode('utf8'))
    _dat.conn.write(b'\n')
    _dat.thread = threading.Thread(target=stream_loop, args=[msgQueue])
    _dat.thread.start()

def stop_streaming():
    if _dat.conn is None:
        return
    
    with _dat.terminate_lock:
        if not _dat.terminate:
            _dat.terminate = True