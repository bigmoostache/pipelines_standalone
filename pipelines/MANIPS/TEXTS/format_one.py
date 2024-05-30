import os

class Pipeline:

    def __init__(self, 
                 param : str):
        self.param = param
        

    def __call__(self, text : str) -> str:
        
        res = self.param.replace("__text_1__", text)
        return res
