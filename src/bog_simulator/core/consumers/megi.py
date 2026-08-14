from bog_simulator.physics.thermodynamics import megi_consumption

class MEGI:
    def __init__(self, rpm):
        self.update(rpm)

    def update(self, rpm):
        self.rpm = rpm
        self.m_gas = megi_consumption(self.rpm)

#testing
if __name__ == "__main__":
    megi = MEGI(65)
    print(megi.m_gas)