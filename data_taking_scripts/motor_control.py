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

initial_mirror_holder_spacing = cm_to_inch(float(input('Enter initial mirror holder spacing (in cm): ')))
distance_to_move = float(input('Enter the distance to move in cm (Empty resonator modemap is usually 3): '))
resolution = int(input('Enter the number of measurements needed: '))
increment_distance = cm_to_inch(distance_to_move/resolution)

#time to wait
sec_wait_for_na_averaging = 2
#important parameters. all units are in inches
plate_thickness = 1/8
num_plates = 4
#set up motors and logger
orpheus_motors = OrpheusMotors(auths_file, motors_to_move)
logger = DataLogger(auths_file)

logger.initialize_na_settings_for_modemap(averages = 16)
orpheus_motors.move_to_zero()
orpheus_motors.wait_for_motors()
mirror_spacing_tracker = initial_mirror_holder_spacing
initial_plate_separation = orpheus_motors.plate_separation(mirror_spacing_tracker,num_plates)

#Send alert saying you are starting the modemap measurement
print('Starting modemap measurement')
logger.start_modemap('Debugging dielectrics setup')

current_resonator_length = inch_to_cm(initial_mirror_holder_spacing)+1.0497
wide_scan_start_freq = 15e9
wide_scan_stop_freq = 18e9
narrow_scan_span = 200e6
try:
    i = 0
    override = 0 # 0 is false, 1 is true
    while i <= abs(distance_to_move):
        print('Resonator length: {}'.format(current_resonator_length))
        resonant_freq = logger.flmn(0,0,18,current_resonator_length)
        narrow_scan_start_freq = resonant_freq - narrow_scan_span/2
        narrow_scan_stop_freq = resonant_freq + narrow_scan_span/2
        #print(resonant_freq)
        #log widescan
        logger.log_modemap(wide_scan_start_freq, wide_scan_stop_freq, sec_wait_for_na_averaging, 'widescan')
        #log narrowscan
        logger.log_modemap(narrow_scan_start_freq, narrow_scan_stop_freq, sec_wait_for_na_averaging, 'narrowscan')

        i = round((i+inch_to_cm(increment_distance)),4)
        if i <= abs(distance_to_move):
            print("now scanning distance = " +str(i))
            mirror_spacing_tracker, new_plate_separation = orpheus_motors.move_by_increment(increment_distance,
                                                                                            plate_thickness,
                                                                                            mirror_spacing_tracker,
                                                                                            num_plates,
                                                                                            initial_plate_separation)
            orpheus_motors.wait_for_motors()
            current_resonator_length = current_resonator_length+inch_to_cm(increment_distance)
            initial_plate_separation = new_plate_separation
        print("plate separation: {}".format(initial_plate_separation))
        if override == 0:
            print('')
            prompt = input("Press 'o' to override this prompt. Press any other key to continue: ")
            if prompt == 'o':
                override = 1

except KeyboardInterrupt:
    print('stopping motors and modemap measurement')
    orpheus_motors.stop_and_kill()
    logger.stop_modemap()
logger.stop_modemap()
