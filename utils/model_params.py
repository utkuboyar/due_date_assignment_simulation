def get_simulation_params():
    seed = 3
    n = 10000
    simulation_time = None
    warmup = None
    n_sim = 10
    return seed, n, simulation_time, warmup, n_sim

def dispatching_rule_grid():
    dispatching_rules = ['FIFO', 'SPT', 'BWF', 'optimization']
    for dispatching_rule in dispatching_rules:
        yield dispatching_rule

def due_date_policy_grid():
    con_grid = [{'policy':'CON', 'constant':k} for k in range(50, 56)]
    slk_grid = [{'policy':'SLK', 'constant':k} for k in range(20, 26)]
    twk_grid = [{'policy':'TWK', 'moving_avg_window':k} for k in range(5, 8)]
    
    for con_combination in con_grid:
        yield con_combination
    for slk_combination in slk_grid:
        yield slk_combination
    for twk_combination in twk_grid:
        yield twk_combination