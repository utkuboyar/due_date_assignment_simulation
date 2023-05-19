import pandas as pd
from time import time
import datetime
import _pickle

from simulation_environment import Simulation
from utils.model_params import *


if __name__ == '__main__':
    records = {}
    now = datetime.datetime.now()
    records['start_time'] = f'{now.year}-{now.month}-{now.day}_{now.hour}:{now.minute}'

    seed, n, simulation_time, warmup, n_sim = get_simulation_params()
    records['seed'], records['n'], records['simulation_time'], records['warmup'], records['n_sim'] = seed, n, simulation_time, warmup, n_sim

    records['results'] = None

    simulation_info = []
    for dispatching_rule in dispatching_rule_grid():
            for due_date_policy_params in due_date_policy_grid():
                print(dispatching_rule, due_date_policy_params)
                sim = Simulation(seed=seed, n=n, due_date_policy_params=due_date_policy_params, dispatching_rule=dispatching_rule, warmup=warmup)
                stats = sim.run(n_sim = n_sim)
                sim_info = {'dispatching':dispatching_rule, 'due_date':due_date_policy_params['policy'],
                        'due_date_param':list(due_date_policy_params.values())[1]}
                sim_info.update(stats)
                simulation_info.append(sim_info)
                #print(stats)
                #print()

    df = pd.DataFrame(simulation_info)
    records['results'] = df
    with open(f'records_{records["start_time"]}', 'wb') as f:
        _pickle.dump(records, f)