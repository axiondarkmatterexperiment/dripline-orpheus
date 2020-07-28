'''
    File name: predict_res_freq_tem.py
    Author: Raphael Cervantes
    Date created: 7/15/2020
    Date last modified: 7/15/2020
    Python Version: 3.6
    Description: Script I ran to get modemap in LN2.
'''
from dripline.core import Interface
import time
import common_functions

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

#  ask about notes for current measurement. The user would type in what they want to remember about their current measurement.
measurement_notes = input('Notes about current measurement: ')

### configure na ####
na_start_freq = 15e9
na_stop_freq = 18e9
na_power = -5  # dBm
na_averages = 64
na_sweep_points = 10001  # the max

### configure motion ###
stps_per_cm = 157480 #157480 steps is 1 cm
sec_wait_for_na_averaging = 8
n_measurements = 50
total_distance = 3 #cm
n_motor_steps = total_distance/n_measurements * stps_per_cm
starting_resonator_length = 16  # cm
motor_zero_resonator_length = 16  # cm
starting_motor_steps = (starting_resonator_length - motor_zero_resonator_length)*stps_per_cm

def move_motor_w_backpedaling(endpoint, total_n_motor_steps, forward_steps_per_iter, back_steps_per_iter):
    n_steps = 0
    while abs(total_n_motor_steps - n_steps) >= abs(forward_steps_per_iter):
        the_interface.set(endpoint, forward_steps_per_iter)
        n_steps += forward_steps_per_iter
        the_interface.set('bottom_dielectric_plate_wait_time', 1)
        the_interface.set(endpoint, -back_steps_per_iter)
        n_steps -= back_steps_per_iter
        the_interface.set('bottom_dielectric_plate_wait_time', 1)

# setting the VNA settings
print('Configuring VNA')
common_functions.initialize_na_settings_for_modemap(start_freq = na_start_freq, stop_freq = na_stop_freq, power = na_power, averages = na_averages, sweep_points = na_sweep_points)

#move curved mirror to starting resonator_length position.
print('Restarting motor position')
the_interface.set('curved_mirror_move_to_position', starting_motor_steps)
the_interface.set('bottom_dielectric_plate_move_to_position', starting_motor_steps)
print('Going to wait while motor moves')
common_functions.wait_for_motors()

#send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
the_interface.set('modemap_measurement_status', 'start_measurement')
the_interface.set('modemap_measurement_status_explanation', measurement_notes)


for i in range(n_measurements):
    print('Iteration in loop: {}'.format(i))
    common_functions.data_logging_sequence(sec_wait_for_na_averaging)
    print('Moving motor by {} steps'.format(n_motor_steps))
    #move_motor_w_backpedaling('curved_mirror_move_steps', n_motor_steps, 5000, 500)
    the_interface.set('curved_mirror_move_steps', n_motor_steps)
    print('Going to wait while motor moves')
    common_functions.wait_for_motors()

print('Stopping modemap measurement')
the_interface.set('modemap_measurement_status', 'stop_measurement')

print('Moving top dielectric plate by {} steps'.format((3*n_motor_steps)))
the_interface.set('top_dielectric_plate_move_steps', 1/4*n_measurements*n_motor_steps)
