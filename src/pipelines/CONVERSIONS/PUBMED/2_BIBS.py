from custom_types.BIB.type import BIB
from custom_types.PUBMED.type import PUBMED_BIBS
from typing import List

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, pubmed : PUBMED_BIBS) -> List[BIB]:
        return pubmed.entries