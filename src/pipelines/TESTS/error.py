from random import random
class Pipeline:
    def __init__(self,
                 error_probability : float = 0.5,
                 ):
        pass 
    def __call__(self, input : str) -> str:
        if random() < self.error_probability:
            raise Exception('Random error')
        return input