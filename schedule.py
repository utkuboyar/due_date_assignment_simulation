class Schedule(object):
    def __init__(self, policy):
        self._orders_unordered = None
        self._sequence = None # BST may be implemented
        self._policy = policy
        
    def _add_order(self, new_order):
        self._orders_unordered.append(new_order)
        self._reschedule()
        
    def _pop_order(self):
        order = self._sequence.pop()
        self._orders_unordered.remove(order)
        
    def _reschedule(self):
        # BST may be implemented
        if self._policy != 'optimization':
            self._sequence = sorted(self._orders_unordered, reverse=True)