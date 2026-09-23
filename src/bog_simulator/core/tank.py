"""Membrane cargo tank model module.

Defines the MembraneTank class, representing an individual LNG membrane containment tank
with specific geometry, level sounding calibration, thermodynamic state, and BOG production.
"""

from typing import Any
import pandas as pd

import bog_simulator.core.environment as env
from bog_simulator.utils import data_loader
from bog_simulator.physics import thermodynamics as th , hydrodynamics as hyd, heat_transfer as ht
from bog_simulator.config import DENSITY_LNG as D

class MembraneTank:
    """Represents an individual GTT-type membrane LNG cargo tank.

    Models geometric dimensions, wetted surface partitions, filling ratio, liquid level
    from sounding tables, boiling point at saturated tank pressure, heat inflow rates,
    and instantaneous boil-off gas (BOG) mass evaporation.

    Attributes:
        tank_num (int): Identification number of the cargo tank (1 to 4).
        tank_geometry (dict): Dimensions including height, breadth, length, h1, and h2.
        tables (pd.DataFrame): Calibration/sounding table mapping gauge height to volume.
        boiling_df (pd.DataFrame): Methane saturation pressure vs. boiling temperature data.
        tank_capacity (float): Total volumetric capacity of the tank [m^3].
        avg_vapor_temp (float): Average vapor phase temperature [K].
        liquid_vol (float): Instantaneous volume of liquid LNG cargo [m^3].
        vapor_vol (float): Instantaneous ullage space vapor volume [m^3].
        P_tank (float): Internal gauge pressure of the tank [mbar].
        avg_liquid_temp (float): Boiling temperature of the liquid cargo [K].
        liquid_level (float): Liquid sounding height measured from tank bottom [m].
        A_submerged (dict): Submerged surface areas contacting cofferdams, sea, and air [m^2].
        Q_rate (float): Instantaneous heat ingress rate into the tank [W].
        m_bog (float): Instantaneous Boil-Off Gas production rate [kg/s].
        access_tank (bool): True if cargo remains in the tank; False if depleted.
    """
    tank_num: int
    tank_geometry: dict[str, float]
    tables: pd.DataFrame
    boiling_df: pd.DataFrame
    tank_capacity: float
    avg_vapor_temp: float
    liquid_vol: float
    vapor_vol: float
    P_tank: float
    avg_liquid_temp: float
    liquid_level: float
    A_submerged: dict[str, float]
    Q_rate: float
    m_bog: float
    access_tank: bool

    def __init__(self, tank_params: dict[str, Any], enviroment: env.Environment) -> None:
        """Initializes a MembraneTank instance with configuration and environmental conditions.

        Args:
            tank_params (dict): Parameter dictionary defining geometry, initial volume,
                pressure, and temperature for this tank.
            enviroment (env.Environment): Environmental model providing draft, ambient
                temperatures, atmospheric pressure, and sloshing factor.
        """
        #---Variables---
        self.tank_num = tank_params["Number"] # Number of the tank
        self.tank_geometry = tank_params["Geometry"] # Geometrical properties of the tank
        self.tables = data_loader.load_calibration_table(self.tank_num) #calibration table of the tank for finding the liquid level
        self.boiling_df = data_loader.load_boiling_points()
        self.tank_capacity = tank_params["Tank_Capacity"] #Total capacity of the tank (m3)
        self.avg_vapor_temp = th.to_Kelvin(tank_params["Avg_Vapor_Temperature"]) # Average Vapor temperature (K)
        self.liquid_vol =tank_params["Liquid_Volume"] #Liquid volume inside the cargo tank (m3)
        self.vapor_vol = (self.tank_capacity - self.liquid_vol) #Remaining vapor volume (m3)
        self.P_tank = tank_params["Tank_Pressure"] #Tank pressure (mbar)
        self.avg_liquid_temp = th.boiling_point(self.P_tank, enviroment.atm, self.boiling_df)#LNG temperature (K)
        self.liquid_level = th.liquid_level(self.liquid_vol, self.tables['Volume[m3]'], self.tables['Gauge[mm]']) #Liquid level to be calculated by the callibration tables (m)
        self.A_submerged = hyd.submerged_area(self.liquid_level, enviroment.draft, self.tank_geometry) #LNG submerged area of the tank coming in contact with enviroment (m2)
        
        #---Calculated---
        self.Q_rate = ht.total_Q_rate(self.A_submerged, 
                                      enviroment.T_coff, 
                                      enviroment.T_sea, 
                                      enviroment.T_air, 
                                      enviroment.ssf, 
                                      self.avg_liquid_temp) #Heat inflow [W]
        self.m_bog = ht.mbog(self.Q_rate) #Boil-of gas production [kg/s]

        self.access_tank = self.liquid_vol >=0
     
    def update_parameters(self, enviroment: env.Environment, dt: int) -> None:
        """Updates the thermodynamic and physical state of the cargo tank over dt seconds.

        Deducts evaporated liquid volume, recalibrates liquid level, updates submerged
        contact areas, re-evaluates saturated boiling and vapor temperatures, and
        computes the updated heat ingress and BOG evaporation rates.

        Args:
            enviroment (env.Environment): Current environmental conditions.
            dt (int): Time increment in seconds.

        Returns:
            None
        """
        self.liquid_vol = self.liquid_vol - th.kg_to_m3(D, self.m_bog * dt)
        #if lng on a certain tank finished
        if self.liquid_vol < 0:
            #set volume 0
            self.liquid_vol = 0
            #and lock the tank
            self.access_tank = False

        self.vapor_vol = self.tank_capacity - self.liquid_vol
        self.liquid_level = th.liquid_level(self.liquid_vol, self.tables['Volume[m3]'], self.tables['Gauge[mm]'])
        self.A_submerged = hyd.submerged_area(self.liquid_level, enviroment.draft, self.tank_geometry)
        self.avg_liquid_temp = th.boiling_point(self.P_tank, enviroment.atm, self.boiling_df)
        self.avg_vapor_temp = th.vapor_temp(self.tank_capacity, self.liquid_vol, self.avg_liquid_temp)

        self.Q_rate = ht.total_Q_rate(self.A_submerged, 
                                        enviroment.T_coff, 
                                        enviroment.T_sea, 
                                        enviroment.T_air, 
                                        enviroment.ssf, 
                                        self.avg_liquid_temp) #Heat inflow [W]
        self.m_bog = ht.mbog(self.Q_rate) #kg/s

    def update(self, dt: int, enviroment: env.Environment) -> None:
        """Refreshes the tank parameters if the tank still contains cargo.

        Args:
            dt (int): Time increment in seconds.
            enviroment (env.Environment): Environmental model instance.
        """
        if self.access_tank:
            self.update_parameters(enviroment, dt)