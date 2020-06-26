from dripline.core import Interface
import time

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})
n_motor_steps = 300
n_sec_wait_for_motor = 3

#move curved mirror to 0 position.
print('Restarting motor position')
the_interface.set('curved_mirror_move_to_position', 0)
print('Going to wait {} seconds while motor moves'.format(n_sec_wait_for_motor))
time.sleep(n_sec_wait_for_motor)

#send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
the_interface.set('modemap_measurement_status', 'start_measurement')

for i in range(10):
    print('Iteration in loop: {}'.format(i))

    print('Setting na_measurement_status to start_measurement')
    the_interface.set('na_measurement_status', 'start_measurement')
    print('Logging list of endpoints')
    the_interface.cmd('na_snapshot', 'log_entities')
    print('Moving motor by {} steps'.format(n_motor_steps))
    the_interface.set('curved_mirror_move_steps', n_motor_steps)
    print('Going to wait {} seconds while motor moves'.format(n_sec_wait_for_motor))
    time.sleep(n_sec_wait_for_motor)
    print('Setting na_measurement_status to stop_measurement')
    the_interface.set('na_measurement_status', 'stop_measurement')

print('Stopping modemap measurement')
the_interface.set('modemap_measurement_status', 'stop_measurement')
