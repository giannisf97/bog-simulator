import tkinter as tk
import pandas as pd

from bog_simulator.ui.consumers_ui import gcu_ui, dfde_ui, megi_ui
from bog_simulator.ui import components

from bog_simulator.core.consumers import consumer, gcu, megi, dfde
from bog_simulator.core import environment

from bog_simulator.utils.data_loader import load_vessel_data, load_weather_variables


class Consumer_Panel(tk.LabelFrame):
    def __init__(self, parent, model: consumer.Consumers, model_env:environment.Environment,  *args, **kwargs):
        super().__init__(parent, text="Control Panel", *args, **kwargs)
        self.model = model
        self.model_env = model_env

        self.gcu_hmi = gcu_ui.GCU_UI(self, model.gcu)
        self.genSets_hmi = [dfde_ui.DFDE_UI(self, genSet_model) for genSet_model in model.gensets]
        self.mainEngines_hmi = [megi_ui.MEGI_UI(self, mainEngine_model) for mainEngine_model in model.mainEngines]
        self.enviroment_ui = components.Enviromental_GUI(self, self.model_env)
        self.options_ui = components.Options(self)

        self._draw_control_hmi()

    def _draw_control_hmi(self):
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

if __name__ == "__main__":
    root = tk.Tk()

    vessel = load_vessel_data()
    enviroment_variables = load_weather_variables()

    megi_models = [megi.MEGI(**megi_params) for megi_params in vessel["Main_Engines"]]
    dfdes_model = [dfde.DFDE(**dfde_params) for dfde_params in vessel["Diesel_Generators"]]
    gcu_model = gcu.GCU(**vessel["Gcu"])
    model_enviroment = environment.Environment(vessel["vessel"], enviroment_variables)
    model = consumer.Consumers(dfdes_model, megi_models, gcu_model)

    consumer_panel = Consumer_Panel(root, model=model, model_env=model_enviroment)

    consumer_panel.pack(padx=10, pady=10, expand=True)

    root.mainloop()