import logging
import sys

import arduino
import config
import data_collector
import lims
import rawData

def main():
    logger = logging.getLogger('my.arduino')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    data_collector._logger = logger

    arduino.start_streaming(
        config.ARDUINO_PORT,
        config.ARDUINO_BAUD, 
        None,
        None,
        logger
    )

    # lims.start_streaming(
    #     config.LIMS_IP,
    #     config.LIMS_PORT,
    #     config.LIMS_ENDPOINT,
    #     logger
    # )
    
    rawData.start_streaming(
        config.LIMS_IP,
        config.LIMS_PORT,
        config.LIMS_ENDPOINT,
        logger
    )

if __name__ == '__main__':
    main()
