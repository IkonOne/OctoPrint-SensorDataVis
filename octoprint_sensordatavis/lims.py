import threading
import time
import queue
from solutionfamily.engine import Engine
from . import data_collector

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
    _lims.logger.debug('[LIMS] Started Streaming...')
    while True:
        with _lims.terminate_lock:
            if _lims.terminate:
                break
        
        time.sleep(1)

        values_to_set = dict()
        sensors = data_collector.get_summarized_readings()
        print(sensors)
        for key in sensors.keys():
            sensor = sensors[key]
            for metric in sensor:
                values_to_set[key + '.' + metric] = sensor[metric]
        
        print(values_to_set)
        if not _lims.engine.set_current_data_values(values_to_set):
            _lims.logger.debug(f'[LIMS] Failed to set values...\n{values_to_set}')

        # while msgQueue.not_empty:
        #     msg = msgQueue.get()
        #     values_to_set = dict()
        #     for sensor in msg:
        #         if 'lims_field' in sensor.keys() and 'value' in sensor.keys():
        #             values_to_set[sensor['lims_field']] = sensor['value']
        #         if 'values' in sensor.keys():
        #             values = sensor['values']
        #             for value in values:
        #                 if 'lims_field' in value.keys() and 'value' in value.keys():
        #                     values_to_set[value['lims_field']] = value['value']
        #     if not _lims.engine.set_current_data_values(values_to_set):
        #         _lims.logger.debug(f'[LIMS] Failed to set values...\n{values_to_set}')
    
    _lims.logger.debug('[LIMS] Stopped Streaming...')
    while msgQueue.not_empty:
        msgQueue.get_nowait()
    _lims.engine = None

def start_streaming(ip, port, logger):
    # if _lims.engine is not None:
    #     _lims.logger.debug('[LIMS] Stream already started.  Cannot start another...')
    #     return

    _lims.logger = logger

    _lims.logger.debug(f'[LIMS] Connecting to: http://{ip}:{port}')
    _lims.engine = Engine.fromurl(f'http://{ip}:{port}')

    _lims.thread = threading.Thread(target=stream_loop)
    _lims.thread.start()

def stop_streaming():
    if _lims.logger:
        _lims.logger.debug('[LIMS] Stopping streaming...')

    if _lims.engine is None:
        return
    
    with _lims.terminate_lock:
        _lims.terminate = True