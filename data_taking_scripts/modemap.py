from dripline.core import Interface

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})
print(test_interface.get('peaches'))

#move curved mirror to 0 position.
the_interface.set('curved_mirror_set_position', 0)

#send alert saying you are starting the modemap measurement
the_interface.set('modemap_measurement_status', 'start_measurement')


for i in range(10):
    the_interface.set('na_measurement_status', 'start_measurement')
    the_interface.cmd('na_snapshot', '-s log_entities')
    the_interface.set('curved_mirror_move_steps', '10')
    the_interface.set('na_measurement_status', 'stop_measurement')


