from dripline.core import Interface
import time
class DriplineLogger:

    def __init__(self, auths_file):
        self.auths_file = auths_file
        self.cmd_interface = Interface(dripline_config={'auth-file': self.auths_file})

    def log_modemap(self, sleep_time):
        print('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        print('Logging list of endpoints')
        self.cmd_interface.cmd('modemap_snapshot_no_iq', 'log_entities')
        self.cmd_interface.get('na_s21_iq_data')
        time.sleep(sleep_time)
        self.cmd_interface.cmd('na_s21_iq_data', 'scheduled_log')
        self.cmd_interface.get('na_s11_iq_data')
        time.sleep(sleep_time)
        self.cmd_interface.cmd('na_s11_iq_data', 'scheduled_log')
        print('Setting na_measurement_status to stop_measurement')
        self.cmd_interface.set('na_measurement_status', 'stop_measurement')

    def start_modemap(self):
        self.cmd_interface.set('modemap_measurement_status', 'start_measurement')

    def stop_modemap(self):
        self.cmd_interface.set('modemap_measurement_status', 'stop_measurement')

    
