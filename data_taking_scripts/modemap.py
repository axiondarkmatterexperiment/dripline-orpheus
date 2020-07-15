from dripline.core import Interface
import time
import common_functions

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

stps_per_cm = 157480 #157480 steps is 1 cm
sec_wait_for_na_averaging = 4
n_measurements = 52
total_distance = 3 #cm
n_motor_steps = total_distance/n_measurements * stps_per_cm

def data_logging_sequence(a_sec_wait_for_na_averaging):
    print('Setting na_measurement_status to start_measurement')
    the_interface.set('na_measurement_status', 'start_measurement')
    print('Logging list of endpoints')
    the_interface.cmd('modemap_snapshot_no_iq', 'log_entities')
    the_interface.get('na_s21_iq_data')
    time.sleep(sec_wait_for_na_averaging)
    the_interface.cmd('na_s21_iq_data', 'scheduled_log')
    the_interface.get('na_s11_iq_data')
    time.sleep(sec_wait_for_na_averaging)
    the_interface.cmd('na_s11_iq_data', 'scheduled_log')
    print('Setting na_measurement_status to stop_measurement')
    the_interface.set('na_measurement_status', 'stop_measurement')

def move_motor_w_backpedaling(endpoint, total_n_motor_steps, forward_steps_per_iter, back_steps_per_iter):
    n_steps = 0
    while abs(total_n_motor_steps - n_steps) >= abs(forward_steps_per_iter):
        the_interface.set(endpoint, forward_steps_per_iter)
        n_steps += forward_steps_per_iter
        the_interface.set('bottom_dielectric_plate_wait_time', 1)
        the_interface.set(endpoint, -back_steps_per_iter)
        n_steps -= back_steps_per_iter
        the_interface.set('bottom_dielectric_plate_wait_time', 1)

#move curved mirror to 0 position.
print('Restarting motor position')
the_interface.set('curved_mirror_move_to_position', 0)
the_interface.set('bottom_dielectric_plate_move_to_position', 0)
print('Going to wait while motor moves')
common_functions.wait_for_motors()

#send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
the_interface.set('modemap_measurement_status', 'start_measurement')

for i in range(n_measurements):
    print('Iteration in loop: {}'.format(i))
    data_logging_sequence(sec_wait_for_na_averaging)
    print('Moving motor by {} steps'.format(n_motor_steps))
    #move_motor_w_backpedaling('curved_mirror_move_steps', n_motor_steps, 5000, 500)
    the_interface.set('curved_mirror_move_steps', n_motor_steps)
    print('Going to wait while motor moves')
    common_functions.wait_for_motors()

print('Stopping modemap measurement')
the_interface.set('modemap_measurement_status', 'stop_measurement')

print('Moving top dielectric plate by {} steps'.format((3*n_motor_steps)))
the_interface.set('top_dielectric_plate_move_steps', 3*n_motor_steps)
