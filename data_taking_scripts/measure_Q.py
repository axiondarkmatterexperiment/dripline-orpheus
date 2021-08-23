'''
Measures the transmission loaded Q, reflection loaded Q, antenna coupling, and reflection unloaded Q. Assumes that the VNA is centered around a mode of interest. Assumes you will be interactive with the VNA manually and that you are using this script just for fitting.
'''
from data_logging import DataLogger
from dripline.core import Interface

auths_file = '/etc/rabbitmq-secret/authentications.json'
data_logger = DataLogger(auths_file)

the_interface = Interface(dripline_config={'auth-file': auths_file})

start_freq = the_interface.get('na_start_freq').payload.to_python()['value_cal']
stop_freq = the_interface.get('na_stop_freq').payload.to_python()['value_cal']

data_logger.log_transmission_switches(start_freq,stop_freq, 1, fitting = True, transmission_endpoint = 's21_iq_transmission_data')

data_logger.log_reflection_switches(start_freq, stop_freq, 1, fitting = True, reflection_endpoint = 's21_iq_reflection_data')


