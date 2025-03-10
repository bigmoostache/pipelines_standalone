from random import random
class Pipeline:
    def __init__(self,
                 error_probability : float = 0.5,
                 ):
        self.error_probability = error_probability
    def __call__(self, input : str) -> str:
        if random() < self.error_probability:
            raise Exception('Random error')
        return input