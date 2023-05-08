import pandas as pd
import numpy as np

from product import Product
from customer import Customer

from events import JobStart, JobFinish, OrderCancelation, OrderArrival

class Order(object):
    def __init__(self, arrival_time, product_type, customer_type, quantity, dispatching_rule, env, order_id):
        self._environment = env
        self._id = order_id
        
        self._arrival_time = np.round(arrival_time).astype(int)
        self._event_arrival = OrderArrival(self._arrival_time, self)
        self._quantity = np.round(quantity).astype(int)
        self._product = Product(product_type)
        self._customer = Customer(customer_type)
        
        self._start_time = None
        self._finish_time = None
        
        #unit process time is calculated with (expected p.t. * k)
        self._process_time = self._product.get_unit_process_time() * quantity
        
        self._expected_process_time = np.round(self._product.get_expected_unit_process_time() * quantity).astype(int)
        self._weight = np.round(quantity * self._product.get_unit_profit() * self._customer.get_reliability() * self._customer.get_weight_coefficient()).astype(int)
        
        self._dispatching_rule = dispatching_rule
        
        cancels_after = self._customer.cancels_order()
        if cancels_after is None:
            self._cancelation_time = None
        else:
            #if  self._start_time is not None and self._start_time > (self._arrival_time + cancels_after):
            self._cancelation_time = self._arrival_time + cancels_after
            self._event_cancelation = OrderCancelation(self._cancelation_time, self)
#             else:
#                 self._cancelation_time = None
#             # to detect the cancels_after time
#             if self._id in [547,661,671,700]:
#                 print(cancels_after,' ', self._id, ' ',self._cancelation_time )
            
    def due_date_accepted(self, due_date, t) -> bool:
        if self._customer.rejects_due_date((due_date - t)/self.get_expected_process_time()):
            #print('due date rejected', self._id)
            self._due_date = None
            self.prevent_cancelation()
            return False
        else:
            #print('due date accepted', self._id)
            self._due_date = due_date
            self._event_job_start = JobStart(None, self) 
            self._event_job_finish = JobFinish(None, self)
            return True
        
    def update_event_times(self, t) -> float:
        self._event_job_start.update_time(t)
        self._event_job_finish.update_time(t + self._process_time)
        #print('here update_event_times', t, t + self._process_time)
        return t + self._process_time
    
#     def get_stats(self):
#         # order's ---> id + customer + product + quantity + weight + arrival
#                     # + dd offered + dd accepted + start + cancelled + finish +
#         stats_list = [self._id, self._customer._type, self._product._type, self._quantity, self.get_weight(), 
#                       self._arrival_time, self.due_date_accepted(), self._start_time, self._cancelation_time, 
#                       self._finish_time]
#         return [stats_list]
    
    def get_expected_process_time(self):
        return self._expected_process_time
    
    def get_weight(self):
        return self._weight
    
    def cancel(self) -> None:
        self._event_job_start.remove()
        self._event_job_finish.remove()
        
    def prevent_cancelation(self) -> None:
        if self._cancelation_time is not None:
            self._cancelation_time = None
            self._event_cancelation.remove()
            
    def __lt__(self, other_order):
        if self._dispatching_rule == 'FIFO':
             return self._arrival_time < other_order._arrival_time
        if self._dispatching_rule == 'SPT':
             return self._expected_process_time < other_order._expected_process_time
        if self._dispatching_rule == 'BWF':
             return -self._weight < -other_order._weight
            
    def __repr__(self):
        return f'{self._id}'
        info = {'arrival': self._arrival_time, 'exp_process_time': self._expected_process_time, 'weight': self._weight[0]}
        stringified = ""
        for k, v in info.items():
            stringified += f"{k}: {v}\n"
        return f"({stringified})"