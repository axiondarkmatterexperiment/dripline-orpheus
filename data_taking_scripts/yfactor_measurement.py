'''
Takes y-factor measurement.
Sets IF frequency to be a few bandwidths away from the TEM-00-18 mode.
Assumes that the VNA has the TEM mode in view.
Records transfer function with fitted parameters.

'''
from data_logging import DataLogger
from dripline.core import Interface
import sys
import numpy as np

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'

the_interface = Interface(dripline_config={'auth-file': auths_file})

data_logger = DataLogger(auths_file)

sampling_rate = 125e9
fft_size = 50e3
fft_bin_width = sampling_rate/fft_size

rf_center_frequency =  17.0e9 #choose something off resonance with the TEM_00-18 mode, maybe by 2 bandwidths
if_center = 29.5e6
digitization_time = 30

data_logger.start_yfactor_measurement('test')

start_freq = the_interface.get('na_start_freq').payload.to_python()['value_cal']
stop_freq = the_interface.get('na_stop_freq').payload.to_python()['value_cal']

while the_interface.get('yfactor_measurement_status').payload.to_python()['value_cal'] == 'start_measurement':
    data_logger.digitize(rf_center_frequency, if_center, digitization_time, fft_bin_width, log_power_monitor = True, disable_motors = True, keep_vna_off = False)
    data_logger.log_transmission_switches(start_freq,stop_freq, 1, fitting = True, transmission_endpoint = 's21_iq_transmission_data', track_max_s21=True)
    
