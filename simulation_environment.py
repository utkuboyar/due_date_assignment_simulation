import pandas as pd
import numpy as np
from scipy.stats import norm
import multiprocessing 

from schedule import JobQueue
from heap import MinHeap
from due_date_policies import CON, SLK, TWK
from order import Order

from utils.env_variables import ProductParameters, CustomerParameters, OrderParameters

class Simulation(object):
    def __init__(self, seed, **kwargs):
        self.seed = seed
        self.kwargs = kwargs

    @staticmethod
    def run_environment(config):
        n, due_date_policy_params, dispatching_rule = config['n'], config['due_date_policy_params'], config['dispatching_rule']
        simulation_time, warmup = None, None
        if 'simulation_time' in config:
            simulation_time = config['simulation_time']
        if 'warmup' in config:
            warmup = config['warmup']
        seed = config['seed']

        env = Environment(n=n, due_date_policy_params=due_date_policy_params, dispatching_rule=dispatching_rule, 
                          seed=seed, simulation_time=simulation_time, warmup=warmup)
        env.run_once()
        stats = env.collect_stats()
        return stats

    def run(self, n_sim, num_cores=-1) -> dict:
        stat_names = {'tardiness_proportion':[], 'rejection_proportion':[],
                       'weighted_tardiness_proportion':[], 'weighted_rejection_proportion':[],
                       'avg_tardiness_amount':[], 'weighted_avg_tardiness_amount':[]}     
        
        if num_cores <= 0:
            self._num_cores = multiprocessing.cpu_count()
        else:
            self._num_cores = min(multiprocessing.cpu_count(), num_cores)

        np.random.seed(self.seed)
        self.env_seeds = np.random.randint(0, n_sim*100000, n_sim)

        args_list = []
        for seed in self.env_seeds:
            config = self.kwargs.copy()
            config['seed'] = seed
            args_list.append(config)

        with multiprocessing.Pool(processes=self._num_cores) as pool:
            results = pool.map(Simulation.run_environment, args_list)
        
        stats = {name:[] for name in stat_names}
        for result in results:
            for i, name in enumerate(stat_names):
                stats[name].append(result[i])
        self._stats_df = pd.DataFrame(stats)
        return self._stats_df.mean().to_dict()
            
        # for i in range(n_sim):
        #     print(f'round {i}')
        #     self.run_once(log=log)
        #     self._collect_stats()

        # self._stats_df = pd.DataFrame(self._stats)
        # return self._stats_df



class Environment(object):
    def __init__(self, n, due_date_policy_params, dispatching_rule, seed, simulation_time=None, warmup=None):
        self._product_probs = ProductParameters.get_probs()
        self._customer_probs = CustomerParameters.get_probs()
        self.max_order_count = n
        self._due_date_policy = due_date_policy_params['policy']
        self._due_date_policy_params = due_date_policy_params
        del self._due_date_policy_params['policy']
        self._dispatching_rule = dispatching_rule
        self.seed = seed
        self.simulation_time = simulation_time
        self.warmup = warmup/2
    
    def _initialize(self) -> None:
        np.random.seed(self.seed)
        self.event_heap = MinHeap()
        self._queue = JobQueue(self._dispatching_rule)
        
        if self._due_date_policy == 'CON':
            self._due_date_assigner = CON(**self._due_date_policy_params)
        if self._due_date_policy == 'SLK':
            self._due_date_assigner = SLK(**self._due_date_policy_params)
        if self._due_date_policy == 'TWK':
            self._due_date_assigner = TWK(**self._due_date_policy_params)

        self._time_now = 0

        self.machine_is_idle = True
        self._in_process = None
        
        self._get_order_arrivals()
        self._get_order_products()
        self._get_order_customers()
        self.orders_df = pd.DataFrame({'id':[i for i in range(self.max_order_count)] ,'arrival': self._order_arrivals, 
                                       'product': self._order_prod_types, 'customer':self._order_customer_types})
        self.orders_df['quantity'] = self.orders_df.apply(lambda row: Environment.get_order_quantity(row['product'], row['customer']), axis=1)
        self.orders_df['quantity'] = self.orders_df['quantity'].apply(lambda x: max(x, 1))

        self._orders = {}
        # for i, row in self.orders_df.iterrows():
        #     self._orders[i] = Order(arrival_time=row['arrival'], product_type=row['product'], customer_type=row['customer'], 
        #             quantity=row['quantity'], dispatching_rule=self._dispatching_rule, env=self, order_id=i)
        orders = self.orders_df.apply(Environment.create_order, axis=1, dispatching_rule=self._dispatching_rule, env=self)
        self._orders = {i: order for i, order in enumerate(orders)}

    @staticmethod      
    def create_order(row, dispatching_rule, env):
        return Order(arrival_time=row['arrival'], product_type=row['product'], customer_type=row['customer'], 
                    quantity=row['quantity'], dispatching_rule=dispatching_rule, env=env, order_id=row['id'])
    
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
        if self._due_date_policy == 'TWK':
            self._due_date_assigner._add_order(self._in_process)
        self._in_process = None
        
    def _offer_due_date(self, params):
        #if self._in_process is None:
        t = self._time_now + self._get_expected_remaining_process_time()
        
        # params['expected_completion_time'] += self._time_now
        # params['time_now'] = self._time_now
        params['expected_completion_time'] += t
        params['time_now'] = t
        due_date = np.round(self._due_date_assigner(**params)).astype(int)
        return self._new_order.due_date_accepted(due_date, self._time_now)
            
    def _update_events(self):
        sequence = self._queue.get_sequence()
        # t = self._time_now # + o an makinedeki işin remaining zamanı
        if self._in_process is None:
            t = self._time_now #+ 1e-5
        else:
            t = self._in_process._event_job_finish.time #+ 1e-5
        for order in reversed(sequence):
            # print('***', t)
            t = order.update_event_times(t)
            
    def get_stats(self, order):
        return order._id, order._customer._type, order._product._type, order._quantity, order.get_weight(), order._arrival_time, order._due_date, order._start_time, order._cancelation_time, order._finish_time, order.get_expected_process_time()
    
    def show_stats(self):
        stats_df = pd.DataFrame({'order':self._orders})

        stats = stats_df['order'].apply(self.get_stats)
        stats_df[['ID', 'customer type', 'product type', 'quantity','weight','arrival', 'due date','start','cancelled', 'finish', 'expected_process_time']] = pd.DataFrame(stats.tolist())
        stats_df  = stats_df.drop('order', axis=1)
        stats_df['weight'] = stats_df['weight'].astype(int)
        
        #START'TAN SONRA CANCEL EDİLENLERİN CANCELLED TİME'LARINI NONE'A ÇEVİR
        # customer reliabilityler 1 olunca burası hata veriyor
        mask = (stats_df['start'].notna()) & (stats_df['cancelled'].notna()) & (stats_df['start'] < stats_df['cancelled'])
        #print('cancelled after started being processed:', stats_df.loc[mask])
        stats_df.loc[mask, 'cancelled'] = None
        
        mask_tardy1 = (stats_df['finish'].notna()) & (stats_df['due date'].notna()) & (stats_df['finish'] > stats_df['due date'])
        stats_df.loc[mask_tardy1, 'tardy amount'] = stats_df.loc[mask_tardy1, 'finish'] - stats_df.loc[mask_tardy1, 'due date']

        return stats_df

    def run_once(self, log=False):
        self._initialize()
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

    def collect_stats(self):
        stats = self.show_stats()
        
        # Calculate the indices for the middle portion
        max_time = stats['finish'].max()
        warmup_percentage = 100 - self.warmup
        warmup_start = int(max_time * (self.warmup / 100))
        warmup_end = int(max_time * (warmup_percentage / 100))
        print(warmup_start,' - ', warmup_end)
        
        # Create a mask for orders within the warmup time range
        mask_warmup = (
            (stats['arrival'].between(warmup_start, warmup_end)) | (stats['start'].between(warmup_start, warmup_end)) |
            (stats['cancelled'].between(warmup_start, warmup_end)) | (stats['finish'].between(warmup_start, warmup_end))
        )

        # Apply the mask to filter the stats
        stats_warmed = stats[mask_warmup]
        #print(stats_warmed)
        stats_warmed['tardy amount'] = stats_warmed['tardy amount'].fillna(0)

        mask_tardy = stats_warmed['tardy amount'] > 0
        # mask_tardy = stats_warmed['tardy amount'].notna()
        mask_rejection = stats_warmed['due date'].isna()
        
        tardiness_prop = mask_tardy.sum()/len(stats_warmed)
        rejection_prop = mask_rejection.sum()/len(stats_warmed)

        avg_tardiness_amount = np.sum(stats_warmed['tardy amount']/stats_warmed['expected_process_time'])/len(stats_warmed)
        weighted_avg_tardiness_amount = np.sum(stats_warmed['tardy amount']/stats_warmed['expected_process_time'])/stats_warmed[mask_tardy]['weight'].sum()

        weighted_tardiness_prop = stats_warmed[mask_tardy]['weight'].sum()/stats_warmed['weight'].sum()
        weighted_rejection_prop = stats_warmed[mask_rejection]['weight'].sum()/stats_warmed['weight'].sum()

        return tardiness_prop, rejection_prop, weighted_tardiness_prop, weighted_rejection_prop, avg_tardiness_amount, weighted_avg_tardiness_amount

        # self._stats['tardiness_proportion'].append(tardiness_prop)
        # self._stats['rejection_proportion'].append(rejection_prop)
        # self._stats['weighted_tardiness_proportion'].append(weighted_tardiness_prop)
        # self._stats['weighted_rejection_proportion'].append(weighted_rejection_prop)

    # def run(self, n_sim, num_cores=-1, log=False) -> pd.DataFrame:
    #     self._stats = {'tardiness_proportion':[], 'rejection_proportion':[],
    #                    'weighted_tardiness_proportion':[], 'weighted_rejection_proportion':[]}
        
    #     if num_cores <= 0:
    #         self._num_cores = multiprocessing.cpu_count()
    #     else:
    #         self._num_cores = min(multiprocessing.cpu_count(), num_cores)

    #     for i in range(n_sim):
    #         # if log:
    #         #     print('******')
    #         #     print('******')
    #         #     print('******')
    #         print(f'round {i}')
    #         self.run_once(log=log)
    #         self._collect_stats()

    #     self._stats_df = pd.DataFrame(self._stats)
    #     return self._stats_df
