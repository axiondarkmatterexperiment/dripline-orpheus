from dripline.core import Interface
import time
import common_functions

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

the_interface.set('curved_mirror_move_to_position', 0)
the_interface.set('bottom_dielectric_plate_move_to_position', 0)
the_interface.set('top_dielectric_plate_move_to_position', 0)

common_functions.wait_for_motors()

