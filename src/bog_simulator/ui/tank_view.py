import tkinter as tk

from bog_simulator.ui import components

from bog_simulator.core import vessel
from bog_simulator.core import tank

from bog_simulator.physics.thermodynamics import to_degC


class LNGC_GUI(tk.Frame):
    '''Tk.Frame subclass that contains all the GUI tanks'''
    def __init__(self, parent, model : vessel.LNGc, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.model = model
        self.tanks = [Tank_GUI(self, self.model.tanks[index]) for index in range(4)]
        self.init_tanks_gui()
    
    def init_tanks_gui(self):
        '''Position the tank guis inside self class'''
        for index, tank in enumerate(self.tanks):
            tank.grid(row = 0, column = index)

    def update(self, dt):
        '''Update values'''
        self.model.update_internal_timer(dt)
        self.model.update_enviroment_conditions() 
        self.model.vapor_header = self.model.update_pressure(dt)# update the pressure in the Vapor header
        self.model.stats.fetch_data(self.model.vapor_header, self.model.cons.total_consumption(), dt)
        #for all the tanks update their values
        for tank in self.tanks:
            tank.update(dt, self.model.env)

class Tank_GUI(tk.LabelFrame):
    '''Child class of tk.LabelFrame representing each tank with values'''
    def __init__(self,parent, model: tank.MembraneTank, *args, **kwargs):
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
        
    def set_values(self):
        '''Set the values of tank parameters'''
        self.P_tank.set(round(self.model.P_tank, 2))
        self.liquid_temp.set(round(to_degC(self.model.avg_liquid_temp), 2))
        self.vapor_temp.set(round(to_degC(self.model.avg_vapor_temp), 2))
        self.liquid_vol.set(round(self.model.liquid_vol, 2))
        self.vapor_vol.set(round(self.model.vapor_vol, 2))
        self.liquid_level.set(round(self.model.liquid_level, 2))
        self.filling_ratio = self.model.liquid_level / self.model.tank_geometry["height"]
    
    def update(self, dt, enviroment):
        '''Updates the values of tank parameters'''
        self.model.update(dt, enviroment)
        self.set_values()
        self.canvas.coords(self.liquid_level_bar,90,
                           self.y1 - self.filling_ratio * (self.y1-self.y0),
                            110,180)