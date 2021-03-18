from dripline.core import Interface
import time
import math
import numpy as np
from fitting_functions import data_lorentzian_fit
from fitting_functions import calculate_coupling
from fitting_functions import reflection_deconvolve_line
from scipy.interpolate import interp1d
from fitting_functions import func_pow_reflected

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

    def initialize_na_settings_for_modemap(self,start_freq = 15e9, stop_freq = 18e9, power = (-5) , averages = 0, average_enable = 1, sweep_points = 2000):
        self.cmd_interface.set('na_start_freq', start_freq)
        self.cmd_interface.set('na_stop_freq', stop_freq)
        self.cmd_interface.set('na_power', power)
        self.cmd_interface.set('na_average_enable', average_enable)
        if average_enable == 1:
            self.cmd_interface.set('na_averages', averages)
        self.cmd_interface.set('na_sweep_points', sweep_points)

    def guess_resonant_frequency(self, start_freq, stop_freq, averaging_time = 2):
        self.cmd_interface.set('na_start_freq', start_freq)
        self.cmd_interface.set('na_stop_freq', stop_freq)
        self.switch_transmission_path()
        s21_iq = self.cmd_interface.get('s21_iq_transmission_data').payload.to_python()['value_cal']
        time.sleep(averaging_time)
        s21_iq = self.cmd_interface.get('s21_iq_transmission_data').payload.to_python()['value_cal']
        s21_re, s21_im = np.array(s21_iq[::2]), np.array(s21_iq[1::2])
        s21_pow = s21_re**2 + s21_im**2
        if stop_freq > 18e9:
            freq = np.linspace(start_freq, 18e9, num = len(s21_pow))
        else:
            freq = np.linspace(start_freq, stop_freq, num = len(s21_pow))
        
        ind_resonant = np.argmax(s21_pow)
        resonant_f = freq[ind_resonant]
        return resonant_f
        
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

    def log_vna_data(self,start_freq, stop_freq, sec_wait_for_na_averaging, na_iq_data_notes= '', autoscale = False):
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        print('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
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

    def log_transmission_switches(self, start_freq, stop_freq, sec_wait_for_na_averaging, na_iq_data_notes= '', autoscale = False, fitting = False):
        print('Measuring transmission with VNA')
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        print('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        self.cmd_interface.set('na_measurement_status_explanation', na_iq_data_notes)
        print('Logging list of endpoints')
        self.cmd_interface.cmd('modemap_snapshot_no_iq', 'log_entities')
        self.switch_transmission_path()
        self.cmd_interface.get('s21_iq_transmission_data')
        time.sleep(sec_wait_for_na_averaging)
        self.cmd_interface.cmd('s21_iq_transmission_data', 'scheduled_log')
        if fitting:
            s21_iq = self.cmd_interface.get('s21_iq_transmission_data').payload.to_python()['value_cal']
            s21_re, s21_im = np.array(s21_iq[::2]), np.array(s21_iq[1::2])
            s21_pow = s21_re**2 + s21_im**2
            freq = np.linspace(start_freq, stop_freq, num = len(s21_pow))
            popt_transmission, pcov_transmission = data_lorentzian_fit(s21_pow, freq, 'transmission')
            perr_transmission = np.sqrt(np.diag(pcov_transmission))
            print('Transmission lorentzian fitted parameters')
            print(popt_transmission)
            self.cmd_interface.set('f_transmission', popt_transmission[0])
            self.cmd_interface.set('sig_f_transmission', perr_transmission[0])
            self.cmd_interface.set('Q_transmission', popt_transmission[1])
            self.cmd_interface.set('sig_Q_transmission', perr_transmission[1])
            self.cmd_interface.set('dy_transmission', popt_transmission[2])
            self.cmd_interface.set('sig_dy_transmission', perr_transmission[2])
            self.cmd_interface.set('C_transmission', popt_transmission[3])
            self.cmd_interface.set('sig_C_transmission', perr_transmission[3])
        self.cmd_interface.set('na_measurement_status', 'stop_measurement')

    def log_reflection_switches(self, start_freq, stop_freq, sec_wait_for_na_averaging, na_iq_data_notes= '', autoscale = False, fitting = False):
        print('Measuring reflection with VNA')
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        print('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        self.cmd_interface.set('na_measurement_status_explanation', na_iq_data_notes)
        print('Logging list of endpoints')
        self.cmd_interface.cmd('modemap_snapshot_no_iq', 'log_entities')
        self.switch_reflection_path()
        self.cmd_interface.get('s21_iq_reflection_data')
        time.sleep(sec_wait_for_na_averaging)
        self.cmd_interface.cmd('s21_iq_reflection_data', 'scheduled_log')
        if fitting:
            s11_iq = self.cmd_interface.get('s21_iq_reflection_data').payload.to_python()['value_cal']
            s11_re, s11_im = np.array(s11_iq[::2]), np.array(s11_iq[1::2])
            s11_pow = s11_re**2 + s11_im**2
            s11_mag = np.sqrt(s11_pow)
            s11_phase = np.unwrap(np.angle(s11_re+1j*s11_im))
            freq = np.linspace(start_freq, stop_freq, num = len(s11_pow))
            popt_reflection, pcov_reflection = data_lorentzian_fit(s11_pow, freq, 'reflection')
            perr_reflection = np.sqrt(np.diag(pcov_reflection))
            print('Reflection lorentzian fitted parameters')
            print(popt_reflection)
            self.cmd_interface.set('f_reflection', popt_reflection[0])
            self.cmd_interface.set('Q_reflection', popt_reflection[1])
            self.cmd_interface.set('dy_reflection', popt_reflection[2])
            self.cmd_interface.set('C_reflection', popt_reflection[3])

            #TODO figure out how to deal with this weird edge case later. This doesn't seem physical
            if popt_reflection[2] >= popt_reflection[3]:
                beta = 1
            else:
                # Gam_res is reflection coeffient Gamma of the resonator
                Gam_res_mag, Gam_res_phase = reflection_deconvolve_line(freq, s11_mag, s11_phase, popt_reflection[3])
                # Calculates magnitude of Gamma_cavity by plugging resonant frequency into fitted function
                Gam_res_mag_fo = np.sqrt(func_pow_reflected(popt_reflection[0], *popt_reflection)*1/popt_reflection[3])
                Gam_res_interp_phase = interp1d(freq, Gam_res_phase, kind='cubic')
                # calculate phase of Gamma_cavity at resonant frequency by interpolating
                # data.
                Gam_res_phase_fo = Gam_res_interp_phase(popt_reflection[0])
                beta = calculate_coupling(Gam_res_mag_fo, Gam_res_phase_fo)
            print("Antenna coupling : {}".format(beta))
            self.cmd_interface.set('antenna_coupling', beta)
        self.cmd_interface.set('na_measurement_status', 'stop_measurement')



    def log_transmission_reflection_switches(self,start_freq, stop_freq, sec_wait_for_na_averaging, na_iq_data_notes= '', autoscale = False, fitting = False):
        print('VNA reflection measurement')
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        print('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        self.cmd_interface.set('na_measurement_status_explanation', na_iq_data_notes)
        print('Logging list of endpoints')
        self.cmd_interface.cmd('modemap_snapshot_no_iq', 'log_entities')
        # get transmission data
        self.switch_transmission_path()
        self.cmd_interface.get('s21_iq_transmission_data')
	    #  wait for network analyzer to finish several sweeps for averaging
        time.sleep(sec_wait_for_na_averaging)
        if autoscale:
            self.cmd_interface.set('na_commands', 'autoscale')
        self.cmd_interface.cmd('s21_iq_transmission_data', 'scheduled_log')
        if fitting:
            s21_iq = self.cmd_interface.get('s21_iq_transmission_data').payload.to_python()['value_cal']
            s21_re, s21_im = np.array(s21_iq[::2]), np.array(s21_iq[1::2])
            s21_pow = s21_re**2 + s21_im**2
            freq = np.linspace(start_freq, stop_freq, num = len(s21_pow))
            popt_transmission, pcov_transmission = data_lorentzian_fit(s21_pow, freq, 'transmission')
            perr_transmission = np.sqrt(np.diag(pcov_transmission))
            print('Transmission lorentzian fitted parameters')
            print(popt_transmission)
            self.cmd_interface.set('f_transmission', popt_transmission[0])
            self.cmd_interface.set('sig_f_transmission', perr_transmission[0])
            self.cmd_interface.set('Q_transmission', popt_transmission[1])
            self.cmd_interface.set('sig_Q_transmission', perr_transmission[1])
            self.cmd_interface.set('dy_transmission', popt_transmission[2])
            self.cmd_interface.set('sig_dy_transmission', perr_transmission[2])
            self.cmd_interface.set('C_transmission', popt_transmission[3])
            self.cmd_interface.set('sig_C_transmission', perr_transmission[3])


        # get reflection data
        self.switch_reflection_path()
        self.cmd_interface.get('s21_iq_reflection_data')
	    #  wait for network analyzer to finish several sweeps for averaging
        time.sleep(sec_wait_for_na_averaging)
        if autoscale:
            self.cmd_interface.set('na_commands', 'autoscale')
        self.cmd_interface.cmd('s21_iq_reflection_data', 'scheduled_log')
        if fitting:
            s11_iq = self.cmd_interface.get('s21_iq_reflection_data').payload.to_python()['value_cal']
            s11_re, s11_im = np.array(s11_iq[::2]), np.array(s11_iq[1::2])
            s11_pow = s11_re**2 + s11_im**2
            s11_mag = np.sqrt(s11_pow)
            s11_phase = np.unwrap(np.angle(s11_re+1j*s11_im))
            popt_reflection, pcov_reflection = data_lorentzian_fit(s11_pow, freq, 'reflection')
            perr_reflection = np.sqrt(np.diag(pcov_reflection))
            print('Reflection lorentzian fitted parameters')
            print(popt_reflection)
            self.cmd_interface.set('f_reflection', popt_reflection[0])
            self.cmd_interface.set('sig_f_reflection', perr_reflection[0])
            self.cmd_interface.set('Q_reflection', popt_reflection[1])
            self.cmd_interface.set('sig_Q_reflection', perr_reflection[1])
            self.cmd_interface.set('dy_reflection', popt_reflection[2])
            self.cmd_interface.set('sig_dy_reflection', perr_reflection[2])
            self.cmd_interface.set('C_reflection', popt_reflection[3])
            self.cmd_interface.set('sig_C_reflection', perr_reflection[3])

            #TODO figure out how to deal with this weird edge case later. This doesn't seem physical
            if popt_reflection[2] >= popt_reflection[3]:
                beta = 1
            else:
                # Gam_res is reflection coeffient Gamma of the resonator
                Gam_res_mag, Gam_res_phase = reflection_deconvolve_line(freq, s11_mag, s11_phase, popt_reflection[3])
                # Calculates magnitude of Gamma_cavity by plugging resonant frequency into fitted function
                Gam_res_mag_fo = np.sqrt(func_pow_reflected(popt_reflection[0], *popt_reflection)*1/popt_reflection[3])
                Gam_res_interp_phase = interp1d(freq, Gam_res_phase, kind='cubic')
                # calculate phase of Gamma_cavity at resonant frequency by interpolating
                # data.
                Gam_res_phase_fo = Gam_res_interp_phase(popt_reflection[0])
                beta = calculate_coupling(Gam_res_mag_fo, Gam_res_phase_fo)
            print("Antenna coupling : {}".format(beta))
            self.cmd_interface.set('antenna_coupling', beta)

        self.cmd_interface.set('na_measurement_status', 'stop_measurement')
    def digitize(self, resonant_frequency, if_center, digitization_time):
        print('Now digitizing')
        self.switch_digitization_path()
        self.cmd_interface.set('lo_freq', resonant_frequency - if_center)
        self.cmd_interface.cmd('fast_daq', 'start-run')
        time.sleep(digitization_time)
        daq_status = self.cmd_interface.get('fast_daq', specifier='daq-status').payload.to_python()
        # check if digitizer is done digitizing.
        while daq_status['server']['status'] == 'Running':
            daq_status = self.cmd_interface.get('fast_daq', specifier='daq-status').payload.to_python()
            time.sleep(1)


    def start_modemap(self, modemap_notes = ''):
        # TODO throw error if notes isn't a string.
        self.cmd_interface.set('modemap_measurement_status', 'start_measurement')
        # TODO write if statement
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

    def switch_reflection_path(self):
        print('Switching to reflection path')
        self.cmd_interface.set('switch_ps_select_channel', 'CH2')
        time.sleep(0.1)
        self.cmd_interface.set('switch_ps_channel_output', 0)
        time.sleep(0.1)
        self.cmd_interface.set('switch_ps_select_channel', 'CH1')
        time.sleep(0.1)
        self.cmd_interface.set('switch_ps_channel_output', 1)
        time.sleep(0.1)

    def switch_transmission_path(self):
        print('Switching to transmission path')
        time.sleep(0.1)
        self.cmd_interface.set('switch_ps_select_channel', 'CH2')
        time.sleep(0.1)
        self.cmd_interface.set('switch_ps_channel_output', 0)
        time.sleep(0.1)
        self.cmd_interface.set('switch_ps_select_channel', 'CH1')
        time.sleep(0.1)
        self.cmd_interface.set('switch_ps_channel_output', 0)
        time.sleep(0.1)

    def switch_digitization_path(self):
        self.cmd_interface.set('switch_ps_select_channel', 'CH2')
        self.cmd_interface.set('switch_ps_channel_output', 1)
