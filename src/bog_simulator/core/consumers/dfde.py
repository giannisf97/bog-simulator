from bog_simulator.physics.thermodynamics import dfde_consumption
from bog_simulator.physics import per

class DFDE:
    def __init__(self, type, output):
        self.type = type
        self.update(output)

    def update(self, output):
        self.output = output
        m_gas_new = dfde_consumption(self.type, output)
        self.m_gas = per.sec(m_gas_new)


if __name__ == '__main__':
    dfde = DFDE("W8L34DF", 2600)
    print(per.hour(dfde.m_gas))