import os

class Pipeline:

    def __init__(self, 
                 format : str):
        self.format = format
        assert "__text_1__" in self.format
        assert "__text_2__" in self.format
        

    def __call__(self, text_1 : str, text_2 : str) -> str:
        res = self.format.replace("__text_1__", text_1)
        res = res.replace("__text_2__", text_2)
        return res
