from typing import List
class Pipeline:
    def __init__(self, n_duplicates : int):
        self.n_duplicates = n_duplicates

    def __call__(self) -> List[str]:
        return  ["" for _ in range(self.n_duplicates)]

