from dripline.core import Interface
import time
class DataLogger:

    def __init__(self, auths_file):
        self.auths_file = auths_file
        self.cmd_interface = Interface(dripline_config={'auth-file': self.auths_file})

    def initialize_na_settings_for_modemap(start_freq = 15e9, stop_freq = 18e9, power = (-5) , averages = 0, sweep_points = 10001):
        self.cmd_interface.set('na_start_freq', start_freq)
        self.cmd_interface.set('na_stop_freq', stop_freq)
        self.cmd_interface.set('na_power', power)
        self.cmd_interface.set('na_averages', averages)
        self.cmd_interface.set('na_sweep_points', sweep_points)

    def log_modemap(self, sec_wait_for_na_averaging):
        print('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        print('Logging list of endpoints')
        self.cmd_interface.cmd('modemap_snapshot_no_iq', 'log_entities')

        self.cmd_interface.get('na_s21_iq_data')
	    #  autoscale the window so that the s21 data fits. This is so I can watch the data while it's being recorded.
        self.cmd_interface.set('na_commands', 'autoscale')
	    #  wait for network analyzer to finish several sweeps for averaging
        time.sleep(sec_wait_for_na_averaging)
        self.cmd_interface.cmd('na_s21_iq_data', 'scheduled_log')

        self.cmd_interface.get('na_s11_iq_data')
        #  autoscale the window so that the s11 data fits. This is so I can watch the data while it's being recorded.
        self.cmd_interface.set('na_commands', 'autoscale')
        #  wait for network analyzer to finish several sweeps for averaging
        time.sleep(sec_wait_for_na_averaging)
        self.cmd_interface.cmd('na_s11_iq_data', 'scheduled_log')
        print('Setting na_measurement_status to stop_measurement')
        self.cmd_interface.set('na_measurement_status', 'stop_measurement')

    def start_modemap(self):
        self.cmd_interface.set('modemap_measurement_status', 'start_measurement')

    def stop_modemap(self):
        self.cmd_interface.set('modemap_measurement_status', 'stop_measurement')

    def log_s21(self, sleep_time = 0):
        self.cmd_interface.get('na_s21_iq_data')
        time.sleep(sleep_time)
        self.cmd_interface.cmd('na_s21_iq_data', 'scheduled_log')

    def log_s11(self, sleep_time = 0):
        self.cmd_interface.get('na_s11_iq_data')
        time.sleep(sleep_time)
        self.cmd_interface.cmd('na_s11_iq_data', 'scheduled_log')
