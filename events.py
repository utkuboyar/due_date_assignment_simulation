class Event(object):
    def __init__(self, time, order):
        self.time = time
        self.order = order
        self.occurance_time_fixed = False
        self.type = None
        
        self.environment = self.order._environment
        self.heap = self.environment.event_heap
        self.heap.add(self)
        
    def update_time(self, time):
        if self.type in ['arrival', 'cancelation']:
            raise Exception('occurance times for order arrival and cancelation events are set at initialization!')
        if self.occurance_time_fixed:
            raise Exception('occurance time was fixed for this event, it cannot be updated!')
        
        if time != self.time:
            self.time = time
            self.heap.update_event(self)
        
    def occur(self):
        raise NotImplementedError('Event is an abstract class')
        
    def __lt__(self, other_event):
        if self.time == other_event.time:
            if self.type == 'finish':
                return True
            if self.type == 'start':
                return other_event.type != 'finish'
        return self.time < other_event.time
    
    def __repr__(self):
        info = {'type': self.type, 'order': self.order._id, 'time': self.time}
        stringified = ""
        for k, v in info.items():
            stringified += f"{k}: {v}\n"
        return f"({stringified})"
    
    def __del__(self):
        pass
    
    def remove(self):
        self.heap.remove(self)


class OrderArrival(Event):
    def __init__(self, time, order):
        super().__init__(time, order)
        self.type = 'arrival'
        self.occurance_time_fixed = True
        
    def occur(self):
        self.environment.arrival(self.order)

class OrderCancelation(Event):
    def __init__(self, time, order):
        super().__init__(time, order)
        self.type = 'cancelation'
        self.occurance_time_fixed = True
        
    def occur(self):
        self.order.cancel()
        #self.environment.cancelation(self)
        self.environment.cancelation(self.order)

class JobStart(Event):
    def __init__(self, time, order):
        super().__init__(time, order)
        self.type = 'start'
        
    def occur(self):
        self.order.prevent_cancelation()
        self.environment.start_job(self.order)

class JobFinish(Event):
    def __init__(self, time, order):
        super().__init__(time, order)
        self.type = 'finish'
    
    def occur(self):
        self.environment.finish_job()