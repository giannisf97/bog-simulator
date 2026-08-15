import tkinter as tk
from tkinter import ttk

from bog_simulator.config import RESOURCE_DIR

from bog_simulator.core.consumers import gcu

from bog_simulator.utils import resize_img

from bog_simulator.ui.components import LabelInput

class GCU_UI(tk.Frame):
    def __init__(self, parent, model: gcu.GCU, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.model = model
        self.rate = tk.IntVar(value=self.model.rate)
        self._img = resize_img.import_image(RESOURCE_DIR / "gcu_hmi.png", 50, 70)
        self._draw_hmi()

    def _draw_hmi(self):
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

        self.rate_ui.pack()
        self.canvas.pack()
        self.label.pack()

    def update(self):
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