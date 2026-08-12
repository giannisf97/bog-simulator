import tkinter as tk
from tkinter import messagebox

from bog_simulator.ui import tank_view
from bog_simulator.ui import components

from bog_simulator.core.vessel import LNGc
from bog_simulator.core.environment import Environment
from bog_simulator.core.tank import MembraneTank


class Simulation_GUI(tk.Tk):
    '''Main Application Window'''
    def __init__(self, vessel_model: LNGc, environment: Environment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #initialize the main gui including all the tanks
        self.lngc_gui = tank_view.LNGC_GUI(self, vessel_model)
        self.lngc_gui.grid(row=0, column=0, rowspan=2)        
        #initialize the control buttons
        self.control_panel = components.Control_Panel(self)
        self.control_panel.grid(row=0, column=1, sticky='n')

        self.enviromental_gui = components.Enviromental_GUI(self, environment)
        self.enviromental_gui.grid(row=1, column=1, sticky='n')
        #set 0 or False
        self.running = False
        

    def run_simulation(self):
        '''Method that runs continously the simulation with a given time step''' 
        if self.running and not self.lngc_gui.model.env.end:
            # Fetch consumption and time step
            self.lngc_gui.model.cons = -float(self.control_panel.consumption_spinbox.get())
            self.time_step = int(self.control_panel.time_step.get()) * 60
            
            # Update model and UI variables
            self.lngc_gui.update(self.time_step)
            self.enviromental_gui.set_values(self.lngc_gui.model.env)
            # Post-execution state check
            if not self.lngc_gui.model.env.end:
                self.after(1000, self.run_simulation)
            else:
                # Terminate
                self.on_end()
                
        elif self.lngc_gui.model.env.end:
            self.on_end()

    def on_pause(self):
        self.control_panel.start_button.config(state=tk.NORMAL)
        self.running = False

    def on_end(self):
        if self.lngc_gui.model.env.end:
            messagebox.showinfo("End of simulation", "Simulation completed !")
            self.lngc_gui.model.show_stats()

    def on_start(self):
        #disable start button
        self.control_panel.start_button.config(state=tk.DISABLED)
        self.running = True
        self.run_simulation()

    def step(self):
        if not self.running and not self.lngc_gui.model.env.end:
            self.lngc_gui.model.cons = -float(self.control_panel.consumption_spinbox.get())
            self.time_step = int(self.control_panel.time_step.get()) * 60
            self.lngc_gui.update(self.time_step)
            self.enviromental_gui.set_values(self.lngc_gui.model.env)
        self.on_end()

    def run(self):
        self.mainloop()