import threading
import queue
from solutionfamily.engine import Engine

class Lims():
    def __init__(self) -> None:
        self.engine = None
        self.port = -1
        self.ip = None
        self.thread = None
        self.logger = None
        self.terminate = False
        self.terminate_lock = threading.Lock()

_lims = Lims()
msgQueue = queue.Queue()

def stream_loop():
    while True:
        with _lims.terminate_lock:
            if _lims.terminate:
                break

        while msgQueue.not_empty:
            msg = msgQueue.get()
            values_to_set = dict()
            for sensor in msg:
                values_to_set[sensor['lims_field']] = sensor['value']
            # values_to_set = {
            #     'Facility.Sensors.FilamentDiameter': msg[''],
            # }
            _lims.engine.set_current_data_values(values_to_set)
            if _lims.logger is not None:
                _lims.logger.info(msg)
    
    while msgQueue.not_empty:
        msgQueue.get_nowait()
    _lims.engine = None

def start_streaming(ip, port, logger=None):
    if _lims.engine is not None:
        return
    
    _lims.logger = logger
    _lims.engine = Engine.fromurl(f'http://{ip}:{port}')
    _lims.thread = threading.Thread(target=stream_loop)
    _lims.thread.start()

def stop_streaming():
    if _lims.engine is None:
        return
    
    with _lims.terminate_lock:
        _lims.terminate = True