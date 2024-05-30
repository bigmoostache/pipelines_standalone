from typing import List

class Pipeline:
    def __init__(self):
        pass
    def __call__(self) -> List[dict]:
        raise Exception("This pipeline is not meant to be called")