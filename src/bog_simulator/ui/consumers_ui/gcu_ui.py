"""
Gas Combustion Unit (GCU) UI Component.

Provides graphical control and status interface for the Gas Combustion Unit,
allowing operator adjustment of the gas burn rate [kg/h] and activation/deactivation.
"""

from typing import Any
from PIL import ImageTk

import tkinter as tk
from tkinter import ttk

from bog_simulator.config import RESOURCE_DIR

from bog_simulator.core.consumers import gcu
from bog_simulator.physics import per

from bog_simulator.utils import resize_img

from bog_simulator.ui.components import LabelInput

class GCU_UI(tk.Frame):
    """
    Tkinter frame component for controlling and monitoring the GCU.

    Attributes:
        model (GCU): Underlying Gas Combustion Unit model instance.
        rate (tk.IntVar): Controlled burning rate in kilograms per hour [kg/h].
        _img (PhotoImage): Rendered thumbnail of the GCU plant.
        start_btn (tk.Button): Button toggling GCU operation on or off.
    """
    model: gcu.GCU
    rate: tk.IntVar
    _img: ImageTk.PhotoImage
    rate_ui: LabelInput
    canvas: tk.Canvas
    label: tk.Label
    start_btn: tk.Button

    def __init__(self, parent: tk.Misc, model: gcu.GCU, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the GCU UI control panel.

        Args:
            parent (tk.Widget): Parent Tkinter container.
            model (gcu.GCU): GCU model instance.
            *args: Variable length argument list for tk.Frame.
            **kwargs: Arbitrary keyword arguments for tk.Frame.
        """
        super().__init__(parent, *args, **kwargs)
        self.model = model
        self.rate = tk.IntVar(value=int(per.hour(self.model.m_gas)))
        self._img = resize_img.import_image(RESOURCE_DIR / "gcu_hmi.png", 50, 70)
        self._draw_hmi()

    def _draw_hmi(self) -> None:
        """Build and pack HMI controls (burn rate spinbox, unit icon, status toggle)."""
        input_args = {
            'from_': self.model.capacity["min"],
            'to': self.model.capacity["max"],
            'increment': 100,
            'textvariable': self.rate,
            'width': 10
        }
        label_args = {'text': "Rate"}

        self.rate_ui = LabelInput(self, ttk.Spinbox, input_args=input_args, label_args=label_args, width= 50)

        self.canvas = tk.Canvas(self, width= 50, height= 70)
        self.canvas.create_image(25, 35, image= self._img)

        self.label = tk.Label(self, text="GCU")

        self.start_btn = tk.Button(self,
                                   bg= 'green' if self.model.is_operational else 'light grey', 
                                   text= "start", 
                                   command= self.stop_gcu if self.model.is_operational else self.start_gcu)

        self.rate_ui.pack()
        self.canvas.pack()
        self.label.pack()
        self.start_btn.pack()

    def stop_gcu(self) -> None:
        """Extinguish the GCU burner and update UI button appearance."""
        self.start_btn.configure(bg='light grey', text="start", command=self.start_gcu)
        self.model.stop_gcu()

    def start_gcu(self) -> None:
        """Ignite the GCU burner and update UI button appearance."""
        self.start_btn.config(bg='green', text="stop", command=self.stop_gcu)
        self.model.start_gcu()

    def update(self) -> None:
        """
        Synchronize UI burn rate setpoint to the GCU model.

        Reads target combustion rate [kg/h] from the spinbox and passes it
        to the model update method.
        """
        rate = self.rate.get()
        self.model.update(rate)




if __name__ == "__main__":
    gcu_config = {
        "rate": 2000,
        "is_operational": True
    }
    root = tk.Tk()
    gcu_hmi1 = GCU_UI(root, gcu.GCU(**gcu_config))
    gcu_hmi2 = GCU_UI(root, gcu.GCU(**gcu_config))
    gcu_hmi1.pack(side='left')
    gcu_hmi2.pack(side= "left")

    root.mainloop()