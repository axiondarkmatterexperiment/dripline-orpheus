from motor import OrpheusMotors
auths_file = '/etc/rabbitmq-secret/authentications.json'
motors_to_move = ['curved_mirror', 'bottom_dielectric_plate', 'top_dielectric_plate']

orpheus_motors = OrpheusMotors(auths_file, motors_to_move)
orpheus_motors.set_internal_position_to_value(0)

print(F"Internal counters for {motors_to_move} set to 0")
