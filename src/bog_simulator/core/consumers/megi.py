from bog_simulator.physics.thermodynamics import megi_consumption

from bog_simulator.physics import per

class MEGI:
    rpm_limit = {
        "min": 45,
        "max": 73
    }
    def __init__(self, **megi_config):
        config = megi_config or {}

        self.type = config["type"]
        self.is_operational = config["is_operational"]
        self.update(config["rpm"])

    def start_engine(self):
        self.is_operational = True

    def stop_engine(self):
        self.is_operational = False

    def update(self, rpm):
        if self.rpm_limit["max"] >= rpm >= self.rpm_limit["min"]:
            self.rpm = rpm
            self.m_gas = self.is_operational * megi_consumption(self.rpm)

#testing
if __name__ == "__main__":
    megi = MEGI(65)
    print(megi.m_gas)