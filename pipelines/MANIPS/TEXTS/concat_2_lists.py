from typing import List

class Pipeline:

    def __init__(self): 
        pass        

    def __call__(self, text_1 : List[str], text_2 : List[str]) -> List[str]:
        return text_1 + text_2
