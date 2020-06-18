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
    the_interface.cmd('na_snapshot', 'log_entities')
    time.sleep(3)
    the_interface.set('curved_mirror_move_steps', 300)
    the_interface.set('na_measurement_status', 'stop_measurement')


the_interface.set('modemap_measurement_status', 'stop_measurement')
