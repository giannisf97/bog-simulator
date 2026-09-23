"""Cargo tanks visualization GUI module."""

from typing import Any, TYPE_CHECKING
import tkinter as tk

from bog_simulator.ui import components

from bog_simulator.core.vessel import LNGc
from bog_simulator.core.tank import MembraneTank

from bog_simulator.physics.thermodynamics import to_degC

if TYPE_CHECKING:
    from bog_simulator.core.environment import Environment

class LNGC_GUI(tk.Frame):
    """Container frame holding the visual widgets for all 4 cargo tanks.

    Attributes:
        model (LNGc): Central vessel domain model.
        tanks (list[Tank_GUI]): List of GUI widgets for each cargo tank.
    """
    model: LNGc
    tanks: list["Tank_GUI"]

    def __init__(self, parent: tk.Misc, model: LNGc, *args: Any, **kwargs: Any) -> None:
        """Initializes the LNGC cargo tanks display grid.

        Args:
            parent: Parent Tkinter widget.
            model (LNGc): Vessel domain model instance.
        """
        super().__init__(parent, *args, **kwargs)
        self.model = model
        self.tanks = [Tank_GUI(self, self.model.tanks[index]) for index in range(4)]
        self.init_tanks_gui()
    
    def init_tanks_gui(self) -> None:
        """Positions the 4 tank GUI widgets side-by-side in a horizontal grid."""
        for index, tank_widget in enumerate(self.tanks):
            tank_widget.grid(row = 0, column = index)

    def update(self, dt: int) -> None:  # type: ignore[override]
        """Advances vessel simulation state by dt seconds and refreshes all tank widgets.

        Args:
            dt (int): Time step duration in seconds.
        """
        self.model.update_internal_timer(dt)
        self.model.update_enviroment_conditions() 
        self.model.vapor_header = self.model.update_pressure(dt)# update the pressure in the Vapor header
        self.model.stats.fetch_data(self.model.vapor_header, self.model.cons.total_consumption(), dt)
        #for all the tanks update their values
        for tank_widget in self.tanks:
            tank_widget.update(dt, self.model.env)

class Tank_GUI(tk.LabelFrame):
    """Individual cargo tank HMI panel with graphic level canvas and numerical telemetry.

    Attributes:
        model (MembraneTank): Underlying thermodynamic tank model.
        filling_ratio (float): Ratio of liquid level height to total tank height.
        P_tank (tk.DoubleVar): Displayed tank pressure [mbar].
        liquid_temp (tk.DoubleVar): Displayed liquid LNG temperature [°C].
        vapor_temp (tk.DoubleVar): Displayed vapor phase temperature [°C].
        liquid_vol (tk.DoubleVar): Displayed liquid volume [m^3].
        vapor_vol (tk.DoubleVar): Displayed vapor volume [m^3].
        liquid_level (tk.DoubleVar): Displayed liquid sounding level [m].
    """
    model: MembraneTank
    filling_ratio: float
    x0: int
    y0: int
    x1: int
    y1: int
    canvas: tk.Canvas
    tank: int
    tank_capacity: int
    liquid_level_bar: int
    P_tank: tk.DoubleVar
    liquid_temp: tk.DoubleVar
    vapor_temp: tk.DoubleVar
    liquid_vol: tk.DoubleVar
    vapor_vol: tk.DoubleVar
    liquid_level: tk.DoubleVar

    def __init__(self, parent: tk.Misc, model: MembraneTank, *args: Any, **kwargs: Any) -> None:
        """Initializes a Tank_GUI widget for a specific cargo tank model.

        Args:
            parent: Parent Tkinter widget.
            model (MembraneTank): MembraneTank model instance.
        """
        super().__init__(parent,text=f"Tank {model.tank_num}", *args, **kwargs)
        self.model = model #refers to the model tank created in 'Estimation_model.py'
        #filling ratio of the tank
        self.filling_ratio = self.model.liquid_level / self.model.tank_geometry["height"]
        #coordinates of the full tank
        self.x0, self.y0, self.x1, self.y1 = 90, 80, 110, 180 
        
        #configure the graphical representation of the tanks
        self.canvas = tk.Canvas(self, width=250, height=210)
        self.canvas.pack(expand=True)
        self.tank = self.canvas.create_rectangle((10,10),(200,200), fill="light grey")
        self.tank_capacity = self.canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, outline="black")
        self.liquid_level_bar = self.canvas.create_rectangle(90,self.y1 - self.filling_ratio * (self.y1-self.y0),
                                                             110,180,fill="blue")

        #declare the variables that will hold certain tank parameters
        self.P_tank = tk.DoubleVar()
        self.liquid_temp = tk.DoubleVar()
        self.vapor_temp=tk.DoubleVar()
        self.liquid_vol = tk.DoubleVar()
        self.vapor_vol = tk.DoubleVar()
        self.liquid_level = tk.DoubleVar()

        #set and initialize all the values
        self.set_values()

        #Place the tank parameters in Label-Value format in the tank GUI
        self.P_tank_label = components.LabelValue(self, self.P_tank, text='Tank Pressure [mbar]')
        self.P_tank_label.pack()

        self.liq_temp_label= components.LabelValue(self,
                                        self.liquid_temp,
                                        text='Avg. Liquid Temperature [degC]')
        self.liq_temp_label.pack(expand=True)

        self.vapor_temp_label = components.LabelValue(self, textvariable=self.vapor_temp,
                                           text="Avg. Vapor Temperature [degC]")
        self.vapor_temp_label.pack(expand=True)

        self.liquid_vol_label = components.LabelValue(self, textvariable=self.liquid_vol,
                                           text="LNG Volume [m3]")
        self.liquid_vol_label.pack(expand=True)

        self.vapor_vol_label = components.LabelValue(self, textvariable=self.vapor_vol,
                                          text="Vapor Volume [m3]")
        self.vapor_vol_label.pack(expand=True)

        self.liquid_level_label = components.LabelValue(self, textvariable=self.liquid_level,
                                             text="LNG Level [m]")
        self.liquid_level_label.pack(expand=True)
        
    def set_values(self) -> None:
        """Updates Tkinter variables from model and calculates current filling ratio."""
        self.P_tank.set(round(self.model.P_tank, 2))
        self.liquid_temp.set(round(to_degC(self.model.avg_liquid_temp), 2))
        self.vapor_temp.set(round(to_degC(self.model.avg_vapor_temp), 2))
        self.liquid_vol.set(round(self.model.liquid_vol, 2))
        self.vapor_vol.set(round(self.model.vapor_vol, 2))
        self.liquid_level.set(round(self.model.liquid_level, 2))
        self.filling_ratio = self.model.liquid_level / self.model.tank_geometry["height"]
    
    def update(self, dt: int, enviroment: "Environment") -> None:  # type: ignore[override]
        """Refreshes the tank model state and updates canvas level bar coordinates.

        Args:
            dt (int): Time step in seconds.
            enviroment (Environment): Current environmental conditions instance.
        """
        self.model.update(dt, enviroment)
        self.set_values()
        self.canvas.coords(self.liquid_level_bar,90,
                           self.y1 - self.filling_ratio * (self.y1-self.y0),
                            110,180)