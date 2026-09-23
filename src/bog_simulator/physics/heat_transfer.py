"""Heat transfer and boil-off gas (BOG) calculation module.

This module models conductive and convective heat ingress through the cargo tank
containment insulation system from different environmental boundaries (seawater,
ambient air, and adjacent cofferdam bulkheads), scaled by dynamic sloshing effects.
"""

from typing import TYPE_CHECKING

from bog_simulator.config import THERMAL_CONDUCTIVITY as U
from bog_simulator.config import LANTENT_HEAT as L

if TYPE_CHECKING:
    from bog_simulator.core.tank import MembraneTank

def q_rate(U : float, A : float, T_hot : float, T_cold : float) -> float:
    """Calculates steady-state heat inflow rate through a specified boundary surface.

    Based on Fourier's law of heat conduction / Newton's law of cooling:
    Q = U * A * (T_hot - T_cold)

    Args:
        U (float): Overall heat transfer coefficient [W/(m^2*K)].
        A (float): Effective heat transfer surface area [m^2].
        T_hot (float): Ambient boundary temperature (hot source) [K].
        T_cold (float): Cryogenic cargo liquid temperature (cold sink) [K].

    Returns:
        float: Heat transfer rate into the tank [W].
    """
    return U * A * (T_hot - T_cold)

def total_mbog(tanks : list["MembraneTank"]) -> float:
    """Calculates the cumulative boil-off gas (BOG) generation rate across all tanks.

    Args:
        tanks (list): List of MembraneTank model instances.

    Returns:
        float: Total instantaneous boil-off gas mass flow rate [kg/s].
    """
    return sum([tank.m_bog for tank in tanks])

def total_Q_rate(
    A_submerged: dict[str, float],
    T_coff: float,
    T_sea: float,
    T_air: float,
    ssf: float,
    avg_liquid_temp: float,
) -> float:
    """Calculates the tank's total heat ingress rate from sea, air, and cofferdams.

    Integrates heat ingress across all partitioned boundary interfaces (cofferdam,
    sea, and air) and applies the Sloshing Scaling Factor (SSF).

    Args:
        A_submerged (dict): Dictionary of wetted surface areas {"A_coff", "A_sea", "A_air"} [m^2].
        T_coff (float): Cofferdam space temperature [K].
        T_sea (float): Sea surface water temperature [K].
        T_air (float): Ambient atmospheric air temperature [K].
        ssf (float): Sloshing Scaling Factor [-] (amplification due to vessel motion).
        avg_liquid_temp (float): Average liquid LNG temperature [K].

    Returns:
        float: Total effective heat inflow rate into the cargo tank [W].
    """
    Q_coff = q_rate(U["coff"], A_submerged["A_coff"], T_coff, avg_liquid_temp)
    Q_sea = q_rate(U["sea"], A_submerged["A_sea"], T_sea, avg_liquid_temp)
    #if the liquid level is above the water
    if A_submerged["A_air"]:
        Q_air = q_rate(U["air"], A_submerged["A_air"], T_air, avg_liquid_temp)
    else:
        Q_air = 0
    # return the total heat inflow * sloshing specific factor 
    return (Q_coff + Q_air + Q_sea) * ssf

def mbog(Q_rate: float) -> float:
    """Calculates the Boil-off Gas (BOG) evaporation mass rate from heat ingress.

    Derived from the first law of thermodynamics under saturated boiling conditions:
    m_bog = Q_rate / L

    Args:
        Q_rate (float): Total heat ingress rate into the tank [W] (J/s).

    Returns:
        float: Boil-off gas mass flow rate [kg/s].
    """
    return Q_rate/L