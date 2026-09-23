"""Voyage environmental conditions module.

Simulates environmental and meteorological conditions along the vessel's voyage track,
updating ambient air/sea temperatures, barometric pressure, and sea states at each time step.
"""

from typing import Any

import pandas as pd
from bog_simulator.physics.thermodynamics import to_Kelvin
from bog_simulator.physics.hydrodynamics import ssf

class Environment:
    """Simulates the environmental conditions of a given voyage track.

    Reads time-series weather and oceanographic data, converting temperatures to Kelvin,
    extracting atmospheric pressure and sea state, and determining the Sloshing Scaling Factor.

    Attributes:
        ic (int): Class-level step counter tracking the current row in the weather dataset.
        df (pd.DataFrame): Time-series DataFrame of environmental data.
        vessel_data (dict): Static vessel configuration dictionary.
        end (bool): Flag indicating if the end of the voyage dataset has been reached.
        date (str): Current timestamp of the voyage.
        sea_state (int): Wind force / Beaufort number (BN).
        voyage (str): Voyage condition ('L' for Laden, 'B' for Ballast).
        T_air (float): Ambient air temperature [K].
        T_sea (float): Sea surface water temperature [K].
        T_coff (float): Cofferdam space temperature [K].
        atm (float): Mean sea level atmospheric pressure [mbar].
        draft (float): Vessel draft [m].
        ssf (float): Current Sloshing Scaling Factor.
    """
    ic: int = 0 #internal counter refers to the days
    
    df: pd.DataFrame
    vessel_data: dict[str, Any]
    end: bool
    date: str
    sea_state: int
    voyage: str
    T_air: float
    T_sea: float
    T_coff: float
    atm: float
    draft: float
    ssf: float

    def __init__(self, vessel_data: dict[str, Any], enviromental_condition: pd.DataFrame) -> None:
        """Initializes the Environment model with vessel data and weather time-series.

        Args:
            vessel_data (dict): Vessel configuration containing voyage type, draft, and cofferdam temp.
            enviromental_condition (pd.DataFrame): DataFrame containing hourly weather recordings.
        """
        self.df = enviromental_condition
        self.vessel_data = vessel_data

        #----initiate weather variables: day 1----
        self.set_variables()

        #---Ending simulation---
        self.end = False

    def set_variables(self) -> None:
        """Extracts and initializes environmental variables for the current time step."""
        self.date = self.df["date"].iloc[self.ic] # datetime

        self.sea_state = self.df["wind_speed_10m"].iloc[self.ic] # BN

        self.voyage = self.vessel_data["voyage"] # 'L' or 'B'

        self.T_air = to_Kelvin(self.df["apparent_temperature"].iloc[self.ic]) # Air temp [K]
        self.T_sea = to_Kelvin(self.df["sea_surface_temperature"].iloc[self.ic]) # Sea water temp [K]
        self.T_coff = to_Kelvin(self.vessel_data["cofferdam_space"]) # deg C

        self.atm = self.df["pressure_msl"].iloc[self.ic] # Atmospheric pressure [mbar]

        self.draft =  self.vessel_data["draft"]

        self.ssf = ssf(self.sea_state, self.voyage)

    def update(self) -> None:
        """Advances environmental conditions to the next time step.

        Increments the dataset row counter, checks for voyage completion, and refreshes variables.
        """
        self.update_internal_counter() #next day
        # if reach the end of voyage
        if self.ic >= len(self.df):
            # terminate and exit
            self.end = True
            return
        
        #-------update weather variables------
        self.set_variables()

    @classmethod
    def update_internal_counter(cls) -> None:
        """Increments the class-level row pointer for the environmental dataset."""
        cls.ic += 1