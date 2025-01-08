import serial
import logging
import time
import struct

from lib.logging_config import logger


logger = logging.getLogger(__name__)


class SerialDevice:

    def __init__(self, port:str, baudrate:int, timeout:int=0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            logger.debug(f'Connected to {self.port}')

        except serial.SerialException as e:
            logger.error(f'Error connecting to {self.port}: {e}')


    def disconnect(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.debug(f'Disconnected from {self.port}')


    def send(self, message:str, timeout):
        if not self.connection or not self.connection.is_open:
            logger.error('Attempt to send while serial port not connected.')
            raise Exception('Serial port not connected.')
        self.connection.write(message.encode())
        logger.debug(f'Sent: {message.strip()}')
        time.sleep(timeout)

    def receive(self):
        if not self.connection or not self.connection.is_open:
            logger.error('Attempt to send while serial port not connected.')
            raise Exception('Serial port not connected.')
        response = self.connection.readline().decode().strip()
        logger.debug(f'Received: {response}\n')
        return response
    
    def receive_package(self):
        if not self.connection or not self.connection.is_open:
            logger.error('Attempt to send while serial port not connected.')
            raise Exception('Serial port not connected.')

        for i in range(500):
            if self.connection.in_waiting >= 196:
                break
            time.sleep(0.0001)

        response = self.connection.read_all()       
        messages = response.split(b'\n')
        if messages == b':er':
            logger.error(f'Received: {messages[0]}')
        elif not messages :
            logger.error(f'Received: {response}')
        else:
            logger.debug(f'Received: {messages[0]} + data(not writed here)\n')
    
        return response