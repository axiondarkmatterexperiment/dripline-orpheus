from dripline.core import Interface
import time

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

def wait_for_motors():
    while (get_status() != ['R','R','R']):
        print(get_status())
        time.sleep(1)
    print('done waiting')

the_interface.set('curved_mirror_move_to_position', 0)
the_interface.set('bottom_dielectric_plate_move_to_position', 0)
the_interface.set('top_dielectric_plate_move_to_position', 0)

wait_for_motors()

