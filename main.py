import pandas as pd
import numpy as np
from scipy.stats import expon, uniform, norm

from time import time

from simulation_environment import Environment
from due_date_policies import CON, SLK, TWK



if __name__ == '__main__':
    dispatching_rules = ['FIFO', 'SPT', 'BWF']
    due_date_policies = {'con': {k:CON(constant=k) for k in range(7, 15)}, 'slk': {k:SLK(constant=k) for k in range(3, 9)}}

    for dr in dispatching_rules:
        for k, v in due_date_policies.items():
            for k1, v1 in v.items():
                np.random.seed(3)
                print(dr, k, k1)
                env = Environment(n=2000, due_date_policy=v1, dispatching_rule=dr)
                env.initialize()
                env.run()

            
                

