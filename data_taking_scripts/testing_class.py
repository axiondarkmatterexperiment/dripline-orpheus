from motor import OrpheusMotors
from data_logging import DataLogger
#setting up connection to dripline
auths_file = '/etc/rabbitmq-secret/authentications.json'

def cm_to_inch(dist):
    return dist/2.54
def inch_to_cm(dist):
    return dist*2.54

# names should be exactly like 'curved_mirror', 'top_dielectric_plate', 'bottom_dielectric_plate'
motors_to_move = ['curved_mirror', 'bottom_dielectric_plate', 'top_dielectric_plate']

cavity_length_tracker = cm_to_inch(float(input('Enter initial resonator length (in cm): ')))
distance_to_move = float(input('Enter the distance to move in cm (Empty cavity modemap is usually 3): '))
resolution = float(input('Enter the number of measurements needed: '))
increment_distance = cm_to_inch(distance_to_move/resolution)

#time to wait
sleep4 = 4
#important parameters. all units are in inches
plate_thickness = 1/8
num_plates = 4
#set up motors and logger
orpheus_motors = OrpheusMotors(auths_file, motors_to_move)
logger = DataLogger(auths_file)

logger.initialize_na_settings_for_modemap(averages = 64)
orpheus_motors.move_to_zero()
orpheus_motors.wait_for_motors()
initial_plate_separation = orpheus_motors.plate_separation(cavity_length_tracker,num_plates)

#Send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
logger.start_modemap()
i = 0
while i <= distance_to_move:
    logger.log_modemap(sleep4) #parameter - time allowed for averaging
    cavity_length_tracker, new_plate_separation = orpheus_motors.move_by_increment(increment_distance,
                                                                                   plate_thickness,
                                                                                   cavity_length_tracker,
                                                                                   num_plates,
                                                                                   initial_plate_separation)
    orpheus_motors.wait_for_motors()
    i = round((i+inch_to_cm(increment_distance)),4)
    initial_plate_separation = new_plate_separation
    print("now scanning distance = " +str(i))
#stop
print('Stopping modemap measurement')
logger.stop_modemap()
