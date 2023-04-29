class Event(object):
    def __init__(self, time, order, env):
        self.time = time
        self.order = order
        self.occurance_time_fixed = False
        self.type = None
        
        self.environment = env
        self.heap = self.environment._event_heap
        
    def update_time(self, time):
        if self.type in ['arrival', 'cancellation']:
            raise Exception('occurance times for order arrival and cancellation events are set at initialization!')
        if self.occurance_time_fixed:
            raise Exception('occurance time was fixed for this event, it cannot be updated!')
        
        if time != self.time:
            self.time = time
            self.heap.update_event(self)
        
    def occur(self):
        raise NotImplementedError('Event is an abstract class')
        
    def __lt__(self, other_event):
        return self.time < other_event.time
    
    def __repr__(self):
        pass
    
    def __del__(self):
        pass
    
    def remove(self):
        self.heap.remove(self)


class OrderArrival(Event):
    def __init__(self, time, order, env):
        super().__init__(self, time, order, env)
        self.type = 'arrival'
        self.occurance_time_fixed = True
        
    def occur(self):
        self.environment.arrival(self)

class OrderCancellation(Event):
    def __init__(self, time, order, env):
        super().__init__(self, time, order, env)
        self.type = 'cancellation'
        self.occurance_time_fixed = True
        
    def occur(self):
        self.order.remove_events()
        self.environment.cancellation(self)

class JobStart(Event):
    def __init__(self, time, order, env):
        super().__init__(self, time, order, env)
        self.type = 'start'
        
    def occur(self):
        self.environment.start_job(self.order)

class JobFinish(Event):
    def __init__(self, time, order, env):
        super().__init__(self, time, order, env)
        self.type = 'finish'
    
    def occur(self):
        self.environment.finish_job()