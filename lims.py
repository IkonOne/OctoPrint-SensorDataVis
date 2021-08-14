import threading
import time
import queue
from solutionfamily.engine import Engine
import data_collector

class Lims():
    def __init__(self) -> None:
        self.engine = None
        self.port = -1
        self.ip = None
        self.endpoint = None
        self.thread = None
        self.logger = None
        self.terminate = False
        self.terminate_lock = threading.Lock()

_lims = Lims()
msgQueue = queue.Queue()

def stream_loop():
    _lims.logger.info('[LIMS] Started Streaming...')
    while True:
        with _lims.terminate_lock:
            if _lims.terminate:
                break
        
        time.sleep(0.5)

        # values_to_set = dict()
        # sensors = data_collector.get_summarized_readings()
        try:
            values_to_set = data_collector.get_summarized_readings()
            _lims.logger.debug(f'[LIMS] Sending data to lims: {values_to_set}')

            if not _lims.engine.set_current_data_values(values_to_set):
                _lims.logger.debug(f'[LIMS] Failed to set values...\n{values_to_set}')
            else:
                data_collector.clear_summarized_readings()
        except Exception as e:
            _lims.logger.exception(f'[LIMS] Exeception thrown while sending data to LIMS box...')
    
    _lims.logger.info('[LIMS] Stopped Streaming...')
    while not msgQueue.empty():
        msgQueue.get_nowait()
    _lims.engine = None

def start_streaming(ip, port, endpoint, logger):
    # if _lims.engine is not None:
    #     _lims.logger.debug('[LIMS] Stream already started.  Cannot start another...')
    #     return

    _lims.logger = logger

    _lims.logger.info(f'[LIMS] Connecting to: http://{ip}:{port}')
    _lims.engine = Engine.fromurl(f'http://{ip}:{port}')

    with _lims.terminate_lock:
        _lims.terminate = False

    _lims.thread = threading.Thread(target=stream_loop)
    _lims.thread.name = 'LIMS'
    _lims.thread.start()

def stop_streaming():
    if _lims.logger:
        _lims.logger.info('[LIMS] Stopping streaming...')

    if _lims.engine is None:
        return
    
    with _lims.terminate_lock:
        _lims.terminate = True
