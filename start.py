import logging
import time
import argparse
import tkinter as tk
from tkinter import ttk

from lib.logging_config import logger
from lib.SerialDevice import SerialDevice
from lib.AccController import AccController
from lib.AccTestApp import AccTestApp
from lib.DesktopApp import DesktopApp


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="MainApp for data acquisition")

    parser.add_argument('--desktop', action='store_true',
                        help='Flag to indicate desktop mode (default: False)')

    parser.add_argument('--port', type=str, default='COM8',
                        required=True, help='Port for SerialDevice (default: COM8)')
    parser.add_argument('--baudrate', type=int, default=230400,
                        required=True, help='Baudrate for SerialDevice (default: 230400)')

    parser.add_argument('--selectacc', type=int, default=1,
                        required=True, help='Select accelerometer (default: 1)')
    parser.add_argument('--accscale', type=int, default=1,
                        required=True, help='Accelerometer scale (default: 1)')
    parser.add_argument('--accodr', type=int, default=0,
                        help='Accelerometer ODR (default: 0)')
    parser.add_argument('--acqnumsamples', type=int, default=1024*8,
                        required=True, help='Number of samples to acquire (default: 8192)')
    parser.add_argument('--acqdecfactor', type=int, default=1,
                        required=True, help='Decimation factor (default: 1)')
    parser.add_argument('--acqtimsamplerate', type=int,
                        required=True, default=8000, help='Sampling rate in Hz (default: 8000)')

    parser.add_argument('--acqodrrun', action='store_true')
    parser.add_argument('--acqtimerrun', action='store_true')
    parser.add_argument('--looptimes', type=int, default=1)

    args = parser.parse_args()

    if not args.desktop:
        required_args = ['port', 'baudrate', 'selectacc', 'accscale', 'acqnumsamples', 'acqdecfactor', 'acqtimsamplerate']
        missing_args = [arg for arg in required_args if getattr(args, arg) is None]
        if missing_args:
            parser.error(f"The following arguments are required in non-desktop mode: {', '.join(missing_args)}")

        param_dict = vars(parser.parse_args())

        logger.info('Running in embedded mode.')
        app = AccTestApp(param_dict)
        app.init()
        app.run()

    else:
        root = tk.Tk()
        app = DesktopApp(root)
        root.mainloop()


