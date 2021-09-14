from dripline.core import Interface
import time
from motor import OrpheusMotors
import yaml

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})
config_file = open("modemap_config.yaml")
configs = yaml.load(config_file, Loader = yaml.FullLoader)
general_mechanical_configs = configs['general_configs']
locals().update(general_mechanical_configs)

orpheus_motors = OrpheusMotors(auths_file, motors_to_move)

the_interface.set('curved_mirror_move_to_position', 0)
the_interface.set('bottom_dielectric_plate_move_to_position', 0)
the_interface.set('top_dielectric_plate_move_to_position', 0)

common_functions.wait_for_motors()

