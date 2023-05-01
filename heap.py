from heapdict import heapdict
import pandas as pd

class MinHeap:
    def __init__(self):
        self._events = heapdict()
        self._buffer = set()
        self._occured_events = heapdict()
        
    def update_event(self, event):
        if (event not in self._events) and (event not in self._buffer):
            raise Exception('the event that you are trying to update does not exist')
        self._events[event] = event
        if event in self._buffer:
            self._buffer.remove(event)
    
    def is_empty(self):
        return len(self._events) == 0
    
    def get_imminent_event(self):
        event, time = self._events.popitem()
        self._occured_events[event] = event
        return event, event.time
    
    def remove(self, event):
        if event not in self._events:
            if event.type in ['start', 'finish']:
                return
            else:
                raise Exception(event)
        del self._events[event]
        
        
    def add(self, event):
        if event.time is None:
            self._buffer.add(event)
        else:
            self._events[event] = event
        
    def show_events(self, occured=False):
        if occured:
            heap = self._occured_events.heap
        else:
            heap = self._events.heap
        event_times = [event_info[0].time for event_info in heap]
        event_types = [event_info[1].type for event_info in heap]
        event_order_ids = [event_info[1].order._id for event_info in heap]
        
        events_df = pd.DataFrame({'time': event_times, 'type':event_types, 
                                  'order':event_order_ids})
        if occured:
            events_df['accepted'] = [event_info[1].order._due_date is not None for event_info in heap]
        
        return events_df
        
    
            
    