from utils.env_variables import ProductParameters
from utils.helpers import Rounder

class Product(object):
    def __init__(self, prod_type):
        """
        types: 0, 1, 2 
        """
        self._type = prod_type
        self._unit_process_time, self._unit_profit = ProductParameters.get_params(self._type)
        
    def get_type(self):
        return self._type

    def get_unit_process_time(self) -> float:
        return Rounder.round(self.get_expected_unit_process_time() * ProductParameters.get_uncertainty_multiplier())
        
    def get_expected_unit_process_time(self) -> float:
        loc, scale = self._unit_process_time
        return loc + scale/2
    
    def get_unit_profit(self) -> float:
        return self._unit_profit