from scipy.stats import uniform

class Product(object):
    def __init__(self, prod_type):
        """
        types: 0, 1, 2 
        """
        self._type = prod_type
        
        unit_process_times = {0:[0.4, 0.2],
                              1:[0.5, 0.1],
                              2:[0.7, 0.4]}
        self._unit_process_time = unit_process_times[prod_type]
        
        unit_profits = {0: 3, 1: 2.5, 2: 1.8}
        self._unit_profit = unit_profits[prod_type]
        
    def get_type(self):
        return self._type

    def get_unit_process_time(self):
        loc, scale = self._unit_process_time
        return uniform.rvs(loc=loc, scale=scale, size=1)
    
    def get_expected_unit_process_time(self):
        loc, scale = self._unit_process_time
        return loc + scale/2
    
    def get_unit_profit(self):
        return self._unit_profit