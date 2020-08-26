from motor import OrpheusMotors

def cm_to_inch(dist):
    return dist/2.54

auths_file = '/etc/rabbitmq-secret/authentications.json'
motors_to_move = ['curved_mirror', 'bottom_dielectric_plate', 'top_dielectric_plate']
orpheus_motors = OrpheusMotors(auths_file, motors_to_move)

initial_mirror_holder_spacing = float(input('Enter initial mirror holder spacing (in cm): '))
distance_to_move = float(input('Enter the distance to move in cm: '))

num_plates = 4
current_resonator_length_cm =  initial_mirror_holder_spacing + 1.0497
current_resonator_length_in = cm_to_inch(current_resonator_length_cm)
current_plate_separation = current_resonator_length_in/(num_plates+1)

print(F"Current mirror spacing = {initial_mirror_holder_spacing}")
print(F"Current resonator length = {current_resonator_length_cm}")
print(F"Changing resonator length by {distance_to_move}")

current_resonator_length, current_plate_separation = orpheus_motors.move_by_increment(cm_to_inch(distance_to_move),
                                                                                      current_resonator_length_in,
                                                                                      num_plates,
                                                                                      current_plate_separation)
orpheus_motors.wait_for_motors()
print('')
print(F"Final mirror spacing = {initial_mirror_holder_spacing+distance_to_move}")
print(F"Final resonator length = {current_resonator_length_cm+distance_to_move}")
