import threading
import time
import queue
from solutionfamily.engine import Engine
import data_collector
from api_oprint import APIOctoPrint
import config
import time

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
    api = APIOctoPrint(api_url=config.API_URL, api_secret=config.API_SECRET)
    j = api.get_api_job()
    j['job']['file']['name'] = 'lewis.lewis' #delete me
    dotIndex = j['job']['file']['name'].index('.')
    timeStamp = time.strftime("%Y%m%d-%H%M%S")
    fileName = 'data/' + j['job']['file']['name'][0:dotIndex] + timeStamp + '.csv'
    values_to_set = data_collector.get_summarized_readings()
    with open(fileName, 'w') as file:
        for key in values_to_set.keys():
            file.write("%s,"%key)
        file.write("\n")
    file.close()
    var = 0
    while var<4:

        with _raw.terminate_lock:
            if _raw.terminate:
                break
        
        time.sleep(1)


        r = api.get_api_printer()
        state_flags = r['state']['flags']
        print(state_flags)
        state_flags['printing']=True#delete me
        if(state_flags['printing']==True):
            # values_to_set = dict()
            # sensors = data_collector.get_summarized_readings()
            values_to_set = data_collector.get_summarized_readings()
            _raw.logger.debug(f'[RawData] Sending data to file: {values_to_set}')
            with open(fileName, 'a') as file:
                for key in values_to_set.keys():
                    file.write("%s," % (values_to_set[key]))
                file.write("\n")
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