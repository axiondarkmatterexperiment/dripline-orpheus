from data_logging import DataLogger
from dripline.core import Interface
import sys

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'

the_interface = Interface(dripline_config={'auth-file': auths_file})

data_logger = DataLogger(auths_file)

sampling_rate = 125e9
fft_size = 50e3
fft_bin_width = sampling_rate/fft_size

rf_center_frequency =  16.147e9
if_center = 29.5e6

data_logger.digitize(rf_center_frequency, if_center, fft_bin_width, log_power_monitor = True, disable_motors = True)
