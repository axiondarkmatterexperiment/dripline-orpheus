from data_logging import DataLogger
from dripline.core import Interface
import sys

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'

the_interface = Interface(dripline_config={'auth-file': auths_file})

def tone_with_vna(frequency, power):
    the_interface.set('na_center_freq', frequency)
    the_interface.set('na_freq_span', 0)
    the_interface.set('na_if_band', 0)
    the_interface.set('na_power', power)

data_logger = DataLogger(auths_file)

sampling_rate = 125e9
fft_size = 50e3
fft_bin_width = sampling_rate/fft_size
tone_frequency =  16.0742e9

if_center = 30e6
digitization_time = 30
target_tone_power = -15 #let's just be safe.


tone_with_vna(tone_frequency, target_tone_power)
data_logger.digitize(tone_frequency, if_center, digitization_time, fft_bin_width, log_power_monitor = True, disable_motors = True)
