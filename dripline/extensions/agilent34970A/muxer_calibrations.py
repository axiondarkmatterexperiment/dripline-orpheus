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
    M = np.loadtxt(calibration_file, delimiter = ',')
    resistance_cal = M[0,:]
    temperature_cal = M[1,:]
    interpolated_function = interp1d(resistance_cal, temperature_cal, kind = 'cubic')
    interpolated_temperature = interpolated_function(resistance)
    return interpolated_temperature

def x83871_cal(resistance):
    '''calibration for cernox'''
    calibration_file = calibration_dir + 'x83871_calibration.txt'
    interpolated_temperature = _temp_from_calibration_file(resistance, calibration_file)
    return interpolated_temperature
__all__.append("x83871_cal")

def ruox202a_cal(resistance):
    '''calibration for cernox'''
    calibration_file = calibration_dir + 'ruox202a_calibration.txt'
    interpolated_temperature = _temp_from_calibration_file(resistance, calibration_file)
    return interpolated_temperature
__all__.append("ruox202a_cal")


