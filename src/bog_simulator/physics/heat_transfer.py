from bog_simulator.config import THERMAL_CONDUCTIVITY as U
from bog_simulator.config import LANTENT_HEAT as L

def q_rate(U : float, A : float, T_hot : float, T_cold : float) -> float:
    '''Calculates Q inflow'''
    return U * A * (T_hot - T_cold)

def total_mbog(tanks : list) -> float:
    '''Total boil off gas'''
    return sum([tank.m_bog for tank in tanks])

def total_Q_rate(A_submerged, T_coff, T_sea, T_air, ssf, avg_liquid_temp) -> float:
    '''Calculates the tank's heat inflow from air, sea and cofferdam area'''
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
    '''Boil-off Gas rate'''
    return Q_rate/L