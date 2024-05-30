from typing import List

class Pipeline:
    def __init__(self, split_on: str):
        self.split_on = split_on

    def __call__(self, text : str) -> List[str]:
        res = text.split(self.split_on)
        res = [r.strip() for r in res if r.strip()]
        return res