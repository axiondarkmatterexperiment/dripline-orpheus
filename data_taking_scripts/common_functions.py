from dripline.core import Interface
import time

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

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

def move_motors_to_zero(list_of_motors,0):
    for motor_command in list_of_motors:
        the_interface.set(motor_command, 0)

def data_logging_sequence(a_sec_wait_for_na_averaging):
    print('Setting na_measurement_status to start_measurement')
    the_interface.set('na_measurement_status', 'start_measurement')
    print('Logging list of endpoints')
    the_interface.cmd('modemap_snapshot_no_iq', 'log_entities')
    the_interface.get('na_s21_iq_data')
    time.sleep(sec_wait_for_na_averaging)
    the_interface.cmd('na_s21_iq_data', 'scheduled_log')
    the_interface.get('na_s11_iq_data')
    time.sleep(sec_wait_for_na_averaging)
    the_interface.cmd('na_s11_iq_data', 'scheduled_log')
    print('Setting na_measurement_status to stop_measurement')
    the_interface.set('na_measurement_status', 'stop_measurement')
