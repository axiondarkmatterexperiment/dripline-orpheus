from dripline.core import Interface
import time

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

