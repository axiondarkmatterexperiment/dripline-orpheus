from dripline.core import Interface

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'

the_interface = Interface(dripline_config={'auth-file': auths_file})

the_interface.set('curved_mirror_move_to_position', 62992) #plate separation is 15.4 cm. cavity length is about 16.4?
