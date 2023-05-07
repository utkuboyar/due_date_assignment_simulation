from order import Order
import gurobipy as gp
import numpy as np

#from order import Order

class JobQueue(object):

    def __init__(self, policy):
        self._orders_unordered = [] # list of Order instances
        self._sequence = [] # list of Order instances
        self._policy = policy
        
    def add_order(self, new_order):
        self._orders_unordered.append(new_order)
        
    def remove_order(self, order):
        #print('remove_order called')
        # print(self._orders_unordered)
        # print(order)
        # print(type(order))
        # for o in self._orders_unordered:
        #     print('...', type(o))
        self._orders_unordered.remove(order)
        
    def pop_order(self) -> Order:
#         print('here pop_order')
#         print(self._sequence)
        if len(self._sequence) == 0:
            return
        order = self._sequence.pop()
        self._orders_unordered.remove(order)
        return order
        
    def reschedule(self, due_date_params=True, expected_remaining_time_on_machine=None) -> dict:
        if self._policy == 'optimization':
            self.optimize(expected_remaining_time_on_machine=expected_remaining_time_on_machine)
        if self._policy != 'optimization':
            self._proposed_new_schedule = sorted(self._orders_unordered, reverse=True)

        if not due_date_params:
            return {}
        t_completion, t_process = 0, None
        for order in self._proposed_new_schedule:
            t_completion += order._expected_process_time
            if order == self._orders_unordered[-1]:
                break
        return {'expected_completion_time': t_completion, 'expected_process_time':t_process}
    
    def optimize(self, expected_remaining_time_on_machine):
        model = gp.Model('opt_model')
        n = len(self._orders_unordered)
        a, b, p, d = [],[],[],[]
        for i, order in enumerate(self._orders_unordered):
            a.append(order._weight*0.8) #0.8 is given as an initial value will be changed most probabily, a is the due date cost for the new arrived job
            b.append(order._weight) #tardiness cost
            p.append(order._expected_process_time)  
            if i == n-1:
                d.append(None)
            else:
                d.append(order._due_date)
        d = list(np.array(d)-expected_remaining_time_on_machine)

        I = range(n)
        M= sum(p) + 1
        L= [(i,j) for i in I for j in range(i+1,n)]
        C = model.addVars(I, lb=0, vtype=gp.GRB.INTEGER, name='C')  # completion time of each job
        T = model.addVars(I, lb=0, vtype=gp.GRB.INTEGER, name='T')  # tardiness for each job
        Y = model.addVars(L,lb=0, vtype=gp.GRB.BINARY, name='Y')  # binary variables for job sequencing

        model.setObjective(a[n-1] * C[n-1] + gp.quicksum(b[i] * T[i] for i in range(n-1)), sense=gp.GRB.MINIMIZE)

        for i in I:
            for j in range(i+1, n):
                print(i,j)
                model.addConstr(C[i] <= C[j] - p[j] + M * (1 - Y[i,j]))
                model.addConstr(C[j] <= C[i] - p[i] + M * (Y[i,j]))

        for i in range(n-1):
            model.addConstr(T[i] >= C[i] - d[i])
            model.addConstr(T[i] >= 0)

        for i in I:
            model.addConstr(C[i] >= p[i])

        model.optimize()
        if model.status == gp.GRB.INFEASIBLE:
            print(a)
            print(b)
            print(d)
            print(p)
        c=[]
        for i in range(n):
            c.append(C[i].x)
        
        self._proposed_new_schedule = list(np.array(self._orders_unordered)[np.argsort(c)])
            
    
    def set_schedule(self, confirm) -> None:
        if confirm:
            self._sequence = self._proposed_new_schedule.copy()
        else:
            self._orders_unordered.pop()
        self._proposed_new_schedule = None
    
    def get_sequence(self) -> list:
        return self._sequence
    
