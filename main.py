import pandas as pd
import numpy as np
from scipy.stats import expon, uniform, norm

from time import time

from simulation_environment import Environment
from order import Order



if __name__ == '__main__':
    env = Environment(n=100)
    env.initialize()

    orders = []
    for i, row in env.orders.iterrows():
        if i == 10:
            break
        orders.append(Order(arrival_time=row['arrival'], product_type=row['product'], customer_type=row['customer'], 
                            quantity=row['quantity'], dispatching_rule='SPT'))

    for order in orders:
        print(order._arrival_time, order._process_time)
    

            
                

