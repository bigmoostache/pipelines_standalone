from typing import List

class Pipeline:

    def __init__(self, 
                 max_chars: int = 1000, 
                 n_chunks_begin : int = None, 
                 n_chunks_end : int = None):
        self.max_chars = max_chars
        self.n_chunks_begin = n_chunks_begin
        self.n_chunks_end = n_chunks_end

    def __call__(self, article: str) -> List[str]:
        article = article.replace("\n", ' ').replace('. ', '. SPLIT_HERE')
        segments = [x for x in article.split('SPLIT_HERE') if x.strip() != '']   
        paragraphs = []
        current_paragraph = ""
        for segment in segments:
            # Add segment to the current paragraph
            current_paragraph += segment.strip() + ' '
            if len(current_paragraph) > self.max_chars:
                paragraphs.append(current_paragraph)
                current_paragraph = ""
        
        # Add the last paragraph if it's not empty
        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())
            
        if self.n_chunks_begin and self.n_chunks_end:
            if self.n_chunks_begin + self.n_chunks_end >= len(paragraphs):
                return paragraphs
            return paragraphs[:self.n_chunks_begin] + paragraphs[-self.n_chunks_end:]
        elif self.n_chunks_begin:
            return paragraphs[:self.n_chunks_begin]
        elif self.n_chunks_end:
            return paragraphs[-self.n_chunks_end:]
        return paragraphs
