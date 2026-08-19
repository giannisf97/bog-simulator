import pandas as pd
from bog_simulator.physics.thermodynamics import to_Kelvin
from bog_simulator.physics.hydrodynamics import ssf

class Environment:
    '''Simulates the enviromental conditions of a given voyage'''
    ic = 0 #internal counter refers to the days
    def __init__(self, vessel_data: dict, enviromental_condition: pd.Dataframe) -> None:
        self.df = enviromental_condition
        self.vessel_data = vessel_data

        #----initiate weather variables: day 1----
        self.set_variables()

        #---Ending simulation---
        self.end = False

    def set_variables(self) -> None:
        '''Helper method to set weather variables'''
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
        '''Updates enviromental conditions'''
        self.update_internal_counter() #next day
        # if reach the end of voyage
        if self.ic >= len(self.df):
            # terminate and exit
            self.end = True
            return
        
        #-------update weather variables------
        self.set_variables()

    @classmethod
    def update_internal_counter(cls):
        cls.ic += 1