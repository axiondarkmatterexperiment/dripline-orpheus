from dripline.core import Interface
import time

#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

#time to wait for motor to move
n_sec_wait_for_motor = 3

#move curved mirror to 0 position.
print('Restarting motor position')
print('This will take approximately {} seconds'.format(n_sec_wait_for_motor*3))
the_interface.set('curved_mirror_set_position', 0)
time.sleep(n_sec_wait_for_motor)
the_interface.set('bottom_dielectric_plate_set_position', 0)
time.sleep(n_sec_wait_for_motor)
the_interface.set('top_dielectric_plate_set_position', 0)
time.sleep(n_sec_wait_for_motor)
print('motor positions reset')
print('')

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
    actual_distance = distance + gap
    num_pitch_lengths = actual_distance/pitch #these many complete rotations
    steps = steps_per_rotation * num_pitch_lengths
    return steps
def curved_mirror_distance_to_steps(distance):
    num_pitch_lengths = distance/pitch #these many complete rotations
    steps = steps_per_rotation * num_pitch_lengths
    return steps

#Setting cavity length to 6.3 inches for now.
#In practice this wil be something like the_interface.get(steps)
cavity_length_tracker = 6.3
initial_plate_separation = cavity_length_tracker/(num_plates+1)

#Send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
the_interface.set('modemap_measurement_status', 'start_measurement')

#Setting na_measurement_status to start_measurement
print('Setting na_measurement_status to start_measurement')
the_interface.set('na_measurement_status', 'start_measurement')

#Logging list of endpoints
the_interface.cmd('na_snapshot', 'log_entities')

#moving curved mirror
distance = 1 # user input + or -
print('Moving curved mirror motor by {} steps'.format(curved_mirror_distance_to_steps(distance)))
the_interface.set('curved_mirror_move_steps', curved_mirror_distance_to_steps(distance))
time.sleep(n_sec_wait_for_motor)

cavity_length_tracker = cavity_length_tracker+distance
new_plate_separation = (cavity_length_tracker/(num_plates+1))
diff = initial_plate_separation + distance
move_bottom_plate = diff - new_plate_separation #distance to move bottom dielectric plate

#adjusting bottom dielectric plate
print('Moving bottom plate motor by {} steps'.format(plates_distance_to_steps(move_bottom_plate)))
the_interface.set('bottom_dielectric_plate_move_steps', plates_distance_to_steps(move_bottom_plate))
time.sleep(n_sec_wait_for_motor)

#adjusting top dielectric plate
move_top_plate = new_plate_separation - initial_plate_separation
print('Moving top plate motor by {} steps'.format(plates_distance_to_steps(move_top_plate)))
the_interface.set('top_dielectric_plate_move_steps', plates_distance_to_steps(move_top_plate))
time.sleep(n_sec_wait_for_motor)

print('Setting na_measurement_status to stop_measurement')
the_interface.set('na_measurement_status', 'stop_measurement')

# taking another measurement
print('Setting na_measurement_status to start_measurement')
the_interface.set('na_measurement_status', 'start_measurement')
print('Logging list of endpoints')
the_interface.cmd('na_snapshot', 'log_entities')
print('Setting na_measurement_status to stop_measurement')
the_interface.set('na_measurement_status', 'stop_measurement')

#stop
print('Stopping modemap measurement')
the_interface.set('modemap_measurement_status', 'stop_measurement')
