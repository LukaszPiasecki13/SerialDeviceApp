import logging
import struct
import time
from collections import namedtuple

from lib.logging_config import logger
from lib.SerialDevice import SerialDevice

logger = logging.getLogger(__name__)


class DeviceProtocol:
    INIT_ACC_TIMEOUT_S = 1
    DATA_ACQUISITION_MAX_TIME_S = 1 * 60 * 10

    def __init__(self, serial_device: SerialDevice):
        self.serial_device = serial_device
        self.serial_device.connect()

    def _send_command(self, command: str, timeout: int = 0.3, batch_download: bool = False) -> str:
        self.serial_device.send(command, timeout)
        if not batch_download:
            for _ in range(40):
                # max time 10s
                response = self.serial_device.receive()
                if not response:
                    time.sleep(0.25)
                else: 
                    break
        else:
            response = self.serial_device.receive_package()
        return response

    def get_firmware_version(self):
        '''
        Returns the firmware version of the device.

        Returns:
            str: The firmware version of the device.

        '''
        return "An response"

    def check_connection(self) -> bool:
        return False

    def select_accelerometer(self, acc_id):
        """
        Selects the accelerometer by its ID.

        """
        return "An response"

    def override_acc_spi_speed(self, ovr_acc_spi_speed):
        """
        Overrides the SPI speed of the accelerometer.

        """
        return "An response"

    def set_accelerometer_scale(self, scale):
        """
        Sets the scale of the accelerometer.

        """
        return "An response"

    def set_accelerometer_odr(self, odr):
        """
        Sets the Output Data Rate (ODR) of the accelerometer.

        """
        return "An response"

    def set_num_samples_to_acquire(self, num_samples):
        """
        Sets the number of samples the accelerometer should acquire.

        """
        return "An response"

    def set_decimation_factor(self, decimation_factor):
        """
        Sets the decimation factor for the accelerometer's data acquisition.

        """
        return "An response"

    def set_timer_sample_rate(self, timer_sample_rate):
        """
        Sets the sample rate for the timer-based data acquisition.

        """
        return "An response"

    def init_accelerometer(self):
        """
        Initializes the accelerometer. Before that, you need to set the parameters.

        """
        return "An response"

    def run_data_acquisition_odr(self):
        return "An response"

    def run_data_acquisition_timer(self):
        return "An response"
    
    def get_sample_batch(self, sample_batch_no) -> list:
        """
        Returns a batch of samples from the device.
        
        """

        return []

    def get_sample_info(self) -> namedtuple:
        '''
        Returns the sample info of the device.

        '''
        return "An response"

    def __del__(self):
        self.serial_device.disconnect()
