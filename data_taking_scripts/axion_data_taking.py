from motor import OrpheusMotors
from data_logging import DataLogger
import numpy as np
from scipy import interpolate
import yaml
from dripline.core import Interface
import logging
logging.basicConfig(level=logging.INFO)
dl_logger = logging.getLogger(__name__)

def cm_to_inch(dist):
    return dist/2.54
def inch_to_cm(dist):
    return dist*2.54

#configure data taking
config_file = open("axion_data_taking_config.yaml")
configs = yaml.load(config_file, Loader =yaml.FullLoader)
general_mechanical_configs = configs['general_configs']
list_of_keys = list(configs["measurement_configs"].keys())
locals().update(general_mechanical_configs)
print("  Configurations  ")
for i in range(len(list_of_keys)):
    print(F"{i}  {list_of_keys[i]}")
picked_config = int(input(F"Pick you configuration (0 - {len(list_of_keys)-1}): "))
locals().update(configs['measurement_configs'][list_of_keys[picked_config]])

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

#set up motors and data_logger
orpheus_motors = OrpheusMotors(auths_file, motors_to_move)
data_logger = DataLogger(auths_file)

data_logger.initialize_na_settings_for_modemap(averages = averages, average_enable = average_enable, power = vna_power, sweep_points = sweep_points)

#send alert saying you're starting axion data taking
data_logger.start_axion_data_taking()

current_resonator_length_cm = initial_mirror_holder_spacing+1.05
current_resonator_length_in = cm_to_inch(current_resonator_length_cm)
current_plate_separation = orpheus_motors.plate_separation(current_resonator_length_in,num_plates)

the_interface.set('target_fo', starting_fo)

try:
    delta_length = 0
    print('Resonator length: {}'.format(current_resonator_length_cm))
    while delta_length < abs(distance_to_move):
#take transmission measurement
        data_logger.log_transmission_switches(wide_scan_start_freq, wide_scan_stop_freq, sec_wait_for_na_averaging, 'axion data taking. widescan')

        target_fo = the_interface.get('target_fo').payload.to_python()['value_cal']
        print(target_fo)
        #get frequency span for narrowscan
        narrow_scan_start_freq = target_fo - narrow_scan_span_guess/2
        narrow_scan_stop_freq = target_fo + narrow_scan_span_guess/2
        resonant_freq_guess = data_logger.guess_resonant_frequency(narrow_scan_start_freq, narrow_scan_stop_freq, averaging_time = averaging_time_for_fo_guess_measurement)
        narrow_scan_start_freq_focus = resonant_freq_guess-narrow_scan_span_focus/2
        narrow_scan_stop_freq_focus = resonant_freq_guess+narrow_scan_span_focus/2

        #log narrowscan transmission
        data_logger.log_transmission_switches(narrow_scan_start_freq_focus, narrow_scan_stop_freq_focus, sec_wait_for_na_averaging, 'axion data taking. narrowscan', fitting = True)

        # log reflection measurements
        data_logger.log_reflection_switches(wide_scan_start_freq, wide_scan_stop_freq, sec_wait_for_na_averaging, 'axion data taking. widescan')
        data_logger.log_reflection_switches(narrow_scan_start_freq_focus, narrow_scan_stop_freq_focus, sec_wait_for_na_averaging, 'axion data taking. narrowscan', fitting = True)

        #take axion data
        measured_fo = the_interface.get('f_transmission').payload.to_python()['value_cal']
        data_logger.digitize(measured_fo, if_center, digitization_time)

        #adjust target fo
        the_interface.set('target_fo', measured_fo)

        #move plates
        current_resonator_length_in, new_plate_separation = orpheus_motors.move_by_increment(increment_distance,
                                                                                             current_resonator_length_in,
                                                                                             num_plates,
                                                                                             current_plate_separation)
        orpheus_motors.wait_for_motors()
        current_resonator_length_cm = current_resonator_length_cm+inch_to_cm(increment_distance)

        the_interface.set('resonator_length', current_resonator_length_cm) #logging resonator length into endpoint
        current_plate_separation = new_plate_separation
        dl_logger.info("plate separation: {}".format(current_plate_separation))

except KeyboardInterrupt:
    dl_logger.info('stopping motors and modemap measurement')
    orpheus_motors.stop_and_kill()
    data_logger.start_axion_data_taking()

data_logger.turn_off_all_switches()

# send alert saying that you are stopping axion data taking.
data_logger.stop_axion_data_taking()
