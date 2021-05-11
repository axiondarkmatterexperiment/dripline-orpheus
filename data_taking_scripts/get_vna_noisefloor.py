from data_logging import DataLogger
from dripline.core import Interface
import numpy as np

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'

the_interface = Interface(dripline_config={'auth-file': auths_file})

data_logger = DataLogger(auths_file)

data_logger.switch_digitization_path()

noise_floor_voltage = the_interface.get('s21_iq_transmission_data').payload.to_python()['value_cal']
the_interface.cmd('s21_iq_transmission_data', 'scheduled_log')

print(np.std(noise_floor_voltage))
