import matplotlib.pyplot as plt

class Statistics:
    def __init__(self, press, consumption):
        self.total_time = 0
        self.press = []
        self.consumption = []
        self.time = []
        self.fetch_data(press, consumption, self.total_time)

    def fetch_data(self, press, consumption, dt):
        self.total_time += dt
        self.press.append(press)
        self.consumption.append(-consumption)
        self.time.append(self.total_time/3600) # in hours

    def show_plot(self):
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