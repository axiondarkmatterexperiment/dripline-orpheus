from motor import OrpheusMotors
from data_logging import DataLogger
import numpy as np
from scipy import interpolate
import yaml
from dripline.core import Interface
import logging
logging.basicConfig(level=logging.INFO)
dl_logger = logging.getLogger(__name__)

config_file = open("config.yaml")
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

def cm_to_inch(dist):
    return dist/2.54
def inch_to_cm(dist):
    return dist*2.54

#distance_to_move = float(input('Enter the distance to move in cm (Empty resonator modemap is usually 3): '))
#resolution = int(input('Enter the number of measurements needed: '))
increment_distance = cm_to_inch(distance_to_move/number_of_measurement_points)

if narrow_scan:
    resonances_and_lengths = np.loadtxt(ifile_predicted_resonances, skiprows = 1,delimiter = ',')
    predicted_lengths = resonances_and_lengths[:,0]
    predicted_resonances = resonances_and_lengths[:,1]
    func_res_freq_interp = interpolate.interp1d(predicted_lengths, predicted_resonances, kind='cubic')

#set up motors and data logger
orpheus_motors = OrpheusMotors(auths_file, motors_to_move)
data_logger = DataLogger(auths_file)

#  Ask user to describe the measurement. Forces user to document what they are doing.
measurement_description = input('Describe the current measurement setup: ')

data_logger.initialize_na_settings_for_modemap(averages = averages, average_enable = average_enable, power = vna_power, sweep_points = sweep_points)
orpheus_motors.move_to_zero(move_one_motor_at_a_time = True)
orpheus_motors.wait_for_motors()

#Send alert saying you are starting the modemap measurement
dl_logger.info('Starting modemap measurement')
data_logger.start_modemap(measurement_description)

current_resonator_length_cm = initial_mirror_holder_spacing+1.05
the_interface.set('resonator_length', current_resonator_length_cm) #logging resonator length into endpoint
current_resonator_length_in = cm_to_inch(current_resonator_length_cm)
current_plate_separation = orpheus_motors.plate_separation(current_resonator_length_in,num_plates)

try:
    delta_length = 0
    override = 1
    while delta_length < abs(distance_to_move):
        delta_length = round((delta_length+inch_to_cm(increment_distance)),4)
#        if override == 0:
#            prompt = input("Press 'o' to override this prompt. Press any other key to continue: ")
#            print('')
#            if prompt == 'o':
#                override = 1
        dl_logger.info('Resonator length: {}'.format(current_resonator_length_cm))
        #log transmission
        data_logger.log_transmission_reflection_switches(wide_scan_start_freq, wide_scan_stop_freq, sec_wait_for_na_averaging, 'widescan')
        if narrow_scan and (predicted_lengths[0]<current_resonator_length_cm<predicted_lengths[-1]):
            resonant_freq = func_res_freq_interp(current_resonator_length_cm) + tem0018_offset
            narrow_scan_start_freq = resonant_freq - narrow_scan_span_guess/2
            narrow_scan_stop_freq = resonant_freq + narrow_scan_span_guess/2
            if zoom_using_data:
                resonant_freq_guess = data_logger.guess_resonant_frequency(narrow_scan_start_freq, narrow_scan_stop_freq, averaging_time = averaging_time_for_fo_guess_measurement)
                narrow_scan_start_freq = resonant_freq_guess-narrow_scan_span_focus/2
                narrow_scan_stop_freq = resonant_freq_guess+narrow_scan_span_focus/2
            data_logger.log_transmission_reflection_switches(narrow_scan_start_freq, narrow_scan_stop_freq, sec_wait_for_na_averaging, 'narrowscan', fitting = fitting)

        if digitize:
            measured_fo = the_interface.get('f_transmission').payload.to_python()['value_cal']
            data_logger.digitize(measured_fo, if_center, digitization_time)

        dl_logger.info("now scanning distance = " +str(delta_length))
        current_resonator_length_in, new_plate_separation = orpheus_motors.move_by_increment(increment_distance,
                                                                                             current_resonator_length_in,
                                                                                             num_plates,
                                                                                             current_plate_separation,
                                                                                             move_one_motor_at_a_time = False)
        orpheus_motors.wait_for_motors()
        current_resonator_length_cm = current_resonator_length_cm+inch_to_cm(increment_distance)

        the_interface.set('resonator_length', current_resonator_length_cm) #logging resonator length into endpoint
        current_plate_separation = new_plate_separation
        dl_logger.info("plate separation: {}".format(current_plate_separation))
    data_logger.stop_modemap()

except KeyboardInterrupt:
    dl_logger.info('stopping motors and modemap measurement')
    orpheus_motors.stop_and_kill()
    #data_logger.stop_modemap()

data_logger.turn_off_all_switches()
