"""Vessel coordinator module.

Defines the central LNG carrier (LNGC) class integrating cargo tanks, voyage
environmental conditions, machinery consumers, and voyage performance statistics.
"""

import numpy as np

from typing import Any

from bog_simulator.core.environment import Environment
from bog_simulator.core import tank as tnk
from bog_simulator.core.consumers import consumer

from bog_simulator.physics.thermodynamics import total_dp

from bog_simulator.utils.statistics import Statistics

class LNGc:
    """174,000 m3 Deadweight Membrane-Type Liquefied Natural Gas Carrier (LNGC).

    Coordinates thermodynamic state updates across all cargo tanks, monitors vapor
    header pressure, routes boil-off gas to fuel consumers, advances the voyage
    timeline, and records historical time-series data for post-voyage analysis.

    Attributes:
        internal_timer (int): Total simulated voyage elapsed time in seconds.
        env (Environment): Environmental conditions and weather model instance.
        cons (Consumers): Aggregated fuel gas consumers (ME-GI, DFDE, GCU).
        prod (float): Additional BOG production rate [kg/h].
        tank_config (list): Configuration dictionaries for each cargo tank.
        tanks (list[MembraneTank]): Instantiated MembraneTank model objects.
        vapor_header (float): Mean pressure in the common vapor header [mbar].
        stats (Statistics): Statistical recorder for pressure and consumption.
    """
    internal_timer: int = 0 # timer for seconds running simulation
    
    env: Environment
    cons: consumer.Consumers
    prod: float | int
    tank_config: list[dict[str, Any]]
    tanks: list[tnk.MembraneTank]
    vapor_header: float
    stats: Statistics

    def __init__(self, tank_params: list[dict[str, Any]], enviroment: Environment, consumption: consumer.Consumers, production: float | int) -> None:
        """Initializes the LNG Carrier vessel model.

        Args:
            tank_params (list): List of configuration dicts for each of the 4 tanks.
            enviroment (env.Environment): Voyage environmental and weather tracker.
            consumption (consumer.Consumers): Consumers manager handling engine loads.
            production (float): External gas production or injection rate [kg/h].
        """
        #--initialize interfering conditions--
        self.env = enviroment # enviromental condition class
        self.cons = consumption # consumers class
        self.prod = production # Total production kg/h
        self.tank_config = tank_params
        #---Contains---
        self.tanks = self.init_tanks(self.tank_config) #list of tanks
        self.vapor_header = float(np.mean([tank.P_tank for tank in self.tanks])) # Vapor header pressure let be the mean pressure of the tanks

        #---Data acquisition---
        self.stats = Statistics(self.vapor_header, self.cons.total_consumption())

    def init_tanks(self, tank_params: list[dict[str, Any]]) -> list[tnk.MembraneTank]:
        """Helper method returning a list of initialized MembraneTank instances.

        Args:
            tank_params (list): List of parameter dictionaries for the cargo tanks.

        Returns:
            list[MembraneTank]: List of initialized membrane cargo tanks.
        """
        return [tnk.MembraneTank(tank, self.env) for tank in tank_params]

    def update_pressure(self, dt: int) -> float:
        """Updates internal pressure of all interconnected cargo tanks over time step dt.

        Applies pressure change from ideal gas mass balance (converted from Pa to mbar by dividing by 100),
        clamped between 0 mbar (vacuum limit) and 330 mbar (safety relief valve setting).

        Args:
            dt (int): Time step duration in seconds.

        Returns:
            float: Updated average vapor header pressure [mbar].
        """
        for tank in self.tanks:
            tank.P_tank += total_dp(self.tanks, self.cons.total_consumption(), self.prod, dt) / 100
            if tank.P_tank >330:
                tank.P_tank = 330
            elif tank.P_tank < 0:
                tank.P_tank = 0
        return float(np.mean([tank.P_tank for tank in self.tanks]))

    def update_enviroment_conditions(self) -> None:
        """Advances environmental weather variables to the next simulation hour."""
        #when 1 hour passed
        self.env.update()

    def update_tanks(self, dt: int) -> None:
        """Performs a comprehensive update step for environmental conditions and tanks.

        Args:
            dt (int): Time increment in seconds.

        Returns:
            None
        """
        self.update_internal_timer(dt)
        self.update_enviroment_conditions()
        self.vapor_header = self.update_pressure(dt)

        self.stats.fetch_data(self.vapor_header, self.cons.total_consumption(), dt)

        for tank in self.tanks:
            tank.update(dt, self.env)

    def show_stats(self) -> None:
        """Renders the post-voyage Matplotlib dual-axis performance charts."""
        self.stats.show_plot()

    @classmethod
    def update_internal_timer(cls, dt: int) -> None:
        """Increments the class-level elapsed simulation timer by dt seconds.

        Args:
            dt (int): Time step in seconds.
        """
        cls.internal_timer += dt
            

