"""
DFDE (Dual Fuel Diesel Generator) UI Component.

Provides graphical control and telemetry display for individual auxiliary
DFDE generator sets, including electric power output regulation [kW],
generator start/stop toggling, and fuel gas consumption monitoring [kg/h].
"""

from typing import Any
from pathlib import Path
from PIL import ImageTk

from tkinter import ttk
import tkinter as tk

from bog_simulator.core.consumers import dfde

from bog_simulator.utils import resize_img as resize

from bog_simulator.ui.components import LabelInput, LabelValue

from bog_simulator.physics import per

from bog_simulator.config import RESOURCE_DIR

image: Path = RESOURCE_DIR / "dfde_img.png"

class DFDE_UI(tk.Frame):
    """
    Tkinter frame component for controlling and monitoring a DFDE generator set.

    Attributes:
        model (DFDE): Underlying DFDE generator simulation model instance.
        output (tk.IntVar): Electric power output setpoint [kW].
        m_gas (tk.DoubleVar): Displayed gas fuel consumption [kg/h].
        _img (PhotoImage): Rendered thumbnail of the DFDE engine.
        start_btn (tk.Button): Button toggling generator operational state.
    """
    model: dfde.DFDE
    output: tk.IntVar
    m_gas: tk.DoubleVar
    _img: ImageTk.PhotoImage
    canvas: tk.Canvas
    output_ui: LabelInput
    m_gas_ui: LabelValue
    type_label: tk.Label
    start_btn: tk.Button

    def __init__(self, parent: tk.Misc, model: dfde.DFDE, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the DFDE UI control panel.

        Args:
            parent (tk.Widget): Parent Tkinter container.
            model (dfde.DFDE): DFDE generator model instance.
            *args: Variable length argument list for tk.Frame.
            **kwargs: Arbitrary keyword arguments for tk.Frame.
        """
        super().__init__(parent, *args, **kwargs)

        self.model = model

        self.output = tk.IntVar(value=int(self.model.output))
        self.m_gas = tk.DoubleVar(value= round(per.hour(self.model.m_gas), 2))
        
        self._img = resize.import_image(image, width= 50, height= 70)
        self._draw_hmi()

    def _draw_hmi(self) -> None:
        """Build and pack HMI controls (kW input, engine icon, status, consumption)."""
        #set image of the consumer
        self.canvas = tk.Canvas(self, width= 50, height= 70)
        self.canvas.create_image(25, 35, image= self._img)

        #output controller
        input_args = {
            'from_': self.model.min_output,
            'to': self.model.max_output,
            'increment': 50,
            'textvariable': self.output,
            'width': 10
        }
        label_args = {'text': "Kw"}
        self.output_ui = LabelInput(self, ttk.Spinbox, input_args=input_args, label_args=label_args)

        #gas consumption value
        self.m_gas_ui = LabelValue(self, self.m_gas, "Consumption")

        #type of genset
        self.type_label = tk.Label(self, text=self.model.type)
        self.start_btn = tk.Button(self,
                                   bg= 'green' if self.model.is_operational else 'light grey', 
                                   text= "stop" if self.model.is_operational else 'start', 
                                   command= self.stop_dg if self.model.is_operational else self.start_dg)
        self.output_ui.pack()
        self.canvas.pack()
        self.type_label.pack()
        self.m_gas_ui.pack()
        self.start_btn.pack()

    def stop_dg(self) -> None:
        """Shut down the diesel generator and update UI button state."""
        self.start_btn.configure(bg='light grey', text="start", command=self.start_dg)
        self.model.stop_dg()

    def start_dg(self) -> None:
        """Start the diesel generator and update UI button state."""
        self.start_btn.config(bg='green', text="stop", command=self.stop_dg)
        self.model.start_dg()
        
    def update(self) -> None:
        """
        Synchronize UI electric load setpoint to model and refresh consumption readout.

        Reads target power output [kW] from the spinbox, updates the model quadratic
        consumption calculation, and sets displayed kg/h.
        """
        #receive value from controller
        output_new = self.output.get()

        #update model
        self.model.update(output_new)

        #print current gas consumption to the user
        self.m_gas.set(round(per.hour(self.model.m_gas), 2))

        

if __name__ == "__main__":
    generator1_parameters = {
            "type": 'W8L34DF',
            "is_operating": True,
            "output": 3500
        }
    generator2_parameters = {
                "type": 'W6L34DF',
                "is_operating": True,
                "output": 2650
            }
    root = tk.Tk()

    dfde_ui1 = DFDE_UI(root, dfde.DFDE(**generator1_parameters))
    defde_ui2 = DFDE_UI(root, dfde.DFDE(**generator2_parameters))
    dfde_ui1.grid(row=0, column=0)
    defde_ui2.grid(row=0, column= 1)

    root.mainloop()


