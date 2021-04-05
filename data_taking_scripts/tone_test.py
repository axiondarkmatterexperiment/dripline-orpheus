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

logger = DataLogger(auths_file)

vna_power_limits = [-15, -5]
gain = 16 #dB
tone_frequency =  16.5e9
if_center = 30e6
digitization_time = 30
#target_tone_power = 28-gain #aim for 28 dBm at digitizer input. Do not exceed 34 dBm at digitizer input.
target_tone_power = -15 #let's just be safe.


tone_with_vna(tone_frequency, target_tone_power)
logger.digitize(tone_frequency, if_center, digitization_time)
