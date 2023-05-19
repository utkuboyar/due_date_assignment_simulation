def get_simulation_params():
    seed = 3
    n = 10000
    simulation_time = None
    warmup = 20
    n_sim = 3
    return seed, n, simulation_time, warmup, n_sim

def dispatching_rule_grid():
    dispatching_rules = ['FIFO', 'SPT', 'BWF', 'optimization']
    for dispatching_rule in dispatching_rules:
        yield dispatching_rule

def due_date_policy_grid():
    con_grid = [{'policy':'CON', 'constant':100*k} for k in range(2, 4)]
    slk_grid = [{'policy':'SLK', 'constant':50*k} for k in range(3, 5)]
    twk_grid = [{'policy':'TWK', 'moving_avg_window':10*k} for k in range(1, 2)]
    
    for con_combination in con_grid:
        yield con_combination
    for slk_combination in slk_grid:
        yield slk_combination
    for twk_combination in twk_grid:
        yield twk_combination