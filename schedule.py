from order import Order

class JobQueue(object):

    def __init__(self, policy):
        self._orders_unordered = [] # list of Order instances
        self._sequence = [] # list of Order instances
        self._policy = policy
        
    def add_order(self, new_order):
        self._orders_unordered.append(new_order)
        
    def remove_order(self, order):
        self._orders_unordered.remove(order)
        
    def pop_order(self) -> Order:
        order = self._sequence.pop()
        self._orders_unordered.remove(order)
        return order
        
    def reschedule(self, due_date_params=True) -> dict:
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
            
    
    def set_schedule(self, confirm) -> None:
        if confirm:
            self._sequence = self._proposed_new_schedule.copy()
        else:
            self._orders_unordered.pop()
        self._proposed_new_schedule = None
    
    def get_sequence(self) -> list:
        return self._sequence
    