from dripline.core import Interface
import time
#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

#returns the sttus of the motor as a string
def get_status():
    bottom_plate_status = the_interface.get('bottom_dielectric_plate_motor_request_status').payload.to_python()['value_raw']
    top_plate_status = the_interface.get('top_dielectric_plate_motor_request_status').payload.to_python()['value_raw']
    curved_mirror_status = the_interface.get('curved_mirror_motor_request_status').payload.to_python()['value_raw']
    return [curved_mirror_status,top_plate_status,bottom_plate_status]
def wait_for_motors():
    while (get_status() != ['R','R','R']):
        print(get_status())
        time.sleep(1)
    print('done waiting')
#distance to move
print("PLEASE ENTER DISTANCE IN MILLIMETERS (mm)")
distance_to_move = float(input('Enter the distance to move in mm (Empty cavity modemap is usually 30): '))
resolution = float(input('Enter the number of measurements needed: '))
increment_distance = distance_to_move/resolution
forward_increment = increment_distance+increment_distance/2
back_increment = (-1)*increment_distance/2
#time to wait for motor to move
sleep2 = 2
sleep5 = 5
#move curved mirror to 0 position.
print('Restarting motor position')
print('This will take approximately {} seconds'.format(sleep5*3))
the_interface.set('curved_mirror_move_to_position', 0)
the_interface.set('bottom_dielectric_plate_move_to_position', 0)
the_interface.set('top_dielectric_plate_move_to_position', 0)
#wait for motor. If program gets stuck check here for infinite loop
wait_for_motors()
time.sleep(sleep5)
print('motor positions reset')
#all units are in inches
#holder info
plate_thickness = 1/8
lip_thickness = 0.05
holder_thickness = 1/4
num_plates = 4

# motor and rod info
pitch = 1/20 #pitch of threaded rods
steps_per_rotation = 20000 #motor specification

#some necessary computations
holder_center = holder_thickness/2
plate_center = lip_thickness + plate_thickness/2
gap = holder_center - plate_center

#functions to convert distances into steps
def plates_distance_to_steps(distance):
    distance = distance/25.4 ##convert to inch
    actual_distance = distance + gap
    num_pitch_lengths = actual_distance/pitch #these many complete rotations
    steps = steps_per_rotation * num_pitch_lengths
    return int(round(steps))
def curved_mirror_distance_to_steps(distance):
    distance = distance/25.4 ##convert to inch
    num_pitch_lengths = distance/pitch #these many complete rotations
    steps = steps_per_rotation * num_pitch_lengths
    return int(round(steps))
def bottom_dielectric_dist(cavity_len, incr, initial_separation):
    cavity_len = cavity_len+incr
    new_separation = cavity_len/(num_plates+1)
    diff = initial_separation + incr
    move_bottom_plate = diff - new_separation
    return move_bottom_plate, new_separation, cavity_len

#Setting cavity length to 6.3 inches for now.
#In practice this wil be something like the_interface.get(steps)
cavity_length_tracker = 6.3
initial_plate_separation = cavity_length_tracker/(num_plates+1)

#Send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
the_interface.set('modemap_measurement_status', 'start_measurement')

i = 0
while i <= distance_to_move:
    #Setting na_measurement_status to start_measurement
    print('Setting na_measurement_status to start_measurement')
    the_interface.set('na_measurement_status', 'start_measurement')
    #Logging list of endpoints
    the_interface.cmd('na_snapshot', 'log_entities')
    print('Setting na_measurement_status to stop_measurement')
    the_interface.set('na_measurement_status', 'stop_measurement')
    #moving curved mirror
    print('Moving curved mirror motor by {} steps'.format(curved_mirror_distance_to_steps(forward_increment)))
    the_interface.set('curved_mirror_move_steps', curved_mirror_distance_to_steps(forward_increment))
    #adjusting bottom dielectric plate
    move_bottom_plate, new_plate_separation, cavity_length_tracker = bottom_dielectric_dist(cavity_length_tracker, forward_increment, initial_plate_separation)
    print('Moving bottom plate motor by {} steps'.format(plates_distance_to_steps(move_bottom_plate)))
    the_interface.set('bottom_dielectric_plate_move_steps', plates_distance_to_steps(move_bottom_plate))
    #adjusting top dielectric plate
    move_top_plate = new_plate_separation - initial_plate_separation
    print('Moving top plate motor by {} steps'.format(plates_distance_to_steps(move_top_plate)))
    the_interface.set('top_dielectric_plate_move_steps', plates_distance_to_steps(move_top_plate))
    #wait for motor. If program gets stuck check here for infinite loop
    wait_for_motors()
    time.sleep(sleep5)
    initial_plate_separation = new_plate_separation
    #backpedalling
    print('Moving curved mirror motor by {} steps'.format(curved_mirror_distance_to_steps(back_increment)))
    the_interface.set('curved_mirror_move_steps', curved_mirror_distance_to_steps(back_increment))
    move_bottom_plate, new_plate_separation, cavity_length_tracker = bottom_dielectric_dist(cavity_length_tracker, back_increment, initial_plate_separation)
    print('Moving bottom plate motor by {} steps'.format(plates_distance_to_steps(move_bottom_plate)))
    the_interface.set('bottom_dielectric_plate_move_steps', plates_distance_to_steps(move_bottom_plate))
    #adjusting top dielectric plate
    move_top_plate = new_plate_separation - initial_plate_separation
    print('Moving top plate motor by {} steps'.format(plates_distance_to_steps(move_top_plate)))
    the_interface.set('top_dielectric_plate_move_steps', plates_distance_to_steps(move_top_plate))
    #wait for motor. If program gets stuck check here for infinite loop
    wait_for_motors()
    time.sleep(sleep2)
    i = round((i+forward_increment+back_increment),4)
    initial_plate_separation = new_plate_separation
    print("now scanning distance = " +str(i))

#stop
print('Stopping modemap measurement')
the_interface.set('modemap_measurement_status', 'stop_measurement')
