
from custom_types.JSONL.type import JSONL
class Pipeline:
    def __init__(self, max_left_to_right_ratio_in_percent : int, index_name : str):
        self.max_left_to_right_ratio = max_left_to_right_ratio_in_percent / 100 if max_left_to_right_ratio_in_percent else None
        self.index = index_name
    def __call__(self, left : JSONL, right : JSONL) -> JSONL:
        max_len = len(right.lines)
        if self.max_left_to_right_ratio:
            max_len = min(max_len, int(self.max_left_to_right_ratio * len(left.lines)))
        all_lines = left.lines + right.lines[:max_len]
        found_idx = set()
        res = []
        for l in all_lines:
            if l[self.index] in found_idx:
                continue
            res.append(l)
        return JSONL(res)