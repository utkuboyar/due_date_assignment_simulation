import numpy as np
from scipy.stats import expon, norm

class Customer(object):
    def __init__(self, customer_type):
        """
        types: 0, 1 
        """
        self._type = customer_type
        
        reliabilities = {0: 0.97, 1:0.9}
        self._reliability = reliabilities[customer_type]
        
        rejection_coefficients = {0: 0.5, 1: 0.7}  # sayılar şimdilik sallamasyon
        self._rejection_coefficient = rejection_coefficients[customer_type]
        
        weight_coefficients = {0: [11, 1.2], 1: [20, 3.3]} # sayılar şimdilik sallamasyon
        self._weight_coefficient = weight_coefficients[customer_type]
        
        self._cancelation_time = None
        
    def get_type(self):
        return self._type
    
    def cancels_order(self):
        if np.random.random() > self._reliability:
            self._cancelation_time = expon.rvs(size=1)
            return True
        else:
            return False
        
    def get_cancelation_time(self):
        return self._cancelation_time
    
    def get_reliability(self):
        return self._reliability
    
    def rejects_due_date(self, due_date):
        return np.random.random < 1-np.exp(-self._rejection_coefficient*due_date)
    
    def get_weight_coefficient(self):
        mean, std = self._weight_coefficient
        return norm.rvs(loc=mean, scale=std, size=1)