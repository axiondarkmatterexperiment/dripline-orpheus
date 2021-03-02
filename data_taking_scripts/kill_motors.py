'''
    File name: predict_res_freq_tem.py
    Author: Raphael Cervantes
    Date created: 3/02/2021
    Date last modified: 3/02/2021
    Python Version: 3.6
    Description: stops and kills all the motors.
'''

from dripline.core import Interface
import time
import common_functions

auths_file = '/etc/rabbitmq-secret/authentications.json'
the_interface = Interface(dripline_config={'auth-file': auths_file})

the_interface.set(curved_mirror_status_command, stop_and_kill)
the_interface.set(top_dielectric_plate_command, stop_and_kill)
the_interface.set(bottom_dielectric_plate_command, stop_and_kill)
