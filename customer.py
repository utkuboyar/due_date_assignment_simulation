import numpy as np
from scipy.stats import norm
from utils.env_variables import CustomerParameters


class Customer(object):
    def __init__(self, customer_type):
        """
        types: 0, 1 
        """
        self._type = customer_type
        self._reliability, self._rejection_coefficient, self._weight_coefficient = CustomerParameters.get_params(customer_type)

        self._cancelation_time = None
        
    def get_type(self):
        return self._type
    
    def cancels_order(self) -> int:
        if np.random.random() > self._reliability:
            self._cancelation_time = CustomerParameters.get_cancelation_time(self._type)
        return self._cancelation_time
        
#     def get_cancelation_time(self):
#         return self._cancelation_time
    
    def get_reliability(self):
        return self._reliability
    
    def rejects_due_date(self, due_date) -> bool:
        return np.random.random() < 1-np.exp(-self._rejection_coefficient*due_date)
    
    def get_weight_coefficient(self) -> float:
        mean, std = self._weight_coefficient
        return norm.rvs(loc=mean, scale=std, size=1)