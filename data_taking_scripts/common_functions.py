from dripline.core import Interface
import time

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

def initialize_na_settings_for_modemap(start_freq = 15e9, stop_freq = 18e9, power = -5 , averages = 0, sweep_points = 10001):
    the_interface.set('na_start_freq', start_freq)
    the_interface.set('na_stop_freq', stop_freq)
    the_interface.set('na_power', power)
    the_interface.set('na_averages', averages)
    the_interface.set('na_sweep_points', sweep_points)

def plate_separation(length, num_plates):
    return length/(num_plates+1)
#functions to convert distances into steps
def plates_distance_to_steps(distance,holder_thickness,plate_thickness,lip_thickness,pitch=(1/20), steps_per_rotation = 20000):
    holder_center = holder_thickness/2
    plate_center = lip_thickness + plate_thickness/2
    gap = holder_center - plate_center
    actual_distance = distance + gap
    num_pitch_lengths = actual_distance/pitch #these many complete rotations
    steps = steps_per_rotation * num_pitch_lengths
    return int(round(steps))
def curved_mirror_distance_to_steps(distance, pitch = (1/20), steps_per_rotation = 20000):
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

def move_motors_to_zero(list_of_motors):
    for motor_command in list_of_motors:
        the_interface.set(motor_command, 0)

def data_logging_sequence(a_sec_wait_for_na_averaging):
    print('Setting na_measurement_status to start_measurement')
    the_interface.set('na_measurement_status', 'start_measurement')
    print('Logging list of endpoints')
    the_interface.cmd('modemap_snapshot_no_iq', 'log_entities')

    # switch the na to read s21
    the_interface.get('na_s21_iq_data')
    #  autoscale the window so that the s21 data fits. This is so I can watch the data while it's being recorded.
    the_interface.set('na_commands', 'autoscale')
    #wait for network analyzer to finish several sweeps for averaging
    time.sleep(a_sec_wait_for_na_averaging)
    # then record s21 data into database
    the_interface.cmd('na_s21_iq_data', 'scheduled_log')
    # switch the na to read s11
    the_interface.get('na_s11_iq_data')
    #  autoscale the window so that the s11 data fits. This is so I can watch the data while it's being recorded.
    the_interface.set('na_commands', 'autoscale')
    #wait for network analyzer to finish several sweeps for averaging
    time.sleep(a_sec_wait_for_na_averaging)
    # then record s11 data into database
    the_interface.cmd('na_s11_iq_data', 'scheduled_log')
    print('Setting na_measurement_status to stop_measurement')
    the_interface.set('na_measurement_status', 'stop_measurement')

def start_modemap():
    the_interface.set('modemap_measurement_status', 'start_measurement')

def stop_modemap():
    the_interface.set('modemap_measurement_status', 'stop_measurement')
