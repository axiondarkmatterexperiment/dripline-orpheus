'''
Collection of utility functions used while data taking.
'''

from dripline.core import Interface
import time
import math
import numpy as np
from fitting_functions import data_lorentzian_fit
from fitting_functions import calculate_coupling
from fitting_functions import reflection_deconvolve_line
from fitting_functions import deconvolve_phase
from scipy.interpolate import interp1d
from fitting_functions import func_pow_reflected
import uncertainties
from uncertainties import ufloat
from uncertainties import umath
import logging
logging.basicConfig(level=logging.INFO)
dl_logger = logging.getLogger(__name__)

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

    def initialize_na_settings_for_modemap(self,start_freq = 15e9, stop_freq = 18e9, power = (-5) , averages = 0, average_enable = 1, sweep_points = 2000, ifbw = 50e3):
        
        self.cmd_interface.set('na_power', power)
        self.cmd_interface.set('na_start_freq', start_freq)
        self.cmd_interface.set('na_stop_freq', stop_freq)
        self.cmd_interface.set('na_average_enable', average_enable)
        if average_enable == 1:
            self.cmd_interface.set('na_averages', averages)
        self.cmd_interface.set('na_sweep_points', sweep_points)
        self.cmd_interface.set('na_if_band', ifbw)

    def guess_resonant_frequency(self, start_freq, stop_freq, averaging_time = 2):
        self.cmd_interface.set('na_start_freq', start_freq)
        self.cmd_interface.set('na_stop_freq', stop_freq)
        self.switch_transmission_path()
        s21_iq = self.cmd_interface.get('s21_iq_transmission_data').payload.to_python()['value_cal']
        self.cmd_interface.set('na_commands', 'clear_averages')
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

    def log_vna_data(self,start_freq, stop_freq, sec_wait_for_na_averaging, na_iq_data_notes= '', autoscale = False):
        '''
        Used when there is no amplifier attached to the strongly coupled port. Straightforward s21, s11 measurement to obtain reflection and transmission measurements.
        Assumes s11 is on the second trace..
        '''
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        dl_logger.info('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        self.cmd_interface.set('na_measurement_status_explanation', na_iq_data_notes)
        dl_logger.info('Logging list of endpoints')
        self.cmd_interface.cmd('axion_data_taking_short_snapshot', 'log_entities')
	#  wait for network analyzer to finish several sweeps for averaging
        time.sleep(sec_wait_for_na_averaging)
        if autoscale:
            self.cmd_interface.set('na_commands', 'autoscale')
        self.cmd_interface.cmd('na_s21_iq_data', 'scheduled_log')
        self.cmd_interface.cmd('na_s11_iq_data_trace2', 'scheduled_log')
        dl_logger.info('Setting na_measurement_status to stop_measurement')
        self.cmd_interface.set('na_measurement_status', 'stop_measurement')

    def log_transmission_switches(self, start_freq, stop_freq, sec_wait_for_na_averaging, na_iq_data_notes = '', autoscale = False, fitting = False, transmission_endpoint = None, track_max_transmission = False):
        dl_logger.info('Measuring transmission with VNA')
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        dl_logger.info('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status_explanation', na_iq_data_notes)
        self.switch_transmission_path()
        self.cmd_interface.set('na_commands', 'clear_averages')
        self.log_switch_settings()
        self.cmd_interface.get(transmission_endpoint)
        time.sleep(sec_wait_for_na_averaging)
        self.cmd_interface.cmd(transmission_endpoint, 'scheduled_log')
        if fitting or track_max_transmission:
            s21_iq = self.cmd_interface.get(transmission_endpoint).payload.to_python()['value_cal']
            s21_re, s21_im = np.array(s21_iq[::2]), np.array(s21_iq[1::2])
            s21_pow = s21_re**2 + s21_im**2
            freq = np.linspace(start_freq, stop_freq, num = len(s21_pow))
        if track_max_transmission:
            self.cmd_interface.set('transmission_max', np.max(s21_pow))
        if fitting:
            try:
                dl_logger.warning('Could not perform a proper fit')
                popt_transmission, pcov_transmission = data_lorentzian_fit(s21_pow, freq, 'transmission')
            except:
                sys.exit()
            perr_transmission = np.sqrt(np.diag(pcov_transmission)) #pcov_transmission are covariances, so the diagonal is just the variances, so sqrt it to get the std dev.
            dl_logger.info('Transmission lorentzian fitted parameters')
            dl_logger.info('f, Q, dy, C')
            dl_logger.info(popt_transmission)
            #the following three lines were added by me, JS... Looking at the documentation of curve fitting I believe that this should work
            dl_logger.info('Transmission lorentzian fitted parameter errors')
            dl_logger.info('f_sigma, Q_sigma, dy_sigma, C_sigma')
            dl_logger.info(perr_transmission)

            if transmission_endpoint == 's21_iq_transmission_data_stability_check':
                self.cmd_interface.set('f_transmission_stability_check', popt_transmission[0])
                self.cmd_interface.set('Q_transmission_stability_check', popt_transmission[1])
                self.cmd_interface.set('dy_transmission_stability_check', popt_transmission[2])
                self.cmd_interface.set('C_transmission_stability_check', popt_transmission[3])
            else:
                self.cmd_interface.set('f_transmission', popt_transmission[0])
                self.cmd_interface.set('sig_f_transmission', perr_transmission[0])
                self.cmd_interface.set('Q_transmission', popt_transmission[1])
                self.cmd_interface.set('sig_Q_transmission', perr_transmission[1])
                self.cmd_interface.set('dy_transmission', popt_transmission[2])
                self.cmd_interface.set('sig_dy_transmission', perr_transmission[2])
                self.cmd_interface.set('C_transmission', popt_transmission[3])
                self.cmd_interface.set('sig_C_transmission', perr_transmission[3])
        self.cmd_interface.set('na_measurement_status', 'stop_measurement')

    def log_reflection_switches(self, start_freq, stop_freq, sec_wait_for_na_reflection_averaging, na_iq_data_notes = '', autoscale = False, fitting = False, reflection_endpoint = 's21_iq_reflection_data', track_max_reflection = False):
        dl_logger.info('Measuring reflection with VNA')
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        dl_logger.info('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status_explanation', na_iq_data_notes)
        self.switch_reflection_path()
        self.log_switch_settings()
        self.cmd_interface.get(reflection_endpoint)
        self.cmd_interface.set('na_commands', 'clear_averages')
        time.sleep(sec_wait_for_na_reflection_averaging)
        self.cmd_interface.cmd(reflection_endpoint, 'scheduled_log')
        if fitting or track_max_reflection:
            s11_iq = self.cmd_interface.get(reflection_endpoint).payload.to_python()['value_cal']
            s11_re, s11_im = np.array(s11_iq[::2]), np.array(s11_iq[1::2])
            s11_pow = s11_re**2 + s11_im**2
            s11_mag = np.sqrt(s11_pow)
            s11_phase = np.unwrap(np.angle(s11_re+1j*s11_im))
            freq = np.linspace(start_freq, stop_freq, num = len(s11_pow))
        if track_max_reflection:
            self.cmd_interface.set('reflection_max', np.max(s11_pow))
        if fitting:
            try:
                popt_reflection, pcov_reflection = data_lorentzian_fit(s11_pow, freq, 'reflection')
            except:
                dl_logger.warning('Could not perform a proper fit')
                sys.exit()
            perr_reflection = np.sqrt(np.diag(pcov_reflection))
            dl_logger.info('Reflection lorentzian fitted parameters')
            dl_logger.info('f, Q, dy, C')
            dl_logger.info(popt_reflection)
            self.cmd_interface.set('f_reflection', popt_reflection[0])
            self.cmd_interface.set('Q_reflection', popt_reflection[1])
            self.cmd_interface.set('dy_reflection', popt_reflection[2])
            self.cmd_interface.set('C_reflection', popt_reflection[3])
            #the following three lines were added by me, JS... Looking at the documentation of curve fitting I believe that this should work
            dl_logger.info('Reflection lorentzian fitted parameter errors')
            dl_logger.info('f_sigma, Q_sigma, dy_sigma, C_sigma')
            dl_logger.info(perr_reflection)

            cavity_phase = deconvolve_phase(freq, s11_phase)
            
            dy_over_C = popt_reflection[2]/popt_reflection[3]
            #dy_over_C_err = perr_reflection[2]*perr_reflection[3] 
            dy=popt_reflection[2]
            C=popt_reflection[3]
            dy_err=perr_reflection[2]
            C_err=perr_reflection[3]
            dy_over_C_err = np.sqrt(dy_err**2/C**2 + dy**2*C_err**2/C**4) #I believe this is the proper error propagation.
            dy_over_C=ufloat(dy/C, dy_over_C_err)
            
            antenna_coupling = calculate_coupling(dy_over_C, cavity_phase)


            dl_logger.info("Antenna coupling : {}".format(antenna_coupling)) #Do I need to alter this line since antenna_coupling is a ufloat now? -JS
            self.cmd_interface.set('antenna_coupling', antenna_coupling.n)
            self.cmd_interface.set('antenna_coupling_error', antenna_coupling.s)

            Qu_reflection = popt_reflection[1]*(1+antenna_coupling)
            dl_logger.info("Unloaded Q from reflection measurement is : {}".format(Qu_reflection))
            self.cmd_interface.set('Q_unloaded_reflection', Qu_reflection)

        self.cmd_interface.set('na_measurement_status', 'stop_measurement')



    def log_transmission_reflection_switches(self,start_freq, stop_freq, sec_wait_for_na_averaging, na_iq_data_notes= '', autoscale = False, fitting = False):
        dl_logger.info('VNA reflection measurement')
        self.set_start_freq(start_freq)
        self.set_stop_freq(stop_freq)
        dl_logger.info('Setting na_measurement_status to start_measurement')
        self.cmd_interface.set('na_measurement_status', 'start_measurement')
        self.cmd_interface.set('na_measurement_status_explanation', na_iq_data_notes)
        dl_logger.info('Logging list of endpoints')
        self.cmd_interface.cmd('axion_data_taking_short_snapshot', 'log_entities')
        # get transmission data
        self.switch_transmission_path()
        self.cmd_interface.get('s21_iq_transmission_data')
        self.cmd_interface.set('na_commands', 'clear_averages')
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
            try:
                popt_transmission, pcov_transmission = data_lorentzian_fit(s21_pow, freq, 'transmission')
                perr_transmission = np.sqrt(np.diag(pcov_transmission))
                dl_logger.info('Transmission lorentzian fitted parameters')
                dl_logger.info(popt_transmission)
                dl_logger.info(perr_transmission)
                self.cmd_interface.set('f_transmission', popt_transmission[0])
                self.cmd_interface.set('sig_f_transmission', perr_transmission[0])
                self.cmd_interface.set('Q_transmission', np.abs(popt_transmission[1]))
                self.cmd_interface.set('sig_Q_transmission', perr_transmission[1])
                self.cmd_interface.set('dy_transmission', popt_transmission[2])
                self.cmd_interface.set('sig_dy_transmission', perr_transmission[2])
                self.cmd_interface.set('C_transmission', popt_transmission[3])
                self.cmd_interface.set('sig_C_transmission', perr_transmission[3])
            except:
                dl_logger.warning('Could not perform a proper fit')
                sys.exit()


        # get reflection data
        self.switch_reflection_path()
        self.cmd_interface.get('s21_iq_reflection_data')
        self.cmd_interface.set('na_commands', 'clear_averages')
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
            try:
                popt_reflection, pcov_reflection = data_lorentzian_fit(s11_pow, freq, 'reflection')
                perr_reflection = np.sqrt(np.diag(pcov_reflection))

                dl_logger.info('Reflection lorentzian fitted parameters')
                dl_logger.info(popt_reflection)
                dl_logger.info(perr_reflection)
                self.cmd_interface.set('f_reflection', popt_reflection[0])
                self.cmd_interface.set('sig_f_reflection', perr_reflection[0])
                self.cmd_interface.set('Q_reflection', np.abs(popt_reflection[1]))
                self.cmd_interface.set('sig_Q_reflection', perr_reflection[1])
                self.cmd_interface.set('dy_reflection', popt_reflection[2])
                self.cmd_interface.set('sig_dy_reflection', perr_reflection[2])
                self.cmd_interface.set('C_reflection', popt_reflection[3])
                self.cmd_interface.set('sig_C_reflection', perr_reflection[3])

                cavity_phase = deconvolve_phase(freq, s11_phase)
                cavity_reflection_interp_phase = interp1d(freq, cavity_phase, kind='cubic')
                phase_at_resonance = cavity_reflection_interp_phase(popt_reflection[0])

                if popt_reflection[2] >= popt_reflection[3]:
                    antenna_coupling = 1
                else:
                    cavity_reflection_at_resonance = np.sqrt((popt_reflection[3]-popt_reflection[2])/popt_reflection[3])
                    antenna_coupling = calculate_coupling(cavity_reflection_at_resonance, phase_at_resonance)

                dl_logger.info("Antenna coupling : {}".format(antenna_coupling))
                self.cmd_interface.set('antenna_coupling', antenna_coupling)
            except:
                dl_logger.warning('Could not perform a proper fit')

                self.cmd_interface.set('f_reflection', 0)
                self.cmd_interface.set('sig_f_reflection', 0)
                self.cmd_interface.set('Q_reflection', 0)
                self.cmd_interface.set('sig_Q_reflection', 0)
                self.cmd_interface.set('dy_reflection', 0)
                self.cmd_interface.set('sig_dy_reflection', 0)
                self.cmd_interface.set('C_reflection', 0)
                self.cmd_interface.set('sig_C_reflection', 0)

        self.cmd_interface.set('na_measurement_status', 'stop_measurement')

    def disable_all_motors(self):
        self.cmd_interface.set('curved_mirror_status_command', 'motor_disable')
        self.cmd_interface.set('bottom_dielectric_plate_status_command', 'motor_disable')
        self.cmd_interface.set('top_dielectric_plate_status_command', 'motor_disable')

    def enable_all_motors(self):
        self.cmd_interface.set('curved_mirror_status_command', 'motor_enable')
        self.cmd_interface.set('bottom_dielectric_plate_status_command', 'motor_enable')
        self.cmd_interface.set('top_dielectric_plate_status_command', 'motor_enable')

    def _round_to_nearest_multiple(self, a_number, base):
        '''Used to set the LO to the nearest IF bin.'''
        return base*round(a_number/base)


    def digitize(self, resonant_frequency, if_center, fft_bin_width, vna_output_enable = 0, keep_vna_off = False, log_power_monitor = False, disable_motors = False):
        ''' 
        resonant_frequency: Frequency you want the digitizer bandwidth to be centered on.
        if_center: Center of the digitizer window.
        fft_bin_width: width of the digitizer bins. Used to make sure local oscillator is set so that different spectrums are aligned.
        vna_output_enable will be set to 0 unless I'm using the VNA to inject a tone into my resonator
        keep_vna_off: Turns VNA back on if false.
        log_power_monitor: log the power monitor while digitizing if set to True.
        disable_motors: If true, disable the motors while digitizing. This may prevent RFI from leaking in.
        '''
        dl_logger.info('Now digitizing')
        self.cmd_interface.set('na_output_enable', vna_output_enable) #almost always should be 0. Otherwise you would see RFI.
        self.switch_digitization_path()

        if disable_motors: 
            self.disable_all_motors()
        
        #round lo frequency to nearest bin width to make sure RF bins are aligned for  grand spectrum.
        lo_frequency = self._round_to_nearest_multiple(resonant_frequency-if_center, fft_bin_width)
        
        self.cmd_interface.set('lo_freq', lo_frequency)
        time.sleep(0.2)
        try: 
            self.cmd_interface.cmd('fast_daq', 'start-run')
        except:
            dl_logger.info('Fast daq pod isnt running yet. Try again')
            #TODO treat the case where pod will never restart. Logarithmic backoff??
            time.sleep(5)
            self.digitize(resonant_frequency, if_center, fft_bin_width, vna_output_enable, keep_vna_off, log_power_monitor, disable_motors)

        try:
            # constantly check if the digitizer is running. Helpful for checking if the fast_daq endpoint is reachable. If not, then digitization crashed.
            daq_status = self.cmd_interface.get('fast_daq', specifier='daq-status').payload.to_python()
        except:
            dl_logger.info('Fast daq pod seemed to have crashed during digitization. Try again')
            self.digitize(resonant_frequency, if_center, fft_bin_width, vna_output_enable, keep_vna_off, log_power_monitor, disable_motors)

        # check if digitizer is done digitizing.
        while daq_status['server']['status'] == 'Running':
            try:
                # constantly check if the digitizer is running. Helpful for checking if the fast_daq endpoint is reachable. If not, then digitization crashed.
                daq_status = self.cmd_interface.get('fast_daq', specifier='daq-status').payload.to_python()
            except:
                dl_logger.info('Fast daq pod seemed to have crashed during digitization. Try again')
                self.digitize(resonant_frequency, if_center, fft_bin_width, vna_output_enable, keep_vna_off, log_power_monitor, disable_motors)
            time.sleep(1)
        self.cmd_interface.cmd('power_monitor_voltage', 'scheduled_log')
        if disable_motors: 
            self.enable_all_motors()
        dl_logger.info('Done digitizing')
        if not keep_vna_off:
            dl_logger.info('Enabling VNA output')
            self.cmd_interface.set('na_output_enable', 1) #turns the VNA output back to 1. 
        time.sleep(0.2)


    def start_modemap(self, modemap_notes = ''):
        # TODO throw error if notes isn't a string.
        self.cmd_interface.set('modemap_measurement_status', 'start_measurement')
        # TODO write if statement
        self.cmd_interface.set('modemap_measurement_status_explanation', modemap_notes)

    def stop_modemap(self):
        self.cmd_interface.set('modemap_measurement_status', 'stop_measurement')

    def start_axion_data_taking(self, axion_data_taking_notes = ''):
        # TODO throw error if notes isn't a string.
        self.cmd_interface.set('axion_data_taking_status', 'start_measurement')
        # TODO write if statement
        self.cmd_interface.set('axion_data_taking_status_explanation', axion_data_taking_notes)

    def stop_axion_data_taking(self):
        self.cmd_interface.set('axion_data_taking_status', 'stop_measurement')

    def start_yfactor_measurement(self, yfactor_measurement_notes = ''):
        # TODO throw error if notes isn't a string.
        self.cmd_interface.set('yfactor_measurement_status', 'start_measurement')
        # TODO write if statement
        self.cmd_interface.set('yfactor_measurement_status_explanation', yfactor_measurement_notes)

    def stop_yfactor_measurement(self):
        self.cmd_interface.set('axion_data_taking_status', 'stop_measurement')

    def log_s21(self, sleep_time = 0):
        self.cmd_interface.get('na_s21_iq_data')
        time.sleep(sleep_time)
        self.cmd_interface.cmd('na_s21_iq_data', 'scheduled_log')

    def log_s11(self, sleep_time = 0):
        self.cmd_interface.get('na_s11_iq_data')
        time.sleep(sleep_time)
        self.cmd_interface.cmd('na_s11_iq_data', 'scheduled_log')

    def flmn(self,l, m, n, length,eps_r = 1, r0 = 33):
        ''' Calculates the resonant frequency for TEM 00n mode in an empty Fabry-Perot cavity..
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
        '''
        Keithley power supply that drives Teledyne switches.
        Channel 2 is off, meaning we are on the VNA path.
        Channel 1 is on, meaning we are on the reflection path.
        '''
        dl_logger.info('Switching to reflection path')
        self.cmd_interface.set('switch_ps_select_channel', 'CH2')
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_channel_output', 0)
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_select_channel', 'CH1')
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_channel_output', 1)

    def switch_transmission_path(self):
        '''
        Keithley power supply that drives Teledyne switches.
        Channel 2 is off, meaning we are on the VNA path.
        Channel 1 is off, meaning we are on the transmission path.
        '''
        dl_logger.info('Switching to transmission path')
        self.cmd_interface.set('switch_ps_select_channel', 'CH2')
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_channel_output', 0)
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_select_channel', 'CH1')
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_channel_output', 0)
        time.sleep(0.001)

    def switch_digitization_path(self):
        '''
        Keithley power supply that drives Teledyne switches.
        Channel 2 is on, meaning we are on the VNA path.
        Channel 1 is off to keep the switch cool.
        '''
        dl_logger.info('Switching to digitization path')
        self.cmd_interface.set('switch_ps_select_channel', 'CH1')
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_channel_output', 0)
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_select_channel', 'CH2')
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_channel_output', 1)

    def turn_off_all_switches(self):
        '''
        Keithley power supply that drives Teledyne switches.
        Channel 2 is off, meaning we are on the VNA path.
        Channel 1 is off, meaning that we are on the transmission path.
        '''
        dl_logger.info('Turning off all switches.')
        self.cmd_interface.set('switch_ps_select_channel', 'CH1')
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_channel_output', 0)
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_select_channel', 'CH2')
        time.sleep(0.001)
        self.cmd_interface.set('switch_ps_channel_output', 0)

    def initialize_lo(self, lo_power):
        '''
        Makes sure that the Local Oscillator is on and at the appropriate power.
        '''
        dl_logger.info('Turning on local oscillator.')
        self.cmd_interface.set('lo_power', lo_power)
        self.cmd_interface.set('lo_output_status', 'on')

    def log_switch_settings(self):
        dl_logger.info('Recording switch settings')
        self.cmd_interface.cmd('switch_ps_select_channel', 'scheduled_log')
        self.cmd_interface.cmd('switch_ps_channel_output', 'scheduled_log')

