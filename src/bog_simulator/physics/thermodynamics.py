"""Thermodynamics and vapor pressure dynamics module.

This module provides functions for thermodynamic unit conversions, boiling point
determination from methane saturation curves, vapor temperature stratification,
cargo tank vapor header pressure dynamics via the ideal gas law, and empirical
fuel gas consumption models for main engines and generators.
"""

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from bog_simulator.physics.heat_transfer import total_mbog

from bog_simulator.config import GAS_CONSTANT as R, MOLECULAR_MASS_CH4 as M

if TYPE_CHECKING:
    from bog_simulator.core.tank import MembraneTank

def to_Kelvin(deg_C: float | int) -> float:
    """Converts temperature from degrees Celsius to Kelvin.

    Args:
        deg_C (int | float): Temperature in degrees Celsius [°C].

    Returns:
        int | float: Temperature in Kelvin [K].
    """
    return deg_C + 273

def to_degC(K: float | int) -> float:
    """Converts temperature from Kelvin to degrees Celsius.

    Args:
        K (int | float): Temperature in Kelvin [K].

    Returns:
        int | float: Temperature in degrees Celsius [°C].
    """
    return K - 273

def kg_to_m3(density : float, kg : float) -> float:
    """Converts mass to volume using liquid density.

    Args:
        density (float): Liquid density [kg/m^3].
        kg (float): Mass [kg].

    Returns:
        float: Volume [m^3].
    """
    return kg/density

def boiling_point(press: float, atm: float, boiling_points: pd.DataFrame) -> float:
    """Determines the boiling temperature of LNG based on absolute tank pressure.

    Performs 1D linear interpolation along the pure methane saturation curve (P_sat vs T_boil).

    Args:
        press (float): Gauge pressure inside the cargo tank [mbar].
        atm (float): Ambient atmospheric pressure [mbar].
        boiling_points (pd.DataFrame): DataFrame containing 'mbarA' (absolute pressure)
            and corresponding 'Temp[K]' columns.

    Returns:
        float: Saturated boiling temperature of the liquid cargo [K].
    """
    abs_press = press + atm # absolute pressure [mbar]
    return np.interp(abs_press, boiling_points['mbarA'], boiling_points['Temp[K]'])#LNG temperature (K)

def liquid_level(l_vol: float, vol: pd.Series, gauge: pd.Series) -> float:
    """Calculates cargo liquid sounding/gauge height from calibration tables.

    Interpolates current liquid volume against the tank's certified calibration table.

    Args:
        l_vol (float): Current liquid volume in the tank [m^3].
        vol (pd.Series): Calibrated volume points [m^3].
        gauge (pd.Series): Corresponding gauge sounding measurements [mm].

    Returns:
        float: Liquid level sounding height [m].
    """
    return np.interp(l_vol, vol, gauge)/1000 # in meters

def total_vapor_vol(tanks: list["MembraneTank"]) -> float:
    """Calculates cumulative vapor space volume across all cargo tanks.

    Args:
        tanks (list): List of MembraneTank model instances.

    Returns:
        float: Total vapor volume [m^3].
    """
    return sum([tank.vapor_vol for tank in tanks])

def mean_vapor_temp(tanks: list["MembraneTank"]) -> float:
    """Calculates the volume/tank-averaged vapor phase temperature.

    Args:
        tanks (list): List of MembraneTank model instances.

    Returns:
        float: Mean vapor temperature [K].
    """
    return float(np.mean([tank.avg_vapor_temp for tank in tanks]))

def vapor_temp(capacity: int | float, liquid_volume: float, liquid_temp: float) -> float:
    """Estimates the vapor space temperature based on filling ratio stratification.

    Empirical approach capturing thermal stratification in the ullage space:
    Lower filling ratios (e.g., ballast heel) lead to wider delta-T offsets between
    warm vapor near the deck and cold cryogenic liquid, whereas high filling ratios
    (laden voyage) bring vapor temperature close to liquid boiling temperature.

    Args:
        capacity (int | float): Total volumetric capacity of the tank [m^3].
        liquid_volume (float): Current volume of liquid LNG [m^3].
        liquid_temp (float): Current liquid boiling temperature [K].

    Returns:
        float: Average vapor space temperature [K].
    """
    level_ratios = [0.02, 0.1, 0.5, 0.8, 0.95, 0.98] # filling ratios
    dTs = [45.0, 35.0, 15.0, 8.0, 4.0, 2.0] # ΔT between vapor and liquid

    current_fr = liquid_volume / capacity #current filling ratio
    current_offset = float(np.interp(current_fr, level_ratios, dTs)) #current ΔT between liquid temp and vapor

    return liquid_temp + current_offset

def total_dp(tanks: list["MembraneTank"], cons: float, prod: float, dt: int | float) -> float:
    """Calculates pressure build-up / drop in the vapor header across all tanks.

    Derived from differentiating the ideal gas equation (P * V = (m / M) * R * T)
    over time interval dt under net mass balance (BOG generated + produced - consumed):
    dP = (R * T_vapor / (V_vapor * M)) * (m_bog + prod - cons) * dt

    Args:
        tanks (list): List of MembraneTank model instances.
        cons (float): Total instantaneous fuel gas consumption rate [kg/s].
        prod (float): Additional gas production/injection rate [kg/s].
        dt (int | float): Time step duration [s].

    Returns:
        float: Net pressure change in the vapor space [Pa].
    """
    return ((R * mean_vapor_temp(tanks)) / (total_vapor_vol(tanks) * M)) * (
            total_mbog(tanks) + prod - cons) * dt


def megi_consumption(rpm: float | int) -> float:
    """Calculates fuel gas consumption of a MAN B&W ME-GI two-stroke main engine.

    Uses a 3rd-order polynomial regression derived from manufacturer testbed data:
    m_gas = 0.00441 * rpm^3 - 0.042 * rpm^2 + 0.95 * rpm [kg/h]

    Args:
        rpm (float | int): Engine shaft rotational speed [RPM] (valid: 45 - 73 RPM).

    Returns:
        float: Fuel gas consumption mass rate [kg/h].
    """
    formula = 0.00441 * pow(rpm, 3) - 0.042 * pow(rpm, 2) + 0.95 * rpm #kg/h
    return float(formula)

def dfde_consumption(type: str, output: float | int) -> float:
    """Calculates fuel gas consumption of Wärtsilä DFDE auxiliary generator sets.

    Uses empirical quadratic performance curves for W6L34DF and W8L34DF models:
    - W6L34DF: m_gas = 1.35e-5 * P^2 + 0.0885 * P + 99.2 [kg/h]
    - W8L34DF: m_gas = 1.01e-5 * P^2 + 0.0885 * P + 132.3 [kg/h]

    Args:
        type (str): Generator engine model ('W6L34DF' or 'W8L34DF').
        output (float | int): Generator electrical power output [kW].

    Returns:
        float: Fuel gas consumption mass rate [kg/h].
    """
    formula: float = 0.0
    if type == 'W6L34DF':
        formula = 1.35e-5 * pow(output, 2) + 0.0885 * output + 99.2 # kg/h
    elif type == 'W8L34DF':
        formula = 1.01e-5 * pow(output, 2) + 0.0885 * output + 132.3 # kg/h

    return formula