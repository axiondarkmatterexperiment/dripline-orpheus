from motor import OrpheusMotors
from data_logging import DataLogger
import numpy as np
from scipy import interpolate
import yaml
from dripline.core import Interface
import logging
logging.basicConfig(level=logging.INFO)
dl_logger = logging.getLogger(__name__)
import time

def cm_to_inch(dist):
    return dist/2.54
def inch_to_cm(dist):
    return dist*2.54

starting_fo = input('What is the current frequency of the TEM_00-18 mode?: ')
#configure data taking
config_file = open("axion_data_taking_config.yaml")
configs = yaml.load(config_file, Loader =yaml.FullLoader)
general_mechanical_configs = configs['general_configs']
list_of_keys = list(configs["measurement_configs"].keys())
locals().update(general_mechanical_configs)
print("  Configurations  ")
for i in range(len(list_of_keys)):
    print(F"{i}  {list_of_keys[i]}")
picked_config = int(input(F"Pick your configuration (0 - {len(list_of_keys)-1}): "))
locals().update(configs['measurement_configs'][list_of_keys[picked_config]])

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

#set up motors and data_logger
orpheus_motors = OrpheusMotors(auths_file, motors_to_move)
data_logger = DataLogger(auths_file)

#make sure we start off with good settings, no matter what the current state is
data_logger.initialize_na_settings_for_modemap(averages = averages, average_enable = average_enable, power = vna_power, sweep_points = sweep_points)
data_logger.turn_off_all_switches()
data_logger.initialize_lo(lo_power)
the_interface.set('na_output_enable', 1)

#  Ask user to describe the measurement. Forces user to document what they are doing.
measurement_description = input('Describe the current measurement setup: ')

#send alert saying you're starting axion data taking
data_logger.start_axion_data_taking(measurement_description)

current_resonator_length_cm = initial_mirror_holder_spacing+1.05
current_resonator_length_in = cm_to_inch(current_resonator_length_cm)
current_plate_separation = orpheus_motors.plate_separation(current_resonator_length_in,num_plates)

the_interface.set('target_fo', starting_fo)

#find initial VNA window for narrowscan measurements
target_fo = the_interface.get('target_fo').payload.to_python()['value_cal']

#get frequency span for narrowscan
narrow_scan_start_freq = target_fo - narrow_scan_span_guess/2
narrow_scan_stop_freq = target_fo + narrow_scan_span_guess/2
resonant_freq_guess = data_logger.guess_resonant_frequency(narrow_scan_start_freq, narrow_scan_stop_freq, averaging_time = averaging_time_for_fo_guess_measurement)
narrow_scan_start_freq_focus = target_fo-narrow_scan_span_focus/2
narrow_scan_stop_freq_focus = target_fo+narrow_scan_span_focus/2
the_interface.set('target_fo', resonant_freq_guess)
target_fo = the_interface.get('target_fo').payload.to_python()['value_cal']

fft_bin_width = sampling_rate/fft_size

i = 0
try:
    delta_length = 0
    print('Resonator length: {}'.format(current_resonator_length_cm))
    while delta_length < abs(distance_to_move):
        start_cadence_time = time.time()
        if the_interface.get('axion_data_taking_status').payload.to_python()['value_cal'] == 'stop_measurement':
            break
        #record that we are starting a measurement
        the_interface.set('axion_record_spectrum_status', 'start_measurement')
        #take transmission measurement
        if not (i%widescan_interval):
            the_interface.set('na_sweep_points', widescan_sweep_points)
            the_interface.set('na_measurement_status', 'start_measurement')
            the_interface.set('na_measurement_status_explanation', 'axion data taking. widescan')
            data_logger.log_transmission_switches(wide_scan_start_freq, wide_scan_stop_freq, sec_wait_for_na_transmission_averaging, 'axion data taking. widescan', transmission_endpoint= 's21_iq_transmission_data_widescan' )
            the_interface.set('na_sweep_points', sweep_points)

        #get frequency span for narrowscan
        #How does it do this before the first transmission scan? It refers to s21_iq_transmission_data in the guess_resonant_frequency function. Won't the first guess be totally wrong?
        if increment_distance:
            narrow_scan_start_freq = target_fo - narrow_scan_span_guess/2
            narrow_scan_stop_freq = target_fo + narrow_scan_span_guess/2
            resonant_freq_guess = data_logger.guess_resonant_frequency(narrow_scan_start_freq, narrow_scan_stop_freq, averaging_time = averaging_time_for_fo_guess_measurement/2)
            narrow_scan_start_freq_focus = target_fo-narrow_scan_span_focus/2
            narrow_scan_stop_freq_focus = target_fo+narrow_scan_span_focus/2
            the_interface.set('target_fo', resonant_freq_guess)
            target_fo = the_interface.get('target_fo').payload.to_python()['value_cal']

        narrow_scan_start_freq_focus = target_fo - narrow_scan_span_focus/2
        narrow_scan_stop_freq_focus = target_fo + narrow_scan_span_focus/2

        the_interface.cmd('axion_data_taking_short_snapshot', 'log_entities')

        data_logger.log_transmission_switches(narrow_scan_start_freq_focus, narrow_scan_stop_freq_focus, sec_wait_for_na_transmission_averaging, fitting = True, transmission_endpoint = 's21_iq_transmission_data')

        data_logger.log_reflection_switches(narrow_scan_start_freq_focus, narrow_scan_stop_freq_focus, sec_wait_for_na_reflection_averaging, fitting = True, reflection_endpoint = 's21_iq_reflection_data')

        #take axion data
        measured_fo = the_interface.get('f_transmission').payload.to_python()['value_cal']
        data_logger.digitize(measured_fo, if_center, fft_bin_width, log_power_monitor = True, disable_motors = disable_motors_while_digitizing)

        #record power going to digitizer, -20 dBm
        the_interface.cmd('power_monitor_voltage', 'scheduled_log')

        # measure transmission after digitization to check for mechanical drifting
        if stability_check:
            data_logger.log_transmission_switches(narrow_scan_start_freq_focus, narrow_scan_stop_freq_focus, sec_wait_for_na_transmission_averaging, fitting = True, transmission_endpoint = 's21_iq_transmission_data_stability_check')
            measured_fo_stability_check = the_interface.get('f_transmission_stability_check').payload.to_python()['value_cal']
            f_transmission_drift = measured_fo - measured_fo_stability_check
            the_interface.set('f_transmission_drift', f_transmission_drift)
        

        the_interface.set('axion_record_spectrum_status', 'stop_measurement')

        # log reflection measurements
        if not (i%widescan_interval):
            #switch is already in the reflection position. we just need to change the frequency range. So we don't have to average as long to have the system settle down.
            data_logger.log_transmission_switches(wide_scan_start_freq, wide_scan_stop_freq, sec_wait_for_na_transmission_averaging, na_iq_data_notes = 'axion data taking. widescan', transmission_endpoint= 's21_iq_transmission_data_widescan' )
            the_interface.set('na_measurement_status', 'stop_measurement')

        #adjust target fo
        the_interface.set('target_fo', measured_fo)

        #move plates if increment_distance is anything other than 0.
        if increment_distance: 
            #TODO figure out what to do with negative increment_distance
            #Wait, I think this is fine as is. Any non-zero value is equivalent to TRUE --JS
            current_resonator_length_in, new_plate_separation = orpheus_motors.move_by_increment(increment_distance,
                                                                                             current_resonator_length_in,
                                                                                             num_plates,
                                                                                             current_plate_separation)
            orpheus_motors.wait_for_motors()
            current_plate_separation = new_plate_separation
        current_resonator_length_cm = current_resonator_length_cm+inch_to_cm(increment_distance)

        the_interface.set('resonator_length', current_resonator_length_cm) #logging resonator length into endpoint
        dl_logger.info("plate separation: {}".format(current_plate_separation))
        i += 1
        stop_cadence_time = time.time()
        cadence_time = stop_cadence_time-start_cadence_time
        the_interface.set('cadence_time', cadence_time)

except KeyboardInterrupt:
    dl_logger.info('stopping motors and modemap measurement')
    orpheus_motors.stop_and_kill()
    data_logger.start_axion_data_taking()

data_logger.turn_off_all_switches()

# send alert saying that you are stopping axion data taking.
data_logger.stop_axion_data_taking()