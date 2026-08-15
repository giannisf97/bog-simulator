from tkinter import ttk
import tkinter as tk

from bog_simulator.utils import resize_img

from bog_simulator.config import RESOURCE_DIR

from bog_simulator.core.consumers import megi

from bog_simulator.ui.components import LabelInput, LabelValue

from bog_simulator.physics import per

class MEGI_UI(tk.Frame):
    def __init__(self, parent, model: megi.MEGI, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.model = model

        self.rpm = tk.IntVar(value=self.model.rpm)
        self.m_gas = tk.DoubleVar(value=round(per.hour(self.model.m_gas), 2))

        self._img = resize_img.import_image(RESOURCE_DIR / "megi_img.png", width=50, height=70)
        self._draw_hmi()

    def _draw_hmi(self):
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

        self.rpm_ui.pack()
        canvas.pack()
        self.type_label.pack()
        self.m_gas_ui.pack()

    def update(self):
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