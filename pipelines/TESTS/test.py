from typing import Literal
from utils.cost import register_cost
class Pipeline:
    __DESCRIPTION__ = "Deleting everything on your computer. RIP."
    
    def __init__(self,
                 some_int : int,
                 some_bool : bool,
                 some_str : str,
                 some_float : float,
                 some_literal : Literal["a", "b", "c"]
                 ):
        pass 
    def __call__(self, input : dict) -> dict:
        register_cost(2.345)
        return input