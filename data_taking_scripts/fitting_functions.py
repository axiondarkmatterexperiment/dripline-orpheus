import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
from scipy.constants import constants
from scipy.interpolate import interp1d

def unpack_iq_data(data):
    ''' Input - [re,im,re,im,...]
        Output - [sqrt(re^2+im^2),sqrt(re^2+im^2),...]
        Takes in iq_data and returns the magnitude of the data'''
    unpacked_data = [data[i]**2+ data[i+1]**2 for i in range(0,len(data)-1,2)]
    return np.array(unpacked_data)

def estimate_uncertainty(data):
    return 2*np.sqrt(data)

def find_nearest_ind(array, value):
    '''Takes in an array and finds the index of a specific value'''
    ind = (np.abs(array-value)).argmin()
    return ind

def f0_guess(data, freq, measurement_type):
    ''' Data and freq are arrays. Freq in Hz is recommended for consistency
        Resonator_length is a number in cm.
        Measurement type should be "transmission" or "reflection". 
        TODO: Ask Raphael about how index_f0 is calculated
        '''
    if measurement_type == 'transmission':
        index_f0 = find_nearest_ind(data, np.max(data))
    else:
        index_f0 = find_nearest_ind(data, np.min(data))
    return freq[index_f0]

def offset_guess(data,measurement_type, filter_percentage = (1/3)):
    ''' Data should be the magnitude of s21/s11 data.
        Guesses normalization for measurement fit'''
    if measurement_type == 'transmission':
        data_filtered = stats.trim1(data,filter_percentage, tail='right')
    elif measurement_type == 'reflection':
        data_filtered = stats.trim1(data, filter_percentage, tail = 'left')
    else:
        raise Exception("not a valid measurement type")
    return np.median(data_filtered)

def dy_guess(data, measurement_type):
    if measurement_type == 'transmission':
        depth = np.max(data)- offset_guess(data, measurement_type)
    elif measurement_type == 'reflection':
        depth = offset_guess(data, measurement_type)- np.min(data)
    else:
        raise Exception("not a valid measurement type")
    return depth

def q_guess(data, freq, measurement_type):
    ''' Data and freq are arrays.
    TODO: Ask Raphael about the way index_f0 is calculated
    '''
    if measurement_type == 'transmission':
        index_f0 = find_nearest_ind(data, np.max(data))
    else:
        index_f0 = find_nearest_ind(data, np.min(data))
    f0 = freq[index_f0]
    dy = dy_guess(data, measurement_type)
    offset = offset_guess(data, measurement_type)
    left_data = data[:index_f0]
    if measurement_type == "reflection":
        index_fwhm = find_nearest_ind(left_data, offset-dy/2)
    elif measurement_type=="transmission":
        index_fwhm = find_nearest_ind(left_data, offset+dy/2)
    else:
        raise Exception("not a valid measurement type")
    # find distance between fwhm and resonance
    f_left = freq[index_fwhm]
    # guess bandwidth as twice that distance
    delta_f = 2*(f0-f_left)
    q_guess = f0/delta_f
    return q_guess

def guess_parameters(data, freq, measurement_type):
    f0 = f0_guess(data, freq, measurement_type)
    offset = offset_guess(data, measurement_type)
    dy = dy_guess(data, measurement_type)
    q = q_guess(data, freq, measurement_type)
    return f0,q, dy, offset

def func_pow_transmitted(f, fo, Q, del_y, C):
    return (fo/(2*Q))**2*del_y/((f-fo)**2+(fo/(2*Q))**2)+C

def func_pow_reflected(f, fo, Q, del_y, C):
    return -(fo/(2*Q))**2*del_y/((f-fo)**2+(fo/(2*Q))**2)+C

def data_lorentzian_fit(data, freq, measurement_type):
    ''' Uses the scipy curve_fit to perform a lorentzian fit on
        reflection or transmission data.
        Resonator_length is a number in cm.
        Peak_search_width is like span but the calculated/predicted frequency is not always
        accurate and might have small shifts.
        Guesses parameters based on input parameters.
        Returns popt which is the calculated parameters given the initial conditions.'''
    p0_guess = guess_parameters(data, freq, measurement_type)
    data_uncertainty = estimate_uncertainty(data)
    if measurement_type == 'transmission':
        popt, pcov = curve_fit(func_pow_transmitted, freq, data, p0_guess, data_uncertainty)
    else:
        popt, pcov = curve_fit(func_pow_reflected, freq, data, p0_guess, data_uncertainty)
    return popt, pcov

def get_arr_ends(x, n_end_elements):
    """returns the first and last n_end_elements of array x"""
    return np.concatenate([x[:n_end_elements], x[-n_end_elements:]])

def reflection_deconvolve_line(f, Gamma_mag, Gamma_phase, C_fit):
    '''From the overall measured reflection coefficient, this method calculated the reflection coefficient Gamma off of the resonator by deconvolving the line path'''
    Gamma_cav_mag = Gamma_mag*np.sqrt(1/C_fit)

    interp_phase = interp1d(f, Gamma_phase, kind='cubic')
    # assume that the phase change due to the transmission line is linear
    f_ends = get_arr_ends(f, 5)
    phase_ends = get_arr_ends(Gamma_phase, 5)
    interp_phase_wo_notch = np.poly1d(np.polyfit(f_ends, phase_ends, 1))
    delay_phase = interp_phase_wo_notch(f)
    # calculate the phase change due to the cavity by subtracting the phase change due to the transmission line.
    Gamma_cav_phase = interp_phase(f) - delay_phase

    return Gamma_cav_mag, Gamma_cav_phase


def deconvolve_phase(freq, measured_reflected_phase):
    '''Removes the effects of the transmission line on the measured phase'''
    # assume that the phase change due to the transmission line is linear
    f_ends = get_arr_ends(freq, 5)
    phase_ends = get_arr_ends(measured_reflected_phase, 5)
    interp_phase_wo_notch = np.poly1d(np.polyfit(f_ends, phase_ends, 1))
    delay_phase = interp_phase_wo_notch(freq)
    # calculate the phase change due to the cavity by subtracting the phase change due to the transmission line.
    deconvolved_phase = measured_reflected_phase - delay_phase
    return deconvolved_phase

#def calculate_coupling(mag_fo, phase_fo):
#    """Calculate coupling to a cavity after reflection fit is done"""
#    # TODO add error propogation
#    sgn = np.sign(phase_fo-np.pi) ## phase_fo has range of [-pi,pi]
#    beta = (1+sgn*mag_fo)/(1-sgn*mag_fo)
#    return beta

def determine_if_undercoupled(s11_phase):
    '''Assumes the largest derivative in phase occurs on resonance. 
    If the derivative is positive on resonance, then it it undercoupled.
    If the derivative is negative on resonance, then it is overcoupled 
    Returns 1 if undercoupled. Else returns 0.
    '''
    f0_derivative = np.max(np.gradient(s11_phase))
    return f0_derivative > 0

def calculate_coupling(dy_over_C, s11_phase):
    '''
    Takes the Lorentzian dip normalized to the s11 background to calculate the coupling coefficient.
    '''
    if dy_over_C > 1: return 1
    Gamma_cav_f0 = np.sqrt(1-dy_over_C)
    if determine_if_undercoupled(s11_phase):
        beta = (1 - Gamma_cav_f0)/(1+Gamma_cav_f0)
    else:
        beta = (1 + Gamma_cav_f0)/(1-Gamma_cav_f0)
    return beta
