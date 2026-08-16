from tkinter import ttk
import tkinter as tk

from bog_simulator.core.consumers import dfde

from bog_simulator.utils import resize_img as resize

from bog_simulator.ui.components import LabelInput, LabelValue

from bog_simulator.physics import per

from bog_simulator.config import RESOURCE_DIR

image = RESOURCE_DIR / "dfde_img.png"

class DFDE_UI(tk.Frame):
    def __init__(self, parent, model: dfde.DFDE, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.model = model

        self.output = tk.IntVar(value= self.model.output)
        self.m_gas = tk.DoubleVar(value= round(per.hour(self.model.m_gas), 2))
        
        self._img = resize.import_image(image, width= 50, height= 70)
        self._draw_hmi()

    def _draw_hmi(self):
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

    def stop_dg(self):
        self.start_btn.configure(bg='light grey', text="start", command=self.start_dg)
        self.model.stop_dg()

    def start_dg(self):
        self.start_btn.config(bg='green', text="stop", command=self.stop_dg)
        self.model.start_dg()
        
    def update(self):
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


