import threading
import time
import queue
from solutionfamily.engine import Engine
import data_collector
import csv

class RawData():
    def __init__(self) -> None:
        self.engine = None
        self.port = -1
        self.ip = None
        self.endpoint = None
        self.thread = None
        self.logger = None
        self.terminate = False
        self.terminate_lock = threading.Lock()

_raw = RawData()
msgQueue = queue.Queue()

def stream_loop():
    _raw.logger.debug('[RAW DATA] Started Streaming...')
    var = 0
    while var < 10:
        with _raw.terminate_lock:
            if _raw.terminate:
                break
        
        time.sleep(1)
        
        # values_to_set = dict()
        # sensors = data_collector.get_summarized_readings()
        values_to_set = data_collector.get_summarized_readings()
        _raw.logger.debug(f'[RawData] Sending data to file: {values_to_set}')
        with open('./data.csv', 'a') as file:
            for key in values_to_set.keys():
                file.write("%s, %s\n" % (key, values_to_set[key]))
        file.close()
        var+=1

    _raw.logger.debug('[RawData] Stopped Streaming...')
    while not msgQueue.empty():
        msgQueue.get_nowait()
    _raw.engine = None

def start_streaming(ip, port, endpoint, logger):
    # if _raw.engine is not None:
    #     _raw.logger.debug('[RawData] Stream already started.  Cannot start another...')
    #     return

    _raw.logger = logger

    _raw.logger.debug(f'[RawData] Connecting to: http://{ip}:{port}')
    _raw.engine = Engine.fromurl(f'http://{ip}:{port}')

    with _raw.terminate_lock:
        _raw.terminate = False

    _raw.thread = threading.Thread(target=stream_loop)
    _raw.thread.start()

def stop_streaming():
    if _raw.logger:
        _raw.logger.debug('[RawData] Stopping streaming...')

    if _raw.engine is None:
        return
    
    with _lims.terminate_lock:
        _lims.terminate = True