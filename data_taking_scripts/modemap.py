from dripline.core import Interface
import time

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

#move curved mirror to 0 position.
the_interface.set('curved_mirror_set_position', 0)

#send alert saying you are starting the modemap measurement
the_interface.set('modemap_measurement_status', 'start_measurement')


for i in range(10):
    print(i)
    the_interface.set('na_measurement_status', 'start_measurement')
    time.sleep(2)
    print('help1')
    the_interface.cmd('na_snapshot', ' log_entities')
    print('help2')
    time.sleep(2)
    the_interface.set('curved_mirror_move_steps', 10)
    print('help3')
    time.sleep(2)
    the_interface.set('na_measurement_status', 'stop_measurement')
    print('help4')
    time.sleep(2)


the_interface.set('modemap_measurement_status', 'stop_measurement')
