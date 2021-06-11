import math
import logging
import numpy as np


logger = logging.getLogger(__name__)

__all__ = []
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

def x83871_cal(resistance):
    '''calibration for cernox'''
    M = np.loadtxt('temperature_sensor_calibrations/x83781_calibration.txt')
    resistance_cal = M[0,:]
    temperature_cal = M[1,:]
    interpolated_temperature = np.interp(resistance, resistance_cal, temperature_cal)
    return interpolated_temperature

# PT 100
def pt100_cal(resistance):
    '''Calibration for the (many) muxer pt100 temperature sensor endpoints'''
    values_x = [2.29, 9.39, 18.52,  39.72,  60.26,  80.31,   100.,  119.4, 138.51]
    values_y = [20.,   50., 73.15, 123.15, 173.15, 223.15, 273.15, 323.15, 373.15]
    return piecewise_cal(values_x, values_y, resistance)
__all__.append("pt100_cal")

# Cernox sensors
def x84971(resistance):
    '''Calibration for a cernox'''
    values_x = [82.2, 297.0, 3988.0]
    values_y = [305.0, 77.0, 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x84971")

def x76782(resistance):
    '''Calibration for a cernox'''
    values_x = [73.9, 251., 2896.]
    values_y = [305., 77., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x76782")

def x76779p2(resistance):
    '''Calibration for a cernox'''
    values_x = [73.2, 246., 2663.6]
    values_y = [305., 77., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x76779p2")

def x41840(resistance):
    '''Calibration for a cernox'''
    values_x = [58.8, 243., 5104.]
    values_y = [305., 77., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x41840")

def x41849(resistance):
    '''Calibration for a cernox'''
    values_x = [53.4, 215., 4337.]
    values_y = [305., 77., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x41849")

def x43022(resistance):
    '''Calibration for a cernox'''
    values_x = [68.6, 248., 3771.]
    values_y = [300., 78., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x43022")

def x76868(resistance):
    '''Calibration for a cernox'''
    values_x = [44.4499, 107.207, 588.164, 1878.75]
    values_y = [305.0, 77.35, 4.2, 1.29997]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x76868")

def x76774(resistance):
    '''Calibration for a cernox'''
    values_x = [73.2, 246., 2790., 11779.]
    values_y = [305., 77., 4.2, 1.3]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x76774")

def x76775(resistance):
    '''Calibration for a cernox'''
    values_x = [71.9, 239., 2585., 10822.]
    values_y = [305., 77., 4.2, 1.3]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x76775")

def x89346_2wirep2(resistance):
    '''Calibration for a cernox'''
    values_x = [371.03973388672, 765., 848.89422607422, 6110.41015625, 4243.]
    values_y = [293., 70., 35., 5.5, 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x89346_2wirep2")

def x89346_2wirep3(resistance):
    '''Calibration for a cernox'''
    values_x = [7834. , 492., 157.]
    values_y = [4.2, 77., 305.]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x89346_2wirep3")

def x89346(resistance): 
    '''Calibration for a cernox'''
    values_x= [7783., 441., 106.]
    values_y= [4.2, 77., 305.]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x89346")

def x84174(resistance):
    '''Calibration for a cernox'''
    values_x = [60.8, 187., 1607.]
    values_y = [305., 77., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x84174")

def x84138(resistance):
    '''Calibration for a cernox'''
    values_x = [77.9, 250., 2401.]
    values_y = [305., 77., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x84138")

def x87830(resistance):
    '''Calibration for a cernox'''
    values_x = [70.6, 225., 1870.]
    values_y = [305., 77., 4.2]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("x87830")

# RuOx sensors
def RuOx202a(resistance):
    '''Calibration for a RuOx'''
    values_x = [2008.5, 2130, 2243.1507919, 2247.82837008, 2252.67165521, 2257.69242943, 2262.90261077, 2268.31490773, 2273.94481798, 2279.80870753, 2285.92402049, 2292.31202231, 2298.99521874, 2305.99750346, 2313.34748079, 2321.07638638, 2329.22021822, 2337.81827044, 2346.91683612, 2356.56678496, 2366.82825705, 2377.76798468, 2389.46691367, 2395.62834041, 2402.01464403, 2408.63984847, 2415.51928432, 2422.6692313, 2430.10802159, 2437.85528088, 2445.93319361, 2454.36562977, 2463.17990092, 2472.40561454, 2482.07710006, 2492.23190591, 2502.91428312, 2514.17316164, 2526.06736559, 2538.66273378, 2552.04016269, 2566.29150584, 2581.5329411, 2597.89797142, 2615.55883889, 2634.71721236, 2655.64428995, 2678.65722169, 2704.16570341, 2732.66352706, 2764.84669842, 2778.92266862, 2793.7502015, 2801.4579521, 2809.36832643, 2825.86689284, 2843.52852376, 2862.62685027, 2883.18617288, 2905.22478212, 2928.99838467, 2954.81636122, 2968.5757862, 2982.95670854, 2998.00687716, 3013.77849689, 3030.32760197, 3047.71832163, 3066.02023264, 3085.31287362, 3105.68291885, 3127.23059199, 3150.06590596, 3174.31753284, 3200.12792484, 3227.66616756, 3257.12144397, 3288.72235472, 3322.72790766, 3359.45759811, 3399.27876097, 3442.65523479, 3490.12848945, 3542.39690771, 3600.2885489, 3664.89413383, 3737.51755467, 3819.87129619, 3914.02777317, 4022.75310485, 4083.59510837, 4149.45062312, 4220.96353588, 4298.96074351, 4384.44214969, 4478.77921405, 4583.74002105, 4701.99100529, 4836.59753612, 4990.611791, 5166.85835176, 5369.38032441, 5611.83504012, 5903.84561811, 6038.02877119, 6184.22615218, 6344.068314, 6519.43869339, 6712.75769848, 6926.90774683, 7165.50302782, 7432.9462211, 7735.1128401, 8079.35355643, 8270.27720363, 8475.69626238, 8697.52271613, 8937.92669063, 9199.42217175, 9485.27250376, 9799.25139812, 10145.8475355, 10531.1357652, 10962.3265779, 11448.087719, 11999.9339566, 12632.1906056, 13363.5119791, 14217.3470276, 15224.3774852, 16425.034128, 17877.7531888, 19665.2816715, 21927.1350297, 23308.1186795, 24920.4604245, 26839.0366817, 29185.9753819, 32137.3219905, 35958.554143, 40977.9945386, 47523.915336, 56177.874649, 69191.1003872]
    values_y = [305.0, 77.0, 40.0, 39.0, 38.0, 37.0, 36.0, 35.0, 34.0, 33.0, 32.0, 31.0, 30.0, 29.0, 28.0, 27.0, 26.0, 25.0, 24.0, 23.0, 22.0, 21.0, 20.0, 19.5, 19.0, 18.5, 18.0, 17.5, 17.0, 16.5, 16.0, 15.5, 15.0, 14.5, 14.0, 13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.8, 5.6, 5.5, 5.4, 5.2, 5.0, 4.8, 4.6, 4.4, 4.2, 4.0, 3.9, 3.8, 3.7, 3.6, 3.5, 3.4, 3.3, 3.2, 3.1, 3.0, 2.9, 2.8, 2.7, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.15, 1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.48, 0.46, 0.44, 0.42, 0.4, 0.38, 0.36, 0.34, 0.32, 0.3, 0.29, 0.28, 0.27, 0.26, 0.25, 0.24, 0.23, 0.22, 0.21, 0.2, 0.19, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11, 0.1, 0.095, 0.09, 0.085, 0.08, 0.075, 0.07, 0.065, 0.06, 0.055, 0.05]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("RuOx202a")

def RuOx102a2(resistance):
    '''Calibration for a RuOx'''
    values_x = [1001.457, 1049.084821, 1050.134248, 1051.234436, 1052.390136, 1053.606421, 1054.888644, 1056.243185, 1057.676999, 1059.198157, 1060.815407, 1062.539058, 1064.38032, 1066.352388, 1068.469693, 1070.749315, 1073.209983, 1075.873923, 1078.765815, 1081.915923, 1085.357865, 1089.133117, 1091.160926, 1093.291746, 1095.533606, 1097.895843, 1100.388624, 1103.023917, 1105.814816, 1108.77684, 1111.927001, 1115.285453, 1118.874253, 1122.719262, 1126.848597, 1131.294538, 1136.091908, 1141.279985, 1146.901466, 1153.006101, 1159.651242, 1166.914569, 1174.892047, 1183.729192, 1193.602217, 1204.749899, 1217.387866, 1231.550801, 1247.555875, 1266.577909, 1275.009829, 1283.981548, 1293.598717, 1303.938409, 1315.072734, 1327.083484, 1340.082629, 1354.198663, 1369.584452, 1386.413226, 1395.434894, 1404.902528, 1414.850356, 1425.317761, 1436.34781, 1447.990209, 1460.299587, 1473.339586, 1487.180513, 1501.904756, 1517.603674, 1534.384654, 1552.367053, 1571.690996, 1592.512433, 1615.01362, 1639.39797, 1665.903196, 1694.797923, 1726.404524, 1761.101101, 1799.379277, 1841.854094, 1889.421115, 1943.25369, 2005.176674, 2077.479961, 2162.932548, 2211.300018, 2263.645311, 2320.08459, 2380.766505, 2446.939292, 2523.006605, 2609.096455, 2704.598442, 2812.424605, 2936.56535, 3080.725123, 3250.526173, 3453.501016, 3700.518459, 3815.025036, 3940.325984, 4078.034019, 4230.017884, 4398.490695, 4586.345291, 4797.016459, 5034.682083, 5304.975959, 5615.030288, 5787.871933, 5974.483538, 6176.700265, 6396.627086, 6636.72171, 6900.156905, 7190.651688, 7512.681341, 7872.352068, 8277.055764, 8735.858457, 9261.107013, 9868.5957, 10579.59141, 11421.60916, 12431.61257, 13658.21729, 15165.46324, 17039.12911, 19400.46809, 20820.34136, 22443.68027, 24330.67681, 26563.61824, 29253.30998, 32601.28279, 37123.89615, 43515.77963, 52106.70612, 63765.09333]
    values_y = [290.0, 40.0, 39.0, 38.0, 37.0, 36.0, 35.0, 34.0, 33.0, 32.0, 31.0, 30.0, 29.0, 28.0, 27.0, 26.0, 25.0, 24.0, 23.0, 22.0, 21.0, 20.0, 19.5, 19.0, 18.5, 18.0, 17.5, 17.0, 16.5, 16.0, 15.5, 15.0, 14.5, 14.0, 13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.8, 5.6, 5.4, 5.2, 5.0, 4.8, 4.6, 4.4, 4.2, 4.0, 3.9, 3.8, 3.7, 3.6, 3.5, 3.4, 3.3, 3.2, 3.1, 3.0, 2.9, 2.8, 2.7, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.15, 1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.48, 0.46, 0.44, 0.42, 0.4, 0.38, 0.36, 0.34, 0.32, 0.3, 0.29, 0.28, 0.27, 0.26, 0.25, 0.24, 0.23, 0.22, 0.21, 0.2, 0.19, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11, 0.1, 0.095, 0.09, 0.085, 0.08, 0.075, 0.07, 0.065, 0.06, 0.055, 0.05]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("RuOx102a2")

# Magnet Temps
def magnet_t1p2(resistance):
    '''Calibration for a cernox'''
    values_x = [4.2, 50., 150.]
    values_y = [1755.75, 261.892, 72.4254]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("magnet_t1p2")

def magnet_t2p2(resistance):
    '''Calibration for a cernox'''
    values_x = [4.2, 50., 150.]
    values_y = [1346.27, 240.923, 62.171]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("magnet_t2p2")

def magnet_t3p2(resistance):
    '''Calibration for a cernox'''
    values_x = [4.21, 50., 150.]
    values_y = [1495., 225.333, 62.59]
    return piecewise_cal(values_x, values_y, abs(resistance), log_x=True, log_y=True)
__all__.append("magnet_t3p2")

# other pressures
def capacitance_manometer_10_offset(volts):
    ''' little pot pressure '''
    values_x = [0., 10., 15., 20.]
    values_y = [-0.16, 9.84, 14.84, 14.84]
    return piecewise_cal(values_x, values_y, volts)
__all__.append("capacitance_manometer_10_offset")

def capacitance_manometer_10(volts):
    ''' little pot pressure '''
    values_x = [0., 10., 15., 20.]
    values_y = [0., 10., 15., 15.]
    return piecewise_cal(values_x, values_y, volts)
__all__.append("capacitance_manometer_10")

def gp358i(volts):
    ''' insulation pressure ion '''
    values_x = [0., 10.]
    values_y = [1e-11, 0.1]
    return piecewise_cal(values_x, values_y, volts, log_y=True)
__all__.append("gp358i")

def gp358c(volts):
    ''' insulation pressure ion '''
    values_x = [0., 7.]
    values_y = [0.0001, 1000.]
    return piecewise_cal(values_x, values_y, volts, log_y=True)
__all__.append("gp358c")

def super_bee(volts):
    ''' insulation pressure ion '''
    values_x = [1., 1.301, 1.699, 2., 2.301, 2.699, 3., 3.301, 3.699, 4., 4.301, 4.699, 5., 5.301, 5.699, 6., 6.301, 6.699, 7., 7.301, 7.477, 7.602, 7.699, 7.778, 7.845, 7.881, 7.903, 7.954, 8.]
    values_y = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1., 2., 5., 10., 20., 50., 100., 200., 300., 400., 500., 600., 700., 760., 800., 900., 1000.]
    return piecewise_cal(values_x, values_y, volts, log_y=True)
__all__.append("super_bee")

# Hall Probe
def HGCA3020(resistance):
    '''Calibration for a Hall Probe'''
    values_x = [-0.02895958, -0.01930098, -0.00964152, 0., 0.00963079, 0.01929507, 0.02898745]
    values_y = [-30., -20., -10., 0., 10., 20., 30]
    return piecewise_cal(values_x, values_y, resistance)
__all__.append("HGCA3020")

def HGCT3020(resistance):
    '''Calibration for a Hall Probe'''
    values_x = [-0.02613, -0.01744, -0.0087197, 0., 0.00873, 0.017463, 0.02617]
    values_y = [-30., -20., -10., 0., 10., 20., 30]
    return piecewise_cal(values_x, values_y, resistance)
__all__.append("HGCT3020")

# Flow Meters
def flow_meter_1k_pot(volts):
    '''Calibration for a 1k pot flow meter'''
    values_x = [0.0, 2.5, 5.0]
    values_y = [0.0, 1.811, 3.622]
    return piecewise_cal(values_x, values_y, volts)
__all__.append("flow_meter_1k_pot")

def flow_meter_main_magnet(volts):
    '''Calibration for a 1k pot flow meter'''
    values_x = [0.0, 2.5, 5.0]
    values_y = [0.0, 18.11, 36.22]
    return piecewise_cal(values_x, values_y, volts)
__all__.append("flow_meter_main_magnet")

def flow_meter_insert(volts):
    '''Calibration for a 1k pot flow meter'''
    values_x = [0.0, 2.5, 5.0]
    values_y = [0.0, 9.055, 18.11]
    return piecewise_cal(values_x, values_y, volts)
__all__.append("flow_meter_insert")
