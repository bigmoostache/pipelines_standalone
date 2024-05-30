import os

class Pipeline:
    def __init__(self, 
                 n_chars : int):
        self.format = format
        self.n_chars = n_chars
        
    def __call__(self, text : str) -> str:
        return text[:self.n_chars]
