from custom_types.JSONL.type import JSONL

class Pipeline:

    def __init__(self, param : str = ""):
        self.index_param = param

    def __call__(self, jsonl_1 : JSONL, jsonl_2 : JSONL, jsonl_3 : JSONL, jsonl_4 : JSONL) -> JSONL:
        _all_lines = jsonl_1.lines + jsonl_2.lines + jsonl_3.lines + jsonl_4.lines
        if self.index_param:
            found = set()
            all_lines = []
            for l in _all_lines:
                if l.get(self.index_param) in found:
                    continue 
                all_lines.append(l)
                found.add(l.get(self.index_param))
        else:
            all_lines = _all_lines
        return JSONL(all_lines)
