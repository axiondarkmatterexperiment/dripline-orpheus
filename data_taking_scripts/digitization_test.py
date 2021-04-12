from data_logging import DataLogger
from dripline.core import Interface
import sys

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'

the_interface = Interface(dripline_config={'auth-file': auths_file})

data_logger = DataLogger(auths_file)

rf_center_frequency =  16.5e9
if_center = 30e6
digitization_time = 30

data_logger.digitize(rf_center_frequency, if_center, digitization_time)
