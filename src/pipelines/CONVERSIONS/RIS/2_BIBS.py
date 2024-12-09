from custom_types.BIB.type import BIB
from custom_types.RIS.type import RisBibs
from typing import List

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, pubmed : RisBibs) -> List[BIB]:
        return pubmed.entries