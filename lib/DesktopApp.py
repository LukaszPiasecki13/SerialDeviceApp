import tkinter as tk
from tkinter import ttk
import logging

from lib.AccTestApp import AccTestApp
from lib.logging_config import logger


logger = logging.getLogger(__name__)


class DesktopApp:
    def __init__(self, root):
        logger.info('Starting Desktop App...')
        self.param_dict = {}
        self.root = root
        self.root.title("Acc test app")

        # Parametry
        self.params = {
            "port": tk.StringVar(value="COM8"),
            "Baudrate": tk.IntVar(value=230400),
            "SelectAcc": tk.IntVar(value=1),
            "AccScale": tk.IntVar(value=2),
            "AccODR": tk.IntVar(value=0),
            "AcqNumSamples": tk.IntVar(value=1024),
            "AcqDecFactor": tk.IntVar(value=1),
            "AcqTimSampleRate": tk.IntVar(value=8000),
            "AcqODRRun": tk.BooleanVar(value=False),
            "AcqTimerRun": tk.BooleanVar(value=True),
            "LoopTimes": tk.IntVar(value=1)
        }

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        row = 0
        for param, var in self.params.items():
            ttk.Label(frame, text=param).grid(
                row=row, column=0, sticky="w", padx=5, pady=5)

            if isinstance(var, tk.BooleanVar):
                check_button = ttk.Checkbutton(
                    frame, variable=var, command=self.update_check_buttons)
                check_button.grid(row=row, column=1,
                                  sticky="w", padx=5, pady=5)
            elif isinstance(var, tk.IntVar):
                if "baudrate" in param.lower():
                    ttk.Combobox(frame, textvariable=var, values=[230400]).grid(
                        row=row, column=1, sticky="w", padx=5, pady=5)
                if "selectacc" in param.lower():
                    ttk.Combobox(frame, textvariable=var, values=[1, 2, 3, 4]).grid(
                        row=row, column=1, sticky="w", padx=5, pady=5)
                if "accscale" in param.lower():
                    ttk.Combobox(frame, textvariable=var, values=[0, 1, 2, 3]).grid(
                        row=row, column=1, sticky="w", padx=5, pady=5)
                else:
                    ttk.Entry(frame, textvariable=var, width=20).grid(
                        row=row, column=1, sticky="w", padx=5, pady=5)
            else:
                ttk.Entry(frame, textvariable=var, width=20).grid(
                    row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1

        self.run_button = ttk.Button(
            frame, text="Run", command=self.run_application)
        self.run_button.grid(row=row, column=0, columnspan=2, pady=10)

    def update_check_buttons(self):
        """
        Function to update check buttons
        """
        if self.params["AcqODRRun"].get():
            self.params["AcqTimerRun"].set(False)
        elif self.params["AcqTimerRun"].get():
            self.params["AcqODRRun"].set(False)

    def run_application(self):
        self.run_button.config(state="disabled", text="Running...")
        init = False

        param_dict = {param.lower(): var.get()
                      for param, var in self.params.items()}
        if self.param_dict == param_dict:
            init = False
        else:
            self.param_dict = param_dict
            init = True

        app = AccTestApp(self.param_dict)
        self.root.after(100, lambda: self.execute_task(app, init))

    def execute_task(self, app, init:bool):
        try:
            if init:
                app.init()

            app.run()
        finally:
            self.run_button.config(state="normal", text="Run")

    def __del__(self):
        logger.info('Desktop App finished.')


if __name__ == "__main__":
    root = tk.Tk()
    window_app = DesktopApp(root)
    root.mainloop()
