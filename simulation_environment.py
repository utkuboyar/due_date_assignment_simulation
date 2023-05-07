import pandas as pd
import numpy as np
from scipy.stats import norm

from schedule import JobQueue
from heap import MinHeap
from order import Order

from utils.env_variables import ProductParameters, CustomerParameters, OrderParameters


class Environment(object):
    def __init__(self, n, due_date_policy, dispatching_rule, simulation_time=None, warmup=None):
        self._product_probs = ProductParameters.get_probs()
        self._customer_probs = CustomerParameters.get_probs()
        self.max_order_count = n
    
        self.event_heap = MinHeap()
        self._queue = JobQueue(dispatching_rule)

        self._due_date_policy = due_date_policy
        self._dispatching_rule = dispatching_rule
        
        #if self._dispatching_rule.policy == TWK:
          #  self._dispatching_rule._define_env(self)
    
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
        order_interarrivals = OrderParameters.get_interarrivals(size=self.max_order_count)
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
        order_quantity_dist = OrderParameters.get_quantity_dist()

        mean, std = order_quantity_dist[(prod_id, customer_id)]
        return np.round(norm.rvs(loc=mean, scale=std, size=1)[0], 0)
    
    def _get_expected_remaining_process_time(self):
        if self._in_process is None:
            return 0
        else:
            return max(0, self._in_process._event_job_start.time + self._in_process._expected_process_time - self._time_now)
        
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

            t = self._get_expected_remaining_process_time()

            params = self._queue.reschedule(due_date_params=True, expected_remaining_time_on_machine=t, time_now=self._time_now)
            if self._offer_due_date(params):
                self._queue.set_schedule(confirm=True)
                self._update_events()
            else:
                self._queue.set_schedule(confirm=False)
                
    def cancelation(self, order):
        # process ediliyorsa cancel etme
        self._queue.remove_order(order)

        t = self._get_expected_remaining_process_time()

        self._queue.reschedule(due_date_params=False, expected_remaining_time_on_machine=t, time_now = self._time_now)
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
        self._dispatching_rule._add_order(self._in_process)
        self._in_process = None
        
    def _offer_due_date(self, params):
        #if self._in_process is None:
        t = self._time_now + self._get_expected_remaining_process_time()
        
        # params['expected_completion_time'] += self._time_now
        # params['time_now'] = self._time_now
        params['expected_completion_time'] += t
        params['time_now'] = t
        due_date = np.round(self._due_date_policy(**params)).astype(int)
        return self._new_order.due_date_accepted(due_date, self._time_now)
            
    def _update_events(self):
        sequence = self._queue.get_sequence()
        # t = self._time_now # + o an makinedeki işin remaining zamanı
        if self._in_process is None:
            t = self._time_now + 1e-13
        else:
            t = self._in_process._event_job_finish.time + 1e-13
        for order in reversed(sequence):
            # print('***', t)
            t = order.update_event_times(t)
            
    def get_stats(self, order):
        return order._id, order._customer._type, order._product._type, order._quantity, order.get_weight(), order._arrival_time, order._due_date, order._start_time, order._cancelation_time, order._finish_time
    
    def show_stats(self):
        stats_df = pd.DataFrame({'order':self._orders})

        stats = stats_df['order'].apply(self.get_stats)
        stats_df[['ID', 'customer type', 'product type', 'quantity','weight','arrival', 'due date','start','cancelled', 'finish']] = pd.DataFrame(stats.tolist())
        stats_df  = stats_df.drop('order', axis=1)
        stats_df['weight'] = stats_df['weight'].str[0].astype(int)
        
        #START'TAN SONRA CANCEL EDİLENLERİN CANCELLED TİME'LARINI NONE'A ÇEVİR
        mask = (stats_df['start'].notna()) & (stats_df['cancelled'].notna()) & (stats_df['start'] < stats_df['cancelled'])
        #print('cancelled after started being processed:', stats_df.loc[mask])
        stats_df.loc[mask, 'cancelled'] = None
        #print(stats_df.loc[mask, 'cancelled'])
        
        
        #IF FINISH AND DUE DATE ARE NOT NONE -> SUBTRACT AND FIND TARDINESS
        mask_tardy1= (stats_df['finish'].notna() & stats_df['finish'] > stats_df['due date'])
        print(stats_df.loc[mask_tardy1])
#         mask_tardy2 = (stats_df.loc[mask_tardy1, 'finish'] <=  stats_df.loc[mask_tardy1, 'due date'])
#         stats_df.loc[mask_tardy2, 'finish'])
        #stats_df[mask_tardy, 'tardiness length'] = stats_df['finish'] - stats_df['due date']
        

        
       
        #print(stats_df.loc[669:673])
#         stats_df.loc[mask, 'cancelled'] = None

        # NEDEN ÇALIŞMADIĞINI ANLAMADIĞIM KOD: amacı start column'da None olmayan değerleri float -> int yapmak.
#         nan_indexes = stats_df[stats_df['start'].isna()].index
#         not_nan_indexes = stats_df.index.difference(nan_indexes)
#         stats_df.loc[not_nan_indexes, 'start'] = stats_df.loc[not_nan_indexes, 'start'].astype(int)
#         print( stats_df.loc[not_nan_indexes, 'start'])

        print(stats_df.dtypes)
        return stats_df[200:230]

    def run(self, log=False):
        self._time_now = 0
        while not self.event_heap.is_empty():
            if log:
                print('--------')
            #print('here')
            event, time = self.event_heap.get_imminent_event()
            self._time_now = time
            event.occur()
            
            if log:
                print(event)
                print('machine after event')
                if self._in_process is not None:
                    print(self._in_process._id)
                else:
                    print('idle')
                print('queue after event')
                print([job._id for job in reversed(self._queue._sequence)])
                #print([job._expected_process_time for job in reversed(self._queue._sequence)])
                print()
                print('--------')
                print()    