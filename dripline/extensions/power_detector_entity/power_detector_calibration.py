import math
import logging
import numpy as np
import os
from scipy.interpolate import interp1d


logger = logging.getLogger(__name__)
file_dir = os.path.abspath(os.path.dirname(__file__))
calibration_dir = file_dir + '/power_monitor_calibrations'

__all__ = []

def _power_from_calibration_file(voltage, calibration_file):
    ''' takes a calibration file and converts voltage to dBm.
    Assumes calibration file has 1st row of voltage and 2nd row of power (dBm).
    Function assumes voltage is a single float value
    '''
    #TODO throw error if resistance is anything but a float.
    M = np.loadtxt(calibration_file, delimiter = ',')
    voltage_cal = M[:,0]
    power_cal = M[:,0]
    interpolated_function = interp1d(voltage_cal, power_cal, kind = 'cubic')
    interpolated_power = float(interpolated_function(voltage)) # interpolation returns an array. Dripline can't handle numpy array. So I cast it to a float.
    return interpolated_power

def zx47_50_cal(voltage):
    '''calibration for zx47-50 power detector'''
    calibration_file = calibration_dir + '/zx4750_calibration.csv'
    interpolated_temperature = _power_from_calibration_file(voltage, calibration_file)
    return interpolated_temperature
__all__.append("zx47_50_cal")


