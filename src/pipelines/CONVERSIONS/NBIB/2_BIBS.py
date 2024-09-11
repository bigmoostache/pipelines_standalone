from custom_types.BIB.type import BIB
from custom_types.NBIB.type import NBIB
from typing import List

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, pubmed : NBIB) -> List[BIB]:
        return pubmed.entries