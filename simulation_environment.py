import pandas as pd
import numpy as np
from scipy.stats import expon, uniform, norm

from schedule import JobQueue
from heap import MinHeap
from order import Order


class Environment(object):
    def __init__(self, n, due_date_policy, dispatching_rule, simulation_time=None, warmup=None):
        self._product_probs = [0.2, 0.3, 0.5]
        self._customer_probs = [0.6, 0.4]
        self.max_order_count = n
    
        self.event_heap = MinHeap()
        self._queue = JobQueue(dispatching_rule)

        self._due_date_policy = due_date_policy
        self._dispatching_rule = dispatching_rule
    
    def initialize(self) -> None:
        self.machine_is_idle = True
        self._in_process = None
        
        self._get_order_arrivals()
        self._get_order_products()
        self._get_order_customers()
        self.orders_df = pd.DataFrame({'arrival': self._order_arrivals, 'product': self._order_prod_types, 
                                    'customer':self._order_customer_types})
        self.orders_df['quantity'] = self.orders_df.apply(lambda row: Environment.get_order_quantity(row['product'], row['customer']), axis=1)

        self._orders = {}
        for i, row in self.orders_df.iterrows():
            self._orders[i] = Order(arrival_time=row['arrival'], product_type=row['product'], customer_type=row['customer'], 
                    quantity=row['quantity'], dispatching_rule=self._dispatching_rule, env=self, order_id=i)
                  
    def _get_order_arrivals(self) -> None:
        """
        calculates order arrival times
        using random exponential interarrivals
        """
        order_interarrivals = np.round(expon.rvs(loc=8, size=self.max_order_count)).astype(int)
        self._order_arrivals = np.cumsum(order_interarrivals)
        
    def _get_order_products(self) -> None:
        """
        assigns order products randomly according to
        the predefined product probabilities
        """
        product_probs_cdf = np.cumsum(self._product_probs)
        self._order_prod_types = self._determine_types(product_probs_cdf)
        
    def _get_order_customers(self) -> None:
        """
        assigns order customers randomly according to
        the predefined product probabilities
        """
        customer_probs_cdf = np.cumsum(self._customer_probs)
        self._order_customer_types = self._determine_types(customer_probs_cdf)
        
    def _determine_types(self, cdf) -> list:
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
    def get_order_quantity(prod_id, customer_id) -> int:
        # bu değişebilir
        order_quantity_dist = {(0,0):(22, 1.4), (0,1):(26, 1.9),
                               (1,0):(15, 2.8), (1,1):(17, 2.2),
                               (2,0):(25, 4.5), (2,1):(19, 0.9)}
        mean, std = order_quantity_dist[(prod_id, customer_id)]
        return np.round(norm.rvs(loc=mean, scale=std, size=1)[0], 0)
    
        
    def arrival(self, order):
        self._new_order = order
        
        # if machine is idle, offer due date without rescheduling
        # if accepted, process the new order
        if self.machine_is_idle:
            params = {'expected_completion_time': order._expected_process_time, 
                      'expected_process_time': order._expected_process_time}
            if self._offer_due_date(params):
                self._new_order.update_event_times(self._time_now)
                self.machine_is_idle = False
        
        # if machine is busy, firstly reschedule the jobs and then offer due date
        else:
            self._queue.add_order(order)

            if self._in_process is None:
                t = 0
            else:
                t = self._in_process._event_job_start.time + self._in_process._event_job_finish.order._expected_process_time - self._time_now

            params = self._queue.reschedule(due_date_params=True, expected_remaining_time_on_machine=t)
            if self._offer_due_date(params):
                self._queue.set_schedule(confirm=True)
                self._update_events()
            else:
                self._queue.set_schedule(confirm=False)
                
    def cancelation(self, order):
        # process ediliyorsa cancel etme
        self._queue.remove_order(order)

        if self._in_process is None:
            t = 0
        else:
            t = self._in_process._event_job_start.time + self._in_process._event_job_finish.order._expected_process_time - self._time_now
        self._queue.reschedule(due_date_params=False, expected_remaining_time_on_machine=t)
        self._queue.set_schedule(confirm=True)
        self._update_events()
        
    def start_job(self, job):
        self.machine_is_idle = False
        self._in_process = job
        started_job = self._queue.pop_order()
        if (started_job is not None) and (started_job != job):
            # sıkıntı, detaylandıralım
            raise Exception('Problem', started_job._id, job._id)
    
    def finish_job(self):
        self.machine_is_idle = True
        self._in_process = None
        
    def _offer_due_date(self, params):
        if self._in_process is None:
            t = self._time_now
        else:
            t = self._in_process._event_job_finish.time
        # params['expected_completion_time'] += self._time_now
        # params['time_now'] = self._time_now
        params['expected_completion_time'] += t
        params['time_now'] = t
        due_date = self._due_date_policy(**params)
        return self._new_order.due_date_accepted(due_date, self._time_now)
            
    def _update_events(self):
        sequence = self._queue.get_sequence()
        # t = self._time_now # + o an makinedeki işin remaining zamanı
        if self._in_process is None:
            t = self._time_now + 1e-13
        else:
            t = self._in_process._event_job_finish.time + 1e-13
        for order in reversed(sequence):
            print('***', t)
            t = order.update_event_times(t)
            
    def run(self):
#         self.initialize()
        self._time_now = 0
        while not self.event_heap.is_empty():
            #print('here')
            event, time = self.event_heap.get_imminent_event()
            print(event)
            self._time_now = time
            event.occur()
            print('machine after event')
            if self._in_process is not None:
                print(self._in_process._id)
            else:
                print('idle')
            print('queue after event')
            print([job._id for job in reversed(self._queue._sequence)])
            print([job._expected_process_time for job in reversed(self._queue._sequence)])
            print()
            print('--------')
            print()