"""
ME-GI Propulsion Engine UI Component.

Provides graphical control and telemetry display for a MAN ME-GI
high-pressure two-stroke main propulsion engine, including RPM setpoint
adjustment, start/stop operation, and hourly gas consumption feedback.
"""

from typing import Any
from PIL import ImageTk

from tkinter import ttk
import tkinter as tk

from bog_simulator.utils import resize_img

from bog_simulator.config import RESOURCE_DIR

from bog_simulator.core.consumers import megi

from bog_simulator.ui.components import LabelInput, LabelValue

from bog_simulator.physics import per

class MEGI_UI(tk.Frame):
    """
    Tkinter frame component for controlling and monitoring an ME-GI engine.

    Attributes:
        model (MEGI): Underlying ME-GI engine simulation model instance.
        rpm (tk.IntVar): Engine rotational speed control variable [RPM].
        m_gas (tk.DoubleVar): Displayed gas fuel consumption [kg/h].
        _img (PhotoImage): Rendered thumbnail of the ME-GI engine.
        start_btn (tk.Button): Button toggling operational / standby state.
    """
    model: megi.MEGI
    rpm: tk.IntVar
    m_gas: tk.DoubleVar
    _img: ImageTk.PhotoImage
    rpm_ui: LabelInput
    m_gas_ui: LabelValue
    type_label: tk.Label
    start_btn: tk.Button

    def __init__(self, parent: tk.Misc, model: megi.MEGI, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the ME-GI UI control panel.

        Args:
            parent (tk.Widget): Parent Tkinter container.
            model (megi.MEGI): ME-GI model instance.
            *args: Variable length argument list for tk.Frame.
            **kwargs: Arbitrary keyword arguments for tk.Frame.
        """
        super().__init__(parent, *args, **kwargs)
        self.model = model

        self.rpm = tk.IntVar(value=int(self.model.rpm))
        self.m_gas = tk.DoubleVar(value=round(per.hour(self.model.m_gas), 2))

        self._img = resize_img.import_image(RESOURCE_DIR / "megi_img.png", width=50, height=70)
        self._draw_hmi()

    def _draw_hmi(self) -> None:
        """Build and pack HMI controls (RPM input, engine icon, status, consumption)."""
        input_args = {
            'from_': self.model.rpm_limit["min"],
            'to': self.model.rpm_limit["max"],
            'increment': 1,
            'textvariable': self.rpm,
            'width': 10
        }
        label_args = {'text': "Rpm"}
        self.rpm_ui = LabelInput(self, ttk.Spinbox, input_args=input_args, label_args=label_args, width= 50)

        self.m_gas_ui = LabelValue(self, self.m_gas, "Consumption")

        canvas = tk.Canvas(self, width= 50, height= 75)
        canvas.create_image(25, 35, image= self._img)

        self.type_label = tk.Label(self, text=self.model.type)

        self.start_btn = tk.Button(self,
                                   bg= 'green' if self.model.is_operational else 'light grey', 
                                   text= "stop" if self.model.is_operational else 'start', 
                                   command= self.stop_engine if self.model.is_operational else self.start_engine)
        
        self.rpm_ui.pack()
        canvas.pack()
        self.type_label.pack()
        self.m_gas_ui.pack()
        self.start_btn.pack()

    def stop_engine(self) -> None:
        """Shut down the ME-GI engine and update the UI button appearance."""
        self.start_btn.configure(bg='light grey', text="start", command=self.start_engine)
        self.model.stop_engine()

    def start_engine(self) -> None:
        """Start the ME-GI engine and update the UI button appearance."""
        self.start_btn.config(bg='green', text="stop", command=self.stop_engine)
        self.model.start_engine()

    def update(self) -> None:
        """
        Synchronize UI inputs to the engine model and refresh displayed consumption.

        Reads target RPM from the spinbox, updates the model physics, and converts
        mass consumption rate from kg/s to displayed kg/h.
        """
        rpm = self.rpm.get()
        self.model.update(rpm)
        new_m_gas = self.model.m_gas
        self.m_gas.set(round(per.hour(new_m_gas), 2))


if __name__ == "__main__":
    megi_config = {
        "type": "5G70ME-C-GI Tier III",
        "rpm": 65,
        "is_operational": True
    }

    root = tk.Tk()
    megi_gui = MEGI_UI(root, megi.MEGI(**megi_config))
    megi_gui2 = MEGI_UI(root, megi.MEGI(**megi_config))
    megi_gui.pack(side="left")
    megi_gui2.pack(side="left")
    root.mainloop()