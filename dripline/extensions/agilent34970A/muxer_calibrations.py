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

#I just copied this from /source/admx_muxer_cals.py in the dragonfly-extended repo. I bought an uncalibrated cernox, not realizing that they expect you to calibrate it yourself.
# But they did ship me a piece of paper with measured values at LHe, LN and room temps, and for the main experiment it seems like using this function with
# only these three data points is enough to calibrate the sensor... Leads_box_temp is an example of a sensor that uses this with only three data points.
def piecewise_cal(values_x, values_y, this_x, log_x=False, log_y=False):
    if log_x:
        logger.debug("doing log x cal")
        values_x = [math.log(x) for x in values_x]
        this_x = math.log(this_x)
    if log_y:
        logger.debug("doing log y cal")
        values_y = [math.log(y) for y in values_y]
    try:
        high_index = [i>this_x for i in values_x].index(True)
    except ValueError:
        high_index = -1
        logger.warning("raw value is above the calibration range, extrapolating")
        #raise dripline.core.DriplineValueError("raw value is likely above calibration range")
    if high_index == 0:
        high_index = 1
        logger.warning("raw value is below the calibration range, extrapolating")
        #raise dripline.core.DriplineValueError("raw value is below calibration range")
    m = (values_y[high_index] - values_y[high_index - 1]) / (values_x[high_index] - values_x[high_index - 1])
    to_return = values_y[high_index - 1] + m * (this_x - values_x[high_index - 1])
    if log_y:
        to_return = math.exp(to_return)
    return to_return


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

def pt100_cal(resistance):
    '''calibration for uncalibrated pt100'''
    calibration_file = calibration_dir + '/pt100_calibration.txt'
    interpolated_temperature = _temp_from_calibration_file(resistance, calibration_file)
    return interpolated_temperature
__all__.append("pt100_cal")

def x201099(resistance):
    '''Calibration for a cernox CX-1050-SD-HT'''
    values_x = [75., 248., 2984.]
    values_y = [295., 77., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append(x201099)


