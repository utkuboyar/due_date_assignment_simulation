from scipy.stats import uniform, expon
import numpy as np

from helpers import Rounder

class ProductParameters(object):
    @staticmethod
    def get_params(prod_id):
        unit_process_times = {0:[0.4, 0.2],
                            1:[0.5, 0.1],
                            2:[0.7, 0.4]}
        unit_profits = {0: 3, 1: 2.5, 2: 1.8}
        return unit_process_times[prod_id], unit_profits[prod_id]
    
    @staticmethod
    def get_uncertainty_constant():
        return uniform.rvs(loc=0.5, scale=1, size=1)[0]
    
    @staticmethod
    def get_probs():
        return [0.2, 0.3, 0.5]
    
class CustomerParameters(object):
    @staticmethod
    def get_params(customer_id):
        reliabilities = {0: 0.97, 1: 0.9}
        rejection_coefficients = {0: 0.03, 1: 0.05}  # sayılar şimdilik sallamasyon
        weight_coefficients = {0: [11, 1.2], 1: [20, 3.3]} # sayılar şimdilik sallamasyon
        return reliabilities[customer_id], rejection_coefficients[customer_id], weight_coefficients[customer_id]
    
    @staticmethod
    def get_cancelation_time(customer_id):
        cancelation_rates = {0: 5, 1: 7}
        rate = cancelation_rates[customer_id]
        return Rounder.round(expon.rvs(loc=rate, size=1))[0]

    @staticmethod
    def get_probs():
        return [0.6, 0.4]
    
class OrderParameters(object):
    @staticmethod
    def get_quantity_dist():
        return {(0,0):(22, 1.4), (0,1):(26, 1.9),
                (1,0):(15, 2.8), (1,1):(17, 2.2),
                (2,0):(25, 4.5), (2,1):(19, 0.9)}
    
    @staticmethod
    def get_interarrivals(size):
        rate = 3
        return Rounder.round(expon.rvs(loc=rate, size=size))


