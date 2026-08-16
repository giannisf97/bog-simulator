class Consumers:
    def __init__(self, genSets: list, mainEngines: list, gcu):
        self.gensets = genSets
        self.mainEngines = mainEngines
        self.gcu = gcu
    
    def total_consumption(self):
        total_cons = 0
        for genset in self.gensets:
            total_cons += genset.m_gas
        for mainEngine in self.mainEngines:
            total_cons += mainEngine.m_gas
        total_cons += self.gcu.m_gas
        return total_cons