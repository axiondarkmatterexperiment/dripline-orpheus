'''
If yfactor_measurement.py is running, then this script will effectively stop it. It basically sets  the endpoint 'yfactor_status' to 'stop_measurement'. yfactor_measurement.py is constantly querying this ednpoint and will exit it's while loop.
'''

from data_logging import DataLogger
from dripline.core import Interface
import sys

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'

the_interface = Interface(dripline_config={'auth-file': auths_file})

the_interface.set('yfactor_measurement_status', 'stop_measurement')
