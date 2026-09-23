"""Reusable graphical widgets for the BOG Simulator user interface."""

from typing import Any, Callable, TYPE_CHECKING

import tkinter as tk
from tkinter import ttk
from bog_simulator.physics.thermodynamics import to_degC

if TYPE_CHECKING:
    from bog_simulator.core.environment import Environment

class LabelInput(ttk.Frame):
    """Compound widget combining a text label with an input entry (Spinbox or Combobox)."""
    input: ttk.Spinbox | ttk.Combobox

    def __init__(
        self,
        parent: tk.Misc,
        input_class: type[tk.Widget | ttk.Widget],
        input_args: dict[str, Any] | None = None,
        label_args: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Initializes a LabelInput compound widget.

        Args:
            parent: Parent Tkinter widget.
            input_class: Input widget class (e.g. ttk.Spinbox or ttk.Combobox).
            input_args (dict): Keyword arguments passed to the input widget.
            label_args (dict): Keyword arguments passed to the label widget.
        """
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

    def get(self) -> str:
        """Retrieves the current value from the embedded input widget."""
        return str(self.input.get())

class LabelValue(tk.Frame):
    """Compound widget displaying a static label text alongside a dynamic variable value."""
    def __init__(self, parent: tk.Misc, textvariable: tk.Variable | None = None, text: str = "", *args: Any, **kwargs: Any) -> None:
        """Initializes a LabelValue widget.

        Args:
            parent (tk.Misc): Parent container.
            textvariable (tk.Variable): Tkinter variable bound to the numerical display.
            text (str): Descriptive label text.
        """
        super().__init__(parent, *args, **kwargs)
        self.text = tk.Label(self, text=text) #label text for example 'Avg. Liquid Temp', 'Avg. Vapor temp' etc.
        val_kwargs: dict[str, Any] = {"bg": "light grey"}
        if textvariable is not None:
            val_kwargs["textvariable"] = textvariable
        self.value = tk.Label(self, **val_kwargs) #A parameter value of the tank
        #place side by side
        self.text.grid(row=0, column=0)
        self.value.grid(row=0, column=1)


class Enviromental_GUI(tk.LabelFrame):
    """HUD frame displaying current voyage environmental and oceanographic conditions."""
    def __init__(self, parent: tk.Misc, enviroment: "Environment", *args: Any, **kwargs: Any) -> None:
        """Initializes the Environmental_GUI HUD panel.

        Args:
            parent: Parent Tkinter widget.
            enviroment (Environment): Environment model providing weather telemetry.
        """
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

    def set_values(self, enviroment: "Environment") -> None:
        """Updates all displayed weather variables from the Environment instance."""
        self.date.set(enviroment.date)
        self.atm.set(round(enviroment.atm, 2))
        self.air_temp.set(round(to_degC(enviroment.T_air), 2))
        self.sea_temp.set(round(to_degC(enviroment.T_sea), 2))
        self.sea_state.set(enviroment.sea_state)

class Options(tk.Frame):
    """Control frame housing the Start, Pause, and Step simulation execution buttons."""
    def __init__(
        self,
        parent: tk.Misc,
        start: Callable[[tk.Button], None],
        pause: Callable[[tk.Button], None],
        step: Callable[[], None],
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Initializes the simulation playback controls.

        Args:
            parent: Parent container.
            start (callable): Start simulation callback.
            pause (callable): Pause simulation callback.
            step (callable): Single-step advance callback.
        """
        super().__init__(parent, *args, **kwargs)
        #start simulation by pressing start
        self.start_button = tk.Button(self, text='Start', width=20, relief='groove', command= lambda: start(self.start_button))
        self.start_button.grid(row = 1, padx=5, pady=5)
        #pause simulation
        self.pause_button = tk.Button(self, text='Pause', command= lambda: pause(self.start_button), relief='groove')
        self.pause_button.grid(row = 2, padx=5, pady=5, sticky='we')
        #step button control
        self.step_button = tk.Button(self, text="Step", command= step, relief='groove')
        self.step_button.grid(row = 3, padx=5, pady=5, sticky='we')