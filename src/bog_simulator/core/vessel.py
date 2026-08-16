import numpy as np

from bog_simulator.core import environment as env
from bog_simulator.core import tank as tnk
from bog_simulator.core.consumers import consumer

from bog_simulator.physics.thermodynamics import total_dp

from bog_simulator.utils.statistics import Statistics

class LNGc:
    internal_timer = 0 # timer for seconds running simulation
    '''174k DW Lng carrier model'''
    def __init__(self, tank_params: list, enviroment: env.Environment, consumption: consumer.Consumers, production: float) -> None:
        #--initialize interfering conditions--
        self.env = enviroment # enviromental condition class
        self.cons = consumption # consumers class
        self.prod = production # Total production kg/h
        self.tank_config = tank_params
        #---Contains---
        self.tanks = self.init_tanks(self.tank_config) #list of tanks
        self.vapor_header = np.mean([tank.P_tank for tank in self.tanks]) # Vapor header pressure let be the mean pressure of the tanks

        #---Data acquisition---
        self.stats = Statistics(self.vapor_header, self.cons.total_consumption())

    def init_tanks(self, tank_params: list):
        '''Helper method return a list of MembraneTank models'''
        return [tnk.MembraneTank(tank, self.env) for tank in tank_params]

    def update_pressure(self, dt : int) -> float:
        '''Updates the conditions of all the tanks per dt'''
        for tank in self.tanks:
            tank.P_tank += total_dp(self.tanks, self.cons.total_consumption(), self.prod, dt) / 100
            if tank.P_tank >330:
                tank.P_tank = 330
            elif tank.P_tank < 0:
                tank.P_tank = 0
        return np.mean([tank.P_tank for tank in self.tanks])

    def update_enviroment_conditions(self):
        #when 1 day passed update enviromental conditions
        if self.internal_timer % 86_400 == 0 and self.internal_timer != 0:
            self.env.update()

    def update_tanks(self, dt : int) -> float:
        '''Updates the conditions of all the tanks per dt'''
        self.update_internal_timer(dt)
        self.update_enviroment_conditions()
        self.vapor_header = self.update_pressure(dt)

        self.stats.fetch_data(self.vapor_header, self.cons.total_consumption(), dt)

        for tank in self.tanks:
            tank.update(dt, self.env)

    def show_stats(self):
        self.stats.show_plot()

    @classmethod
    def update_internal_timer(cls, dt):
        cls.internal_timer += dt
            

