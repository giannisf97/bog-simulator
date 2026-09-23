"""Voyage telemetry statistics and plotting module."""

import matplotlib.pyplot as plt

from bog_simulator.physics import per

class Statistics:
    """Collects and plots time-series simulation variables for post-voyage analysis.

    Tracks mean vapor header pressure [mbar] and total fuel gas consumption [kg/h]
    over the duration of the simulated voyage.

    Attributes:
        total_time (int): Cumulative simulation elapsed time [s].
        press (list[float]): Time-series history of vapor header pressures [mbar].
        consumption (list[float]): Time-series history of total consumption rates [kg/h].
        time (list[float]): Simulation timeline in elapsed hours [h].
    """
    total_time: int | float
    press: list[float]
    consumption: list[float]
    time: list[float]

    def __init__(self, press: float, consumption: float) -> None:
        """Initializes the Statistics time-series recorder.

        Args:
            press (float): Initial vapor header pressure [mbar].
            consumption (float): Initial fuel gas consumption [kg/s].
        """
        self.total_time = 0
        self.press = []
        self.consumption = []
        self.time = []
        self.fetch_data(press, consumption, self.total_time)

    def fetch_data(self, press: float, consumption: float, dt: int | float) -> None:
        """Appends a new time-step telemetry snapshot to the historical records.

        Args:
            press (float): Instantaneous vapor header pressure [mbar].
            consumption (float): Instantaneous fuel gas consumption rate [kg/s].
            dt (int): Time increment in seconds.
        """
        self.total_time += dt
        self.press.append(press)
        self.consumption.append(per.hour(consumption))
        self.time.append(self.total_time/3600) # in hours

    def show_plot(self) -> None:
        """Renders an interactive dual-axis Matplotlib chart of the voyage findings.

        Plots Tank Pressure [mbar] on the left axis and Total Gas Consumption [kg/h]
        on the right axis against Voyage Elapsed Time [hours].
        """
        self.fig, ax1 = plt.subplots()
        color = 'tab:red'
        ax1.set_title("Tank Pressure & Consumption")
        ax1.plot(self.time, self.press, label= "Tank Pressure [mbar]", color= color)
        ax1.set_ylabel('Tank Pressure (mBar)', color=color)
        ax1.tick_params(axis='y', labelcolor= color)
        
        ax1.set_xlabel('Time (H)')

        color = 'tab:blue'
        ax2 = ax1.twinx()
        ax2.plot(self.time, self.consumption, label = "Consumption [kg/h]")
        ax2.set_ylabel('Consumption (kg/h)', color=color)
        ax2.tick_params(axis='y', labelcolor= color)
        
        self.fig.tight_layout()
        plt.show()