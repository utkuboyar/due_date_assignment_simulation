import pandas as pd
import numpy as np

from product import Product
from customer import Customer

class Order(object):
    def __init__(self, arrival_time, product_type, customer_type, quantity, dispatching_rule):
        self._arrival_time = arrival_time
        self._quantity = quantity
        self._product = Product(product_type)
        self._customer = Customer(customer_type)
        
        self._process_time = self._product.get_unit_process_time() * quantity
        self._expected_process_time = self._product.get_expected_unit_process_time() * quantity
        self._weight = quantity * self._product.get_unit_profit() * self._customer.get_reliability() * self._customer.get_weight_coefficient()
        
        self._dispatching_rule = dispatching_rule
        
    def offer_due_date(self, due_date):
        if self._customer.rejects_due_date(due_date):
            pass
        else:
            self._due_date = due_date
            self._is_canceled = self._customer.cancels_order()
            if self._is_canceled:
                self._cancelation_time = self.arrival_time + self._customer.get_cancelation_time()
            
    def __lt__(self, other_order):
        if self._dispatching_rule == 'FIFO':
             return self._arrival_time < other_order._arrival_time
        if self._dispatching_rule == 'SPT':
             return self._expected_process_time < other_order._expected_process_time
        if self._dispatching_rule == 'BWF':
             return -self._weight < -other_order._weight
            
    def __repr__(self):
        info = {'arrival': self._arrival_time, 'exp_process_time': self._expected_process_time, 'weight': self._weight[0]}
        stringified = ""
        for k, v in info.items():
            stringified += f"{k}: {v}\n"
        return f"({stringified})"