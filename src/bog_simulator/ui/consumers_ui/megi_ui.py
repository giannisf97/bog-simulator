from tkinter import ttk
import tkinter as tk

from bog_simulator.utils import resize_img

from bog_simulator.config import RESOURCE_DIR

from bog_simulator.core.consumers import megi

from bog_simulator.ui.components import LabelInput, LabelValue

class MEGI_UI(tk.Frame):
    def __init__(self, parent, model: megi.MEGI, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.model = model

        self.rpm = tk.IntVar(value=self.model.rpm)
        self.m_gas = tk.DoubleVar(value=round(self.model.m_gas, 2))

        self._img = resize_img.import_image(RESOURCE_DIR / "megi_img.png", width=50, height=70)
        self._draw_hmi()

    def _draw_hmi(self):
        input_args = {
            'from_': 45,
            'to': 72,
            'increment': 1,
            'textvariable': self.rpm,
            'width': 10
        }
        label_args = {'text': "Rpm"}
        self.rpm_ui = LabelInput(self, ttk.Spinbox, input_args=input_args, label_args=label_args, width= 50)

        self.m_gas_ui = LabelValue(self, self.m_gas, "Consumption")

        canvas = tk.Canvas(self, width= 50, height= 75)
        canvas.create_image(25, 35, image= self._img)

        self.rpm_ui.pack()
        canvas.pack()
        self.m_gas_ui.pack()

    def update(self):
        rpm = self.rpm.get()
        self.model.update(rpm)
        m_gas = self.model.m_gas
        self.m_gas.set(round(m_gas, 2))


if __name__ == "__main__":
    root = tk.Tk()
    megi_gui = MEGI_UI(root, megi.MEGI(65))

    megi_gui.pack()

    root.mainloop()