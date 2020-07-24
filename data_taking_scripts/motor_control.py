from dripline.core import Interface
import time
import common_functions
#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

def mm_to_inch(dist):
    return dist/25.4

#distance to move
print("PLEASE ENTER DISTANCE IN MILLIMETERS (mm)")
cavity_length_tracker = mm_to_inch(float(input('Enter initial resonator length (in mm): ')))
distance_to_move = float(input('Enter the distance to move in mm (Empty cavity modemap is usually 30): '))
resolution = float(input('Enter the number of measurements needed: '))
increment_distance = distance_to_move/resolution

#time to wait
sleep4 = 4
#important parameters. all units are in inches
plate_thickness = 1/8
lip_thickness = 0.05
holder_thickness = 1/4
pitch = 1/20 #pitch of threaded rods
steps_per_rotation = 20000 #motor specification
#move curved mirror to 0 position.
list_of_motor_commands = ['curved_mirror_move_to_position',
                  'bottom_dielectric_plate_move_to_position',
                  'top_dielectric_plate_move_to_position']
print('Restarting motor position')
common_functions.move_motors_to_zero(list_of_motor_commands)
common_functions.wait_for_motors()
time.sleep(sleep4)
print('motor positions reset')

num_plates = 4
initial_plate_separation = common_functions.plate_separation(cavity_length_tracker,num_plates)

#Send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
the_interface.set('modemap_measurement_status', 'start_measurement')

try:
    i = 0
    while i <= distance_to_move:
        common_functions.data_logging_sequence(sleep4) #parameter - time allowed for averaging
        #moving curved mirror
        curved_mirror_steps = common_functions.curved_mirror_distance_to_steps(mm_to_inch(increment_distance))
        print('Moving curved mirror motor by {} steps'.format(curved_mirror_steps))
        the_interface.set('curved_mirror_move_steps', curved_mirror_steps)
        #adjusting bottom dielectric plate
        cavity_length_tracker = cavity_length_tracker + increment_distance
        new_plate_separation = common_functions.plate_separation(cavity_length_tracker,num_plates)
        diff = initial_plate_separation +increment_distance
        move_bottom_plate = diff - new_plate_separation
        bottom_plate_steps = common_functions.plates_distance_to_steps(mm_to_inch(move_bottom_plate),holder_thickness,plate_thickness,lip_thickness)
        print('Moving bottom plate motor by {} steps'.format(bottom_plate_steps))
        the_interface.set('bottom_dielectric_plate_move_steps',bottom_plate_steps)
        #adjusting top dielectric plate
        move_top_plate = new_plate_separation - initial_plate_separation
        top_plate_steps = common_functions.plates_distance_to_steps(mm_to_inch(move_top_plate),holder_thickness,plate_thickness,lip_thickness)
        print('Moving top plate motor by {} steps'.format(top_plate_steps))
        the_interface.set('top_dielectric_plate_move_steps',top_plate_steps)
        #wait for motor. If program gets stuck check here for infinite loop
        common_functions.wait_for_motors()
        time.sleep(sleep4)
        i = round((i+increment_distance),4)
        initial_plate_separation = new_plate_separation
        print("now scanning distance = " +str(i))
    #stop
    print('Stopping modemap measurement')
    the_interface.set('modemap_measurement_status', 'stop_measurement')

except KeyboardInterrupt:
    print('interrupted')
    #stop
    print('Stopping modemap measurement')
    the_interface.set('modemap_measurement_status', 'stop_measurement')
