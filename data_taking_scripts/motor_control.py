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
#motors_to_move = ['curved_mirror']

narrow_scan = True
wide_scan_start_freq = 15e9
wide_scan_stop_freq = 18e9
narrow_scan_span = 200e6
sec_wait_for_na_averaging = 2

initial_mirror_holder_spacing = cm_to_inch(float(input('Enter initial mirror holder spacing (in cm): ')))
distance_to_move = float(input('Enter the distance to move in cm (Empty resonator modemap is usually 3): '))
resolution = int(input('Enter the number of measurements needed: '))
increment_distance = cm_to_inch(distance_to_move/resolution)

#important parameters. all units are in inches
num_plates = 4
#set up motors and logger
orpheus_motors = OrpheusMotors(auths_file, motors_to_move)
logger = DataLogger(auths_file)

#  Ask user to describe the measurement. Forces user to document what they are doing. 
measurement_description = input('Describe the current measurement setup: ')

logger.initialize_na_settings_for_modemap(averages = 16)
orpheus_motors.move_to_zero()
orpheus_motors.wait_for_motors()
mirror_spacing_tracker = initial_mirror_holder_spacing
current_plate_separation = orpheus_motors.plate_separation(mirror_spacing_tracker,num_plates)

#Send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
logger.start_modemap(measurement_description)

current_resonator_length = inch_to_cm(initial_mirror_holder_spacing)+1.0497
try:
    delta_length = 0
    override = 0 # 0 is false, 1 is true
    while delta_length <= abs(distance_to_move):
        delta_length = round((delta_length+inch_to_cm(increment_distance)),4)
        if override == 0:
            print('')
            prompt = input("Press 'o' to override this prompt. Press any other key to continue: ")
            if prompt == 'o':
                override = 1

        print('Resonator length: {}'.format(current_resonator_length))
        resonant_freq = logger.flmn(0,0,18,current_resonator_length)
        if narrow_scan:
            narrow_scan_start_freq = resonant_freq - narrow_scan_span/2
            narrow_scan_stop_freq = resonant_freq + narrow_scan_span/2
        #print(resonant_freq)
        #log widescan
        logger.log_modemap(wide_scan_start_freq, wide_scan_stop_freq, sec_wait_for_na_averaging, 'widescan')
        #log narrowscan
        if narrow_scan:
            logger.log_modemap(narrow_scan_start_freq, narrow_scan_stop_freq, sec_wait_for_na_averaging, 'narrowscan')

        print("now scanning distance = " +str(delta_length))
        mirror_spacing_tracker, new_plate_separation = orpheus_motors.move_by_increment(increment_distance,
                                                                                        mirror_spacing_tracker,
                                                                                        num_plates,
                                                                                        current_plate_separation)
        orpheus_motors.wait_for_motors()
        current_resonator_length = current_resonator_length+inch_to_cm(increment_distance)
        current_plate_separation = new_plate_separation
        print("plate separation: {}".format(current_plate_separation))

except KeyboardInterrupt:
    print('stopping motors and modemap measurement')
    orpheus_motors.stop_and_kill()
    logger.stop_modemap()
logger.stop_modemap()
