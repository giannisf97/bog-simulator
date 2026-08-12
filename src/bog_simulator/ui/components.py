import tkinter as tk
from tkinter import ttk
from bog_simulator.physics.thermodynamics import to_degC


class LabelInput(ttk.Frame):
    def __init__(self, parent, input_class : tk.Widget | ttk.Widget, input_args = None , label_args = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        self.label = ttk.Label(self, **label_args)
        self.label.grid(row=0, column=0, sticky='we')
        if input_class == ttk.Spinbox:
            self.input = input_class(self, **input_args)
            self.input.grid(row = 0, column = 1, sticky='we')
        else:
            self.input = ttk.Combobox(self, **input_args)
            self.input.grid(row=0, column=1)

    def get(self):
        return self.input.get()

class LabelValue(tk.Frame):
    '''Child class of tk.Frame widget representing label and value for various parameters of the tank'''
    def __init__(self, parent : tk.Widget, textvariable : tk.Variable = None, text : str= None,  *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.text = tk.Label(self, text=text) #label text for example 'Avg. Liquid Temp', 'Avg. Vapor temp' etc.
        self.value = tk.Label(self, textvariable=textvariable, bg='light grey') #A parameter value of the tank
        #place side by side
        self.text.grid(row=0, column=0)
        self.value.grid(row=0, column=1)

class Control_Panel(tk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        #consumption rate control
        self.consumption_rate = tk.DoubleVar()
        self.consumption_rate.set(-parent.lngc_gui.model.cons)
        self.consumption_spinbox = LabelInput(self, ttk.Spinbox, label_args={'text': "Consumption"}, 
                                              input_args={'from_': 0, 'to': 5000, 'increment': 50, 'textvariable':self.consumption_rate})
        self.consumption_spinbox.grid(row = 0, sticky = 'we', padx=5, pady=5)

        #let the user decide the time step
        self.time_step = LabelInput(self, tk.Listbox, input_args={'values': [1, 10, 30, 60, 120]}, label_args={'text': "Time step"})
        self.time_step.grid(row=1, sticky='we', padx=5, pady=5)
        #start simulation by pressing start
        self.start_button = tk.Button(self, text='Start', command = parent.on_start, relief='groove')
        self.start_button.grid(row = 2, sticky = 'we', padx=5, pady=5)
        #pause simulation
        self.pause_button = tk.Button(self, text='Pause', width=50, command=parent.on_pause, relief='groove')
        self.pause_button.grid(row = 3, sticky = 'we', padx=5, pady=5)
        #step button control
        self.step_button = tk.Button(self, text="Step", command=parent.step, relief='groove')
        self.step_button.grid(row = 4, sticky = 'we', padx=5, pady=5)

class Enviromental_GUI(tk.LabelFrame):
    '''Displays various Environmental variables'''
    def __init__(self, parent, enviroment, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        #--init values to be displayed--
        self.date = tk.StringVar()
        self.atm = tk.DoubleVar()
        self.air_temp = tk.DoubleVar()
        self.sea_temp = tk.DoubleVar()
        self.sea_state = tk.IntVar()

        #---set the values----
        self.set_values(enviroment)

        #---init gui of each value---
        self.date_labelVal = LabelValue(self, self.date, "Date")
        self.atm_labelVal = LabelValue(self, self.atm, "Abs. Pressure [mbar]")
        self.air_LabelVal = LabelValue(self, self.air_temp, "Air Temp [deg.C]")
        self.sea_LabelVal = LabelValue(self, self.sea_temp, "Sea Water Temp [deg. C]")
        self.state_LabelVal = LabelValue(self, self.sea_state, "Sea State [BN]")

        #----place them in the grid------
        self.date_labelVal.grid(row=0, column=0, columnspan=2)
        self.atm_labelVal.grid(row=1, column=0)
        self.air_LabelVal.grid(row=1, column=1)
        self.sea_LabelVal.grid(row=2, column=0)
        self.state_LabelVal.grid(row= 2, column= 1)

    def set_values(self, enviroment):
        '''Method to set values in each time step'''
        self.date.set(enviroment.date)
        self.atm.set(round(enviroment.atm, 2))
        self.air_temp.set(round(to_degC(enviroment.T_air), 2))
        self.sea_temp.set(round(to_degC(enviroment.T_sea), 2))
        self.sea_state.set(enviroment.sea_state)