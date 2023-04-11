class DueDatePolicy(object):
    def __init__(self, policy):
        self.policy = policy
    
    def _calculate_due_date(self, **kwargs):
        raise NotImplementedError('DueDatePolicy is an abstract class')
        
    def get_params(self):
        raise NotImplementedError('DueDatePolicy is an abstract class')
        
    def __call__(self, **kwargs):
        return self._calculate_due_date(**kwargs)
       
    
class CON(DueDatePolicy):
    def __init__(self, constant):
        super().__init__('CON')
        self.constant = constant
    
    def _calculate_due_date(self, **kwargs):
        time_now = kwargs['time_now']
        return time_now + self.constant
    
    def get_params(self):
        params = {'policy': 'CON', 'constant': self.constant}
        return params
    
    
class SLK(DueDatePolicy):
    def __init__(self, constant):
        super().__init__('SLK')
        self.constant = constant
        
    def _calculate_due_date(self, **kwargs):
        expected_completion_time = kwargs['expected_completion_time']
        return expected_completion_time + self.constant
        
    def get_params(self):
        params = {'policy': 'SLK', 'constant': self.constant}
        return params
    
class TWK(DueDatePolicy):
    def __init__(self, moving_avg_window=5):
        super().__init__('TWK')
        self._ma_window = moving_avg_window
        
    def _calculate_due_date(self, **kwargs):
        time_now = kwargs['time_now']
        expected_process_time = kwargs['expected_process_time']
        self._calculate_coef() 
        return time_now + expected_process_time * self._coef 
    
    def _calculate_coef(self):
        pass
    
    def get_params(self):
        params = {'policy': 'TWK', 'moving_average': self.constant}
        return params