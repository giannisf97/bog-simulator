from bog_simulator.physics import per

class GCU:
    '''Models Gas Combustion Unit'''
    capacity = {"min": 0, "max": 3300}
    def __init__(self, **gcu_parameters):
        config = gcu_parameters or {}
        self.is_operational = config["is_operational"]
        self.update(config["rate"]) 

    def start_gcu(self):
        self.is_operational = True

    def stop_gcu(self):
        self.is_operational = False

    def update(self, rate):
        if self.capacity["max"] >= rate >= self.capacity["min"]:
            m_gas_new = per.sec(rate)
            self.m_gas = m_gas_new * self.is_operational