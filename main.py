import pandas as pd
import numpy as np
from scipy.stats import expon, uniform, norm

from time import time

from simulation_environment import Environment
from due_date_policies import CON, SLK, TWK



if __name__ == '__main__':
    # np.random.seed(10)

    con = CON(constant=10)
    env = Environment(n=100, due_date_policy=con, dispatching_rule='SPT')
    # slk = SLK(constant=6)
    # env = Environment(n=100, due_date_policy=slk, dispatching_rule='SPT')
    env.initialize()
    env.run()

            
                

