"""Main application GUI window module for BOG Simulator."""

from typing import Any
import tkinter as tk
from tkinter import messagebox

from bog_simulator.ui import tank_view
from bog_simulator.ui import components

from bog_simulator.core.vessel import LNGc
from bog_simulator.core.environment import Environment
from bog_simulator.core.consumers import consumer
from bog_simulator.ui import control_panel

class Simulation_GUI(tk.Tk):
    """Main graphical user interface application window.

    Manages the overall Tkinter event loop, coordinating between the visual cargo tanks
    monitor (LNGC_GUI), the consumer machinery control panel (Consumer_Panel),
    and the simulation time progression (continuous run, pause, single-hour step).

    Attributes:
        lngc_gui (LNGC_GUI): Frame containing visual representations of Tanks 1-4.
        control_panel (Consumer_Panel): Frame containing engine and GCU control inputs.
        running (bool): State flag indicating if continuous simulation is active.
        end (bool): Flag indicating if voyage dataset has terminated.
        time_step (int): Simulation advance step in seconds (default: 3600 s / 1 hour).
    """
    lngc_gui: tank_view.LNGC_GUI
    control_panel: control_panel.Consumer_Panel
    running: bool
    end: bool
    time_step: int

    def __init__(self, vessel_model: LNGc, *args: Any, **kwargs: Any) -> None:
        """Initializes the Simulation_GUI application window with vessel model.

        Args:
            vessel_model (LNGc): Central vessel domain model instance.
        """
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
    
    def _fetch_selection(self) -> None:
        """Fetches latest consumption model selections and sets time step to 1 hour (3600s)."""
        self.lngc_gui.model.cons = self.control_panel.model
        self.time_step = 3600

    def _update_all(self) -> None:
        """Advances model state by one time step and refreshes UI widgets."""
        self.lngc_gui.update(self.time_step)
        self.control_panel.update()
        self.control_panel.set_weather_variables(self.lngc_gui.model.env)

        #update end condition
        self.end = self.lngc_gui.model.env.end

    #==========Options==============

    def run_simulation(self) -> None:
        """Executes simulation continuously in loop (1 hour simulated per second).""" 
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

    def step(self) -> None:
        """Advances simulation forward by a single 1-hour time step."""
        if not self.running and not self.end:
            self._fetch_selection()
            self._update_all()
        self.on_end()

    #=========Entry/Ending Points===========

    def on_pause(self, btn: tk.Button) -> None:
        """Pauses continuous simulation and enables the Start button."""
        btn.config(state=tk.NORMAL)
        self.running = False

    def on_end(self) -> None:
        """Handles simulation completion, displays dialog, and renders post-voyage plot."""
        if self.end:
            messagebox.showinfo("End of simulation", "Simulation completed !")
            self.lngc_gui.model.show_stats()

    def on_start(self, btn: tk.Button) -> None:
        """Starts continuous simulation and disables the Start button."""
        #disable start button
        btn.config(state=tk.DISABLED)
        self.running = True
        self.run_simulation()

    #========MAIN================

    def run(self) -> None:
        """Starts the Tkinter main event loop."""
        self.mainloop()