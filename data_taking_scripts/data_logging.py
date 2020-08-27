from dripline.core import Interface
import time
import math
class DataLogger:

    def __init__(self, auths_file):
        self.auths_file = auths_file
        self.cmd_interface = Interface(dripline_config={'auth-file': self.auths_file})
        self.list_of_na_entities = ['na_start_freq', 'na_stop_freq',
                                     'na_power', 'na_averages','na_average_enable']
        self.list_of_motor_entities = ['curved_mirror_steps', 'bottom_dielectric_plate_steps',
                                       'top_dielectric_plate_steps']

    def set_start_freq(self,start_freq):
        self.cmd_interface.set('na_start_freq', start_freq)

    def set_stop_freq(self,stop_freq):
        self.cmd_interface.set('na_stop_freq', stop_freq)

    def initialize_na_settings_for_modemap(self,start_freq = 15e9, stop_freq = 18e9, power = (-5) , averages = 0, sweep_points = 2000):
        self.cmd_interface.set('na_start_freq', start_freq)
        self.cmd_interface.set('na_stop_freq', stop_freq)
        self.cmd_interface.set('na_power', power)
        self.cmd_interface.set('na_averages', averages)
        self.cmd_interface.set('na_sweep_points', sweep_points)
        #  set up traces.
        self.cmd_interface.cmd('na_s21_iq_data', 'scheduled_log')
        self.cmd_interface.cmd('na_s11_iq_data_trace2', 'scheduled_log')

    def log_motor_steps(self):
        for entitiy in self.list_of_motor_entities:
            self.cmd_interface.cmd(entitiy, 'scheduled_log')

    def log_s21s11(self,start_freq, stop_freq, sec_wait_for_na_averaging):
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        for entity in self.list_of_na_entities:
            self.cmd_interface(entity,'scheduled_log')
	#  wait for network analyzer to finish several sweeps for averaging
        time.sleep(sec_wait_for_na_averaging)
        self.cmd_interface.cmd('na_s21_iq_data', 'scheduled_log')
        self.cmd_interface.cmd('na_s11_iq_data_trace2', 'scheduled_log')

    def log_modemap(self,start_freq, stop_freq, sec_wait_for_na_averaging, na_iq_data_notes= None, autoscale=False):
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        print('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        if not na_iq_data_notes == None:
            self.cmd_interface.set('na_measurement_status_explanation', na_iq_data_notes)
        print('Logging list of endpoints')
        self.cmd_interface.cmd('modemap_snapshot_no_iq', 'log_entities')

	#  wait for network analyzer to finish several sweeps for averaging
        time.sleep(sec_wait_for_na_averaging)
        if autoscale:
            self.cmd_interface.set('na_commands', 'autoscale')
        self.cmd_interface.cmd('na_s21_iq_data', 'scheduled_log')
        self.cmd_interface.cmd('na_s11_iq_data_trace2', 'scheduled_log')
        print('Setting na_measurement_status to stop_measurement')
        self.cmd_interface.set('na_measurement_status', 'stop_measurement')

    def start_modemap(self, modemap_notes = None):
        # TODO throw error if notes isn't a string.
        self.cmd_interface.set('modemap_measurement_status', 'start_measurement')
        # TODO write if statement
        if not modemap_notes == None:
            self.cmd_interface.set('modemap_measurement_status_explanation', modemap_notes)

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

    def flmn(self,l, m, n, length,eps_r = 1, r0 = 33):
        ''' Calculates the resonant frequency for TEM 00n mode.
            Input units should be in cm. '''
        c = 299792458.0
        pi = math.pi
        v = c/math.sqrt(eps_r)
        sum = 1+l+m
        l_in_m = length/100
        r0_m = r0/100

        arccos_term = math.acos(1-2*l_in_m/r0_m)
        n_term = ((n+1)*v/2)/l_in_m
        lm_term = sum*v/(4*l_in_m*pi)
        resonant_frequency = n_term + lm_term*arccos_term
        return resonant_frequency
