class GCU:
    '''Models Gas Combustion Unit'''
    def __init__(self, rate: int):
        self.rate = rate

    def update(self, rate):
        if 3100>= rate >= 0:
            self.rate = rate