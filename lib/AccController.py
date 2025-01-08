import logging
import time
from collections import namedtuple
import math
import numpy as np
from scipy.fft import fft

from lib.DeviceProtocol import DeviceProtocol
from lib.logging_config import logger
from lib.utils import measure_time


logger = logging.getLogger(__name__)


class AccController:
    ACC_NAMES = {
    }

    def __init__(self,
                 serial_device,
                 selectacc: int,
                 accscale: int,
                 accodr: int,
                 acqnumsamples: int,
                 acqdecfactor: int,
                 acqtimsamplerate: int):

        self.acc_id = selectacc
        self.scale = accscale
        self.odr = accodr
        self.num_samples = acqnumsamples
        self.decimation_factor = acqdecfactor
        self.timer_sample_rate = acqtimsamplerate

        self.protocol = DeviceProtocol(serial_device)

     
    @measure_time
    def initialize_accelerometer(self):
        logger.info('Initializing accelerometer...')
        if self.protocol.check_connection():
            try:
                self.protocol.select_accelerometer(self.acc_id)
                self.protocol.set_accelerometer_scale(self.scale)
                self.protocol.set_accelerometer_odr(self.odr)
                self.protocol.set_num_samples_to_acquire(self.num_samples)
                self.protocol.set_decimation_factor(self.decimation_factor)
                self.protocol.set_timer_sample_rate(self.timer_sample_rate)

                self.protocol.init_accelerometer()

            except Exception as e:
                logger.error(f'Error initializing accelerometer: {e}')
                raise e
        else:
            logger.error('Error connecting to device.')
            raise Exception('Error connecting to device.')

    def change_spi_speed(self, new_spi_speed):
        try:
            self.protocol.override_acc_spi_speed(new_spi_speed)
            self.protocol.init_accelerometer()
        except Exception as e:
            logger.error(f'Error changing SPI speed: {e}')
            raise e

    @measure_time
    def run_data_acquisition_odr(self):
        logger.info('Running data acquisition with ODR...')
        self.protocol.run_data_acquisition_odr()

    @measure_time
    def run_data_acquisition_timer(self):
        logger.info('Running data acquisition with timer...')
        self.protocol.run_data_acquisition_timer()

    @measure_time
    def download_data(self):
        logger.info('Downloading data...')
        try:
            num_batches = self.num_samples // 32
            if self.num_samples % 32:
                num_batches += 1

            samples_x = []
            samples_y = []
            samples_z = []

            for current_batch in range(num_batches):
                sample_buffer = self.protocol.get_sample_batch(current_batch)

                if not sample_buffer:
                    raise Exception('Error downloading data.')
                for samples in sample_buffer:
                    samples_x.append(samples[0])
                    samples_y.append(samples[1])
                    samples_z.append(samples[2])

            return samples_x, samples_y, samples_z

        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            raise e

    @measure_time
    def download_sample_info(self):
        try:
            sample_info = self.protocol.get_sample_info()
            return sample_info
        except Exception as e:
            logger.error(f"Error downloading sample info: {e}")
            raise e

    @measure_time
    def save_to_file(self, sample_info: namedtuple, acc_data: tuple, filename: str = '') -> bool:
        """
        Saves accelerometer data to a CSV file with metadata and sample values.
        """
        logger.info("Saving data to file...")
        if sample_info.accelerometer_id in self.ACC_NAMES:
            acc_name = self.ACC_NAMES.get(
                sample_info.accelerometer_id, "unknown")
            bits_per_sample = 16
        else:
            acc_name = sample_info.accelerometer_id
            bits_per_sample = None  # Default if not defined

        if not filename:
            filename = f"{acc_name}_data_{time.strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 1000}.csv"

        try:
            with open(filename, "w") as out:
                # Write header
                out.write("accelerometer;frequency[Hz];num_of_samples\n")
                out.write(f"{acc_name};")

                # Write sampling frequency and number of samples
                out.write(
                    f"{sample_info.sampling_frequency:.2f};{sample_info.num_of_acq_samples}\n")
                out.write("scale[g];bits_per_sample;acquisition_time[ms]\n")

                # Determine scale
                scale_mapping = {0: 2, 1: 4, 2: 8, 3: 16}
                scale = scale_mapping.get(
                    sample_info.accelerometer_scale, None)
                if scale is not None:
                    out.write(f"{scale};")
                else:
                    out.write("unknown;")

                # Write bits per sample and acquisition time
                out.write(
                    f"{bits_per_sample};{sample_info.acquisition_time}\n")
                out.write("x;y;z\n")

                # Write sample data
                for x, y, z in zip(*acc_data):
                    out.write(f"{int(x)};{int(y)};{int(z)}\n")

            return True
        except Exception as e:
            logger.error(f"Error saving data to file: {e}")
            raise e





    # def calculate_rms_velocity(self, sample_info: namedtuple, acc_data: tuple):

    #     # def _axis_calc_rms_velocity(samples):
    #     #     return math.sqrt(sum(x ** 2 for x in samples) / len(samples))

    #     # Funkcja okna Hanninga
    #     def hann_window(data):
    #         return data * np.hanning(len(data))

    #     # Funkcja do obliczania RMS prędkości w pasmach częstotliwości
    #     def calc_rms_velocity(amplitude_array, freq_low, freq_high, sampling_frequency):
    #         # Obliczenie zakresu indeksów odpowiadających częstotliwościom
    #         low_index = int(freq_low * len(amplitude_array) / sampling_frequency)
    #         high_index = int(freq_high * len(amplitude_array) / sampling_frequency)

    #         # Obliczenie RMS w danym zakresie częstotliwości
    #         rms = np.sqrt(np.mean(np.square(amplitude_array)))
    #         return rms

    #     # Funkcja do obliczania RMS prędkości na podstawie danych
    #     def _axis_calc_rms_velocity(input_data, sampling_frequency, rms_vel_calc_freq_low, rms_vel_calc_freq_high):
    #         # Krok 1: Zastosowanie okna Hanninga
    #         windowed_data = hann_window(input_data)

    #         # Krok 2: FFT na oknie danych
    #         N = len(windowed_data)
    #         fft_output = fft(windowed_data)
    #         # Amplituda (moduł FFT)
    #         amplitude_array = np.abs(fft_output[:N//2])  # Bierzemy tylko pierwszą połowę (połowa pasma Nyquista)

    #         # Krok 3: Obliczanie RMS prędkości w określonym paśmie częstotliwości
    #         rms_velocity = calc_rms_velocity(amplitude_array, rms_vel_calc_freq_low, rms_vel_calc_freq_high, sampling_frequency)

    #         # Krok 4: Skalowanie RMS (jeśli wymagane)
    #         rms_velocity *= 1.63  # Skala może być dostosowana w zależności od kalibracji

    #         return rms_velocity

    #     try:
    #         scale_factors = {0: 2.0, 1: 4.0, 2: 8.0, 3: 16.0}
    #         max_ms2 = scale_factors.get(sample_info.accelerometer_scale, None)
    #         if max_ms2 is None:
    #             raise Exception("max_ms2 is None")

    #         scale_factor = (1.0 / 32768.0) * max_ms2

    #         # Przekształcenie próbek przyspieszenia do jednostek "g"
    #         samples_x_scaled = [x * scale_factor for x in acc_data[0]]
    #         samples_y_scaled = [y * scale_factor for y in acc_data[1]]
    #         samples_z_scaled = [z * scale_factor for z in acc_data[2]]

    #         rms_vel_calc_freq_low = 0.1  # Dolna granica pasma częstotliwości (Hz)
    #         rms_vel_calc_freq_high = 1000  # Górna granica pasma częstotliwości (Hz)

    #         # Obliczanie RMS dla każdej osi
    #         rms_vx = _axis_calc_rms_velocity(samples_x_scaled, sample_info.sampling_frequency, rms_vel_calc_freq_low, rms_vel_calc_freq_high)
    #         rms_vy = _axis_calc_rms_velocity(samples_y_scaled, sample_info.sampling_frequency, rms_vel_calc_freq_low, rms_vel_calc_freq_high)
    #         rms_vz = _axis_calc_rms_velocity(samples_z_scaled, sample_info.sampling_frequency, rms_vel_calc_freq_low, rms_vel_calc_freq_high)

    #         print(f"RMS velocity: {rms_vx:.5f} {rms_vy:.5f} {rms_vz:.5f}")
    #         return rms_vx, rms_vy, rms_vz

    #     except Exception as e:
    #         logger.error(f"Error calculating RMS velocity: {e}")
    #         raise e
