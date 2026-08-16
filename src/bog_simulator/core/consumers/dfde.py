from bog_simulator.physics.thermodynamics import dfde_consumption
from bog_simulator.physics import per

class DFDE:
    output_limits = {
        "W8L34DF": {"min": 1400, "max": 4000},
        "W6L34DF": {"min": 1000, "max": 3000}
    }

    def __init__(self, **genset_params):
        config = genset_params or {}

        self.type = config["type"]

        self.max_output = self.output_limits[self.type]["max"]
        self.min_output = self.output_limits[self.type]["min"]

        self.is_operational = config["is_operating"]
        self.update(config["output"])

    def start_dg(self):
        self.is_operational = True

    def stop_dg(self):
        self.is_operational = False

    def update(self, output):
        if  self.min_output <= output <= self.max_output: 
            self.output = output
            m_gas_new = self.is_operational * dfde_consumption(self.type, output)
            self.m_gas = per.sec(m_gas_new)



if __name__ == '__main__':
    generator_parameters = {
        "type": 'W8L34DF',
        "is_operating": False,
        "output": 3500
    }
    dfde = DFDE(**generator_parameters)
    print(per.hour(dfde.m_gas))