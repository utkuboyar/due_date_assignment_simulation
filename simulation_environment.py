import pandas as pd
import numpy as np
from scipy.stats import expon, uniform, norm

from schedule import JobQueue
from heap import MinHeap


class Environment(object):
    def __init__(self, n, due_date_policy, simulation_time=None, warmup=None):
        self._product_probs = [0.2, 0.3, 0.5]
        self._customer_probs = [0.6, 0.4]
        self.max_order_count = n
    
        self._event_heap = MinHeap()
        self._queue = JobQueue()
        self._due_date_policy = due_date_policy
    
    def initialize(self):
        self._get_order_arrivals()
        self._get_order_products()
        self._get_order_customers()
        self.orders = pd.DataFrame({'arrival': self._order_arrivals, 'product': self._order_prod_types, 
                                    'customer':self._order_customer_types})
        self.orders['quantity'] = self.orders.apply(lambda row: Environment.get_order_quantity(row['product'], row['customer']), axis=1)
    
            
    def _get_order_arrivals(self):
        order_interarrivals = expon.rvs(loc=8, size=self.max_order_count)
        self._order_arrivals = np.cumsum(order_interarrivals)
        
    def _get_order_products(self):
        product_probs_cdf = np.cumsum(self._product_probs)
        self._order_prod_types = self._determine_types(product_probs_cdf)
        
    def _get_order_customers(self):
        customer_probs_cdf = np.cumsum(self._customer_probs)
        self._order_customer_types = self._determine_types(customer_probs_cdf)
        
    def _determine_types(self, cdf):
        rvs = np.random.random(self.max_order_count)

        idx = [rvs < cdf[0]] + \
           [(cdf[i] < rvs) & (rvs < cdf[i+1]) for i in range(len(cdf)-2)] + \
           [cdf[-2] < rvs]

        types = pd.DataFrame(np.array(idx).transpose()).astype('int')
        for col in types.columns:
            types[col] = types[col].map({0:np.nan, 1:int(col)})
        types['type'] = types.apply(lambda row: row.dropna().iloc[0], axis=1)

        return types['type'].to_list()
    
    @staticmethod
    def get_order_quantity(prod_id, customer_id):
        order_quantity_dist = {(0,0):(22, 1.4), (0,1):(26, 1.9),
                               (1,0):(15, 2.8), (1,1):(17, 2.2),
                               (2,0):(25, 4.5), (2,1):(19, 0.9)}
        mean, std = order_quantity_dist[(prod_id, customer_id)]
        return norm.rvs(loc=mean, scale=std, size=1)[0]
    
        
    def arrival(self, order):
        self._new_order = order
        
        if self.machine_is_idle:  
            params = {'expected_completion_time': order._expected_process_time, 
                      'expected_process_time': order._expected_process_time}
            if self._offer_due_date(params):
                self._new_order.update_event_times(self._time_now)
                self.machine_is_idle = False
        
        else:
            self._queue.add_order(order)
            params = self._queue.reschedule(due_date_params=True)
            if self._offer_due_date(params):
                self._queue.set_schedule(confirm=True)
                self._update_events()
            else:
                self._queue.set_schedule(confirm=False)
                
    def cancellation(self, order):
        self._queue.remove_order(order)
        self._queue.reschedule(due_date_params=False)
        self._queue.set_schedule(confirm=True)
        self._update_events()
        
    def start_job(self, job):
        self.machine_is_idle = False
        started_job = self._queue.pop_order()
        if started_job != job:
            raise Exception('Problem', started_job, job)
    
    def finish_job(self):
        self.machine_is_idle = True
        
    def _order_due_date(self, params):
        params['expected_completion_time'] += self._time_now
        params['time_now'] = self._time_now
        due_date = self._due_date_policy()
        return self._new_order.due_date_accepted(due_date)
            
    def _update_events(self):
        sequence = self._order_queue.get_sequence()
        t = self._time_now
        for order in sequence:
            t = order.update_event_times(t)
            
    def run(self):
        while not self.events_heap.is_empty:
            event = self.events_heap.get_imminent_event()
            self.time = event.time
            event.occur()
