import pandas as pd
import numpy as np
from scipy.stats import expon, uniform, norm

class Environment(object):
    def __init__(self, n, simulation_time=None, warmup=None):
        self._product_probs = [0.2, 0.3, 0.5]
        self._customer_probs = [0.6, 0.4]
        self.max_order_count = n
    
    def initialize(self):
        self._get_order_arrivals()
        self._get_order_products()
        self._get_order_customers()
        self.orders = pd.DataFrame({'arrival': self._order_arrivals, 'product': self._order_prod_types, 
                                    'customer':self._order_customer_types})
        self.orders['quantity'] = self.orders.apply(lambda row: Environment.get_order_quantity(row['product'], row['customer']), axis=1)
    
    def run(self):
        pass
    
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
