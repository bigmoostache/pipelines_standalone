from typing import List
import re

class Pipeline:

    def __init__(self,
                 max_chars: int =1000):
        self.max_chars = max_chars


    def __call__(self, article :str) -> List[dict]:

        matches = [[m.group(0), (m.start(), m.end() - 1)] for m in re.finditer(r'(?!\\n\\n)([^\n]|\\n(?!\\n))+', article)]
        chunked_text, split_idx = zip(*matches)

        # Truncate by max_chars
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

        # Let us look for all the sections in the article
        sections = []
        for i, chunk in enumerate(new_chunked_text):
            if chunk[0] == "#": sections.append((chunk, new_split_idx[i]))
                
        # Let us assing each paragraph to each session
        assigned_sections = []

        for i,chunk in enumerate(new_chunked_text):
            midpoint = (new_split_idx[i][1]+new_split_idx[i][0])/2

            assigned_section = "other"
            for section in sections:
                section_name = section[0]
                idx_start, idx_end = section[1]
                if midpoint > idx_start:
                    assigned_section = section_name
            
            assigned_sections.append(assigned_section)

        return [{"texts":new_chunked_text[i], "index_ranges":new_split_idx[i], "pseudo_sections":assigned_sections[i]} for i in range(len(new_chunked_text))]
