import math
import logging
import numpy as np
import os
from scipy.interpolate import interp1d


logger = logging.getLogger(__name__)
file_dir = os.path.abspath(os.path.dirname(__file__))
calibration_dir = file_dir + '/temperature_sensor_calibrations'

__all__ = []

def _temp_from_calibration_file(resistance, calibration_file):
    ''' takes a calibration file and converts resistance to temperature.
    Assumes calibration file has 1st row of resistances and 2nd row of temperatures
    Function assumes resistance is a single float value
    '''
    #TODO throw error if resistance is anything but a float.
    M = np.loadtxt(calibration_file, delimiter = ',')
    resistance_cal = M[0,:]
    temperature_cal = M[1,:]
    interpolated_function = interp1d(resistance_cal, temperature_cal, kind = 'cubic')
    interpolated_temperature = float(interpolated_function(abs(resistance))) # interpolation returns an array. Dripline can't handle numpy array. So I cast it to a float.
    return interpolated_temperature

def x83781_cal(resistance):
    '''calibration for cernox'''
    calibration_file = calibration_dir + '/x83781_calibration.txt'
    interpolated_temperature = _temp_from_calibration_file(resistance, calibration_file)
    return interpolated_temperature
__all__.append("x83781_cal")

def x76690_cal(resistance):
    '''calibration for cernox'''
    calibration_file = calibration_dir + '/x76690_calibration.txt'
    interpolated_temperature = _temp_from_calibration_file(resistance, calibration_file)
    return interpolated_temperature
__all__.append("x76690_cal")


def ruox202a_cal(resistance):
    '''calibration for uncalibrated RuOx 202a'''
    calibration_file = calibration_dir + '/ruox202a_calibration.txt'
    interpolated_temperature = _temp_from_calibration_file(resistance, calibration_file)
    return interpolated_temperature
__all__.append("ruox202a_cal")


