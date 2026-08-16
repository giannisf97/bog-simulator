import tkinter as tk
from tkinter import messagebox

from bog_simulator.ui import tank_view
from bog_simulator.ui import components

from bog_simulator.core.vessel import LNGc
from bog_simulator.core.environment import Environment
from bog_simulator.core.consumers import consumer
from bog_simulator.ui import control_panel

class Simulation_GUI(tk.Tk):
    '''Main Application Window'''
    def __init__(self, vessel_model: LNGc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #initialize the main gui including all the tanks
        self.lngc_gui = tank_view.LNGC_GUI(self, vessel_model)
        self.lngc_gui.grid(row=0, column=0, rowspan=2)        

        #initialize the control buttons
        self.control_panel = control_panel.Consumer_Panel(self, 
                                                          self.lngc_gui.model.cons, 
                                                          self.lngc_gui.model.env, 
                                                          self.on_start,
                                                          self.on_pause,
                                                          self.step)
        self.control_panel.grid(row=0, column=1, sticky='n')

        #Conditions
        self.running = False
        self.end = self.lngc_gui.model.env.end

    #============Private=============
    
    def _fetch_selection(self):
        '''Fetch consumption and time step'''
        self.lngc_gui.model.cons = self.control_panel.model
        self.time_step = int(self.control_panel.options_ui.time_step.get()) * 60

    def _update_all(self):
        '''Update model and UI variables'''
        self.lngc_gui.update(self.time_step)
        self.control_panel.update()
        self.control_panel.set_weather_variables(self.lngc_gui.model.env)

        #update end condition
        self.end = self.lngc_gui.model.env.end

    #==========Options==============

    def run_simulation(self):
        '''Method that runs continously the simulation with a given time step''' 
        if self.running and not self.end:
            self._fetch_selection()
            
            self._update_all()
            # Post-execution state check
            if not self.end:
                self.after(1000, self.run_simulation)
            else:
                # Terminate
                self.on_end()
                
        elif self.end:
            self.on_end()

    def step(self):
        if not self.running and not self.end:
            self._fetch_selection()
            self._update_all()
        self.on_end()

    #=========Entry/Ending Points===========

    def on_pause(self, btn):
        btn.config(state=tk.NORMAL)
        self.running = False

    def on_end(self):
        if self.end:
            messagebox.showinfo("End of simulation", "Simulation completed !")
            self.lngc_gui.model.show_stats()

    def on_start(self, btn):
        #disable start button
        btn.config(state=tk.DISABLED)
        self.running = True
        self.run_simulation()

    #========MAIN================

    def run(self):
        self.mainloop()