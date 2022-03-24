#!/usr/bin/env python3

import time
import logging
import sys
from solutionfamily.engine import Engine

LIMS_ADDR = "http://192.168.0.190:8080"
VALUE_KEY = "Facility.TargetValue"

def main(sleepTime):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)

    logger.info(f'Starting the stream...')

    value_count = 0
    engine = Engine.fromurl(LIMS_ADDR)
    logging.info(f'Connected to LIMS engnine at: {LIMS_ADDR}')

    while True:
        values_to_set = { VALUE_KEY: value_count }
        value_count += 1

        try:
            engine.set_current_data_values(values_to_set)
            logger.info(f'Successfully update values: {values_to_set}')
        except Exception as e:
            logger.exception(f'Failed to set values: {values_to_set}')

        time.sleep(sleepTime)


if __name__ == '__main__':
    sleepTime = 1.0
    if len(sys.argv) > 1:
        print(sys.argv)
        sleepTime = float(sys.argv[1])

    main(sleepTime)