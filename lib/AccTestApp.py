import logging
import time
import argparse

from lib.logging_config import logger
from lib.SerialDevice import SerialDevice
from lib.AccController import AccController


logger = logging.getLogger(__name__)


class AccTestApp:
    def __init__(self, param_dict):
        logger.info('Starting Serial Test App...')
        self.device = SerialDevice(
            port=param_dict['port'], baudrate=param_dict['baudrate'])
        self.protocol = None

        self.selectacc = param_dict['selectacc']
        self.accscale = param_dict['accscale']
        self.accodr = param_dict['accodr']
        self.acqnumsamples = param_dict['acqnumsamples']
        self.acqdecfactor = param_dict['acqdecfactor']
        self.acqtimsamplerate = param_dict['acqtimsamplerate']
        self.loop_times = param_dict['looptimes']

        if param_dict['acqodrrun']:
            self.acqodrrun = True
            self.acqtimerrun = False
        else:
            self.acqodrrun = False
            self.acqtimerrun = True

        self.acc = AccController(self.device,
                                 selectacc=self.selectacc,
                                 accscale=self.accscale,
                                 accodr=self.accodr,
                                 acqnumsamples=self.acqnumsamples,
                                 acqdecfactor=self.acqdecfactor,
                                 acqtimsamplerate=self.acqtimsamplerate)

    def init(self):
        self.acc.initialize_accelerometer()

    def run(self):
        for _ in range(self.loop_times):
            if self.acqodrrun:
                self.acc.run_data_acquisition_odr()
            if self.acqtimerrun:
                self.acc.run_data_acquisition_timer()

            sample_info = self.acc.download_sample_info()

            acc_data = self.acc.download_data()
            self.acc.save_to_file(sample_info, acc_data)

    def __del__(self):
        logger.info('MainApp finished.')
