import bog_simulator.core.environment as env
from bog_simulator.utils import data_loader
from bog_simulator.physics import thermodynamics as th , hydrodynamics as hyd, heat_transfer as ht
from bog_simulator.config import DENSITY_LNG as D

class MembraneTank:
    def __init__(self, tank_params: dict, enviroment: env.Environment) -> None:
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
     
    def update_parameters(self, enviroment: env.Environment, dt : int) -> float:
        '''Updates the parameters of the specific tank'''
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

    def update(self, enviroment, dt : int) -> None:
        '''Refresh the tank parameters'''
        if self.access_tank:
            self.update_parameters(dt, enviroment)