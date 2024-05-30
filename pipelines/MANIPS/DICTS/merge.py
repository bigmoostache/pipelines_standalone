import re
from typing import List

class Pipeline:
    def __init__(self):
        pass

    def __call__(self, left : dict, right :dict) -> dict:
        return {**left, **right}