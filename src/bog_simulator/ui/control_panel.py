"""Machinery and consumers HMI control panel module."""

import tkinter as tk
import pandas as pd

from bog_simulator.ui.consumers_ui import gcu_ui, dfde_ui, megi_ui
from bog_simulator.ui import components

from bog_simulator.core.consumers import consumer, gcu, megi, dfde
from bog_simulator.core import environment
from bog_simulator.physics import per
from bog_simulator.utils.data_loader import load_vessel_data, load_weather_variables


from typing import Any, Callable

class Consumer_Panel(tk.LabelFrame):
    """Interactive control panel for propulsion engines, generators, GCU, and weather HUD.

    Attributes:
        model (consumer.Consumers): Consumers domain model instance.
        model_env (environment.Environment): Environment domain model instance.
        gcu_hmi (gcu_ui.GCU_UI): GCU control interface.
        genSets_hmi (list[dfde_ui.DFDE_UI]): List of DFDE generator control widgets.
        mainEngines_hmi (list[megi_ui.MEGI_UI]): List of ME-GI main engine control widgets.
        enviroment_ui (components.Enviromental_GUI): Environmental conditions HUD widget.
        options_ui (components.Options): Simulation start/pause/step controls.
        consumption (tk.DoubleVar): Aggregated fuel gas consumption display [kg/h].
    """
    model: consumer.Consumers
    model_env: environment.Environment
    gcu_hmi: gcu_ui.GCU_UI
    genSets_hmi: list[dfde_ui.DFDE_UI]
    mainEngines_hmi: list[megi_ui.MEGI_UI]
    enviroment_ui: components.Enviromental_GUI
    options_ui: components.Options
    consumption: tk.DoubleVar
    labelValue: components.LabelValue

    def __init__(
        self,
        parent: tk.Misc,
        model: consumer.Consumers,
        model_env: environment.Environment,
        start: Callable[[tk.Button], None] = lambda b: None,
        pause: Callable[[tk.Button], None] = lambda b: None,
        step: Callable[[], None] = lambda: None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Initializes the Consumer_Panel with consumer models and control callbacks.

        Args:
            parent: Parent Tkinter widget.
            model (consumer.Consumers): Consumers domain model.
            model_env (environment.Environment): Environment model.
            start (callable): Callback for simulation start.
            pause (callable): Callback for simulation pause.
            step (callable): Callback for simulation single step.
        """
        super().__init__(parent, text="Control Panel", *args, **kwargs)
        self.model = model
        self.model_env = model_env

        self.gcu_hmi = gcu_ui.GCU_UI(self, model.gcu)
        self.genSets_hmi = [dfde_ui.DFDE_UI(self, genSet_model) for genSet_model in model.gensets]
        self.mainEngines_hmi = [megi_ui.MEGI_UI(self, mainEngine_model) for mainEngine_model in model.mainEngines]
        self.enviroment_ui = components.Enviromental_GUI(self, self.model_env)
        self.options_ui = components.Options(self, start, pause, step)

        self.consumption = tk.DoubleVar(value= round(per.hour(self.model.total_consumption()), 2))

        self.labelValue = components.LabelValue(self, textvariable=self.consumption, text="Consumption")
        self._draw_control_hmi()

    def _draw_control_hmi(self) -> None:
        """Arranges machinery widgets, environmental HUD, and buttons in a grid layout."""
        #======GCU=======
        self.gcu_hmi.grid(row=0, column= 0)

        #=====Generator Sets======
        for col, genSet_hmi in enumerate(self.genSets_hmi):
            genSet_hmi.grid(row=1, column=col)

        #=====Main Engines========
        for col,mainEngine_hmi in enumerate(self.mainEngines_hmi):
            mainEngine_hmi.grid(row=2, column=col)

        #=====Enviroment=========
        self.enviroment_ui.grid(row=0, column=1, columnspan=3, sticky='n')

        #======Options==========
        self.options_ui.grid(row=2, column=2, columnspan=2)

        ########## consumption#############
        self.labelValue.grid(row=3, column=0, columnspan=4)

    def update(self) -> None:
        """Refreshes all consumer HMI widgets and updates total fuel gas consumption readout."""
        self.gcu_hmi.update()
        for genSet_hmi in self.genSets_hmi:
            genSet_hmi.update()
        for mainEngine_hmi in self.mainEngines_hmi:
            mainEngine_hmi.update()

        self.consumption.set(round(per.hour(self.model.total_consumption()), 2)) 

    def set_weather_variables(self, weather_variables: environment.Environment) -> None:
        """Passes updated environmental variables to the environmental HUD widget.

        Args:
            weather_variables (Environment): Updated environmental model.
        """
        self.enviroment_ui.set_values(weather_variables)

if __name__ == "__main__":
    root = tk.Tk()

    vessel = load_vessel_data()
    enviroment_variables = load_weather_variables()

    megi_models = [megi.MEGI(**megi_params) for megi_params in vessel["Main_Engines"]]
    dfdes_model = [dfde.DFDE(**dfde_params) for dfde_params in vessel["Diesel_Generators"]]
    gcu_model = gcu.GCU(**vessel["Gcu"])
    model_enviroment = environment.Environment(vessel["vessel"], enviroment_variables)
    model_consumers = consumer.Consumers(dfdes_model, megi_models, gcu_model)

    consumer_panel = Consumer_Panel(root, model=model_consumers, model_env=model_enviroment)

    consumer_panel.pack(padx=10, pady=10, expand=True)

    root.mainloop()