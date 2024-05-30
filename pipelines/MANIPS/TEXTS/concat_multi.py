from typing import List

class Pipeline:
    def __init__(self, 
                 joiner : str ="\n\n",
                 first_too : bool = False):
        self.joiner = joiner
        self.first_too = first_too
        
    def __call__(self, texts : List[str]) -> str:
        res =  self.joiner.join(texts)
        if self.first_too:
            res = self.joiner + res
        return res
