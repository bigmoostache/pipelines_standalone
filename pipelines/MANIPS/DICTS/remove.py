import re, string
from typing import List

class Pipeline:
    def __init__(self, remove : str):
        self.remove = remove.split(',')

    def __call__(self, dic : dict) -> dict:
        return {k:v for k,v in dic.items() if k not in self.remove}
    