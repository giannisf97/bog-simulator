import numpy as np
import pandas as pd

from bog_simulator.physics.heat_transfer import total_mbog

from bog_simulator.config import GAS_CONSTANT as R, MOLECULAR_MASS_CH4 as M

def to_Kelvin(deg_C: type[int | float]) -> type[int | float]:
    '''Convert to Kelvin'''
    return deg_C + 273

def to_degC(K: type[int | float]) -> type[int | float]:
    '''Convert to degrees celcius'''
    return K - 273

def kg_to_m3(density : float, kg : float) -> float:
    '''Converts mass to volume'''
    return kg/density

def boiling_point(press: float, atm: float, boiling_points: pd.DataFrame) -> float:
    '''Returns the boiling temperature of LNG'''
    abs_press = press + atm # absolute pressure [mbar]
    return np.interp(abs_press, boiling_points['mbarA'], boiling_points['Temp[K]'])#LNG temperature (K)

def liquid_level(l_vol: float, vol: pd.Series, gauge: pd.Series) -> float:
    '''Calculates the remaining liquid level of the LNG'''
    return np.interp(l_vol, vol, gauge)/1000 # in meters

def total_vapor_vol(tanks : list) -> float:
    '''Total vapor volume'''
    return sum([tank.vapor_vol for tank in tanks])

def mean_vapor_temp(tanks : list) -> float:
    '''Mean vapor temerature'''
    return np.mean([tank.avg_vapor_temp for tank in tanks])

def vapor_temp(capacity : int, liquid_volume : float, liquid_temp : float) -> float:
    '''Returns the vapor temperature based on the filling ratio (Empirical approach)'''
    level_ratios = [0.02, 0.1, 0.5, 0.8, 0.95, 0.98] # filling ratios
    dTs = [45.0, 35.0, 15.0, 8.0, 4.0, 2.0] # ΔT between vapor and liquid

    current_fr = liquid_volume / capacity #current filling ratio
    current_offset =  np.interp(current_fr, level_ratios, dTs) #current ΔT between liquid temp and vapor

    return liquid_temp + current_offset

def total_dp(tanks, cons, prod, dt):
    '''Calculates the pressure build-up in all the cargo tanks'''
    return ((R * mean_vapor_temp(tanks)) / (total_vapor_vol(tanks) * M)) * (
            total_mbog(tanks) + (cons + prod) / 3600) * dt


def megi_consumption(rpm):
    formula = (0.00441 * pow(rpm, 3) - 0.042 * pow(rpm, 2) +0.95 * rpm) #kg/h
    return formula