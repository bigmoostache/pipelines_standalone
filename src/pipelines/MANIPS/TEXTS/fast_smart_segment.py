from typing import List
import re

class Pipeline:

    def __init__(self,
                 max_chars: int =1000):
        self.max_chars = max_chars

    def __call__(self, article :str) -> List[str]:
        matches = [[m.group(0), (m.start(), m.end() - 1)] for m in re.finditer(r'(?!\\n\\n)([^\n]|\\n(?!\\n))+', article)]
        chunked_text, split_idx = zip(*matches)
        new_chunked_text = []
        new_split_idx = []
        for i, chunk in enumerate(chunked_text):
            length = len(chunk)
            diff = length - self.max_chars

            if diff>0:
                new_chunked_text.append(chunk[0:self.max_chars])
                start, end = split_idx[i][0], split_idx[i][1]
                new_split_idx.append((start, end +1 - diff))
            else: 
                new_chunked_text.append(chunk)
                start, end = split_idx[i][0], split_idx[i][1]
                new_split_idx.append((start, end+1))
        return new_chunked_text
