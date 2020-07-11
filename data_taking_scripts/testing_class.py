from dripline.core import Interface
import time
import common_functions
import motor
#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

#set up motors
orpheus_motors = motor.OrpheusMotors(auths_file)
print(orpheus_motors.get_motor_status())
