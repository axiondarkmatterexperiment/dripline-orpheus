from dripline.core import Interface
import time
import common_functions
#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

#distance to move
print("PLEASE ENTER DISTANCE IN MILLIMETERS (mm)")
distance_to_move = float(input('Enter the distance to move in mm (Empty cavity modemap is usually 30): '))
resolution = float(input('Enter the number of measurements needed: '))
increment_distance = distance_to_move/resolution

#time to wait
sleep4 = 4

#move curved mirror to 0 position.
list_of_motor_commands = ['curved_mirror_move_to_position',
                  'bottom_dielectric_plate_move_to_position',
                  'top_dielectric_plate_move_to_position']
print('Restarting motor position')
common_functions.move_motors_to_zero(list_of_motor_commands)
common_functions.wait_for_motors()
time.sleep(sleep4)
print('motor positions reset')

#Setting cavity length to 6.3 inches for now.
#In practice this wil be something like the_interface.get(steps)
cavity_length_tracker = 6.3
num_plates = 4
initial_plate_separation = cavity_length_tracker/(num_plates+1)

#Send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
the_interface.set('modemap_measurement_status', 'start_measurement')

i = 0
while i <= distance_to_move:
    common_functions.data_logging_sequence(sleep4) #parameter - time allowed for averaging
    #moving curved mirror
    print('Moving curved mirror motor by {} steps'.format(common_functions.curved_mirror_distance_to_steps(increment_distance)))
    the_interface.set('curved_mirror_move_steps', common_functions.curved_mirror_distance_to_steps(increment_distance))
    #adjusting bottom dielectric plate
    cavity_length_tracker = cavity_length_tracker + increment_distance
    new_plate_separation = cavity_length_tracker/(num_plates+1)
    diff = initial_plate_separation +increment_distance
    move_bottom_plate = diff - new_plate_separation
    print('Moving bottom plate motor by {} steps'.format(common_functions.plates_distance_to_steps(move_bottom_plate)))
    the_interface.set('bottom_dielectric_plate_move_steps',common_functions.plates_distance_to_steps(move_bottom_plate))
    #adjusting top dielectric plate
    move_top_plate = new_plate_separation - initial_plate_separation
    print('Moving top plate motor by {} steps'.format(common_functions.plates_distance_to_steps(move_top_plate)))
    the_interface.set('top_dielectric_plate_move_steps',common_functions.plates_distance_to_steps(move_top_plate))
    #wait for motor. If program gets stuck check here for infinite loop
    wait_for_motors()
    time.sleep(sleep4)
    i = round((i+increment_distance),4)
    initial_plate_separation = new_plate_separation
    print("now scanning distance = " +str(i))

#stop
print('Stopping modemap measurement')
the_interface.set('modemap_measurement_status', 'stop_measurement')
