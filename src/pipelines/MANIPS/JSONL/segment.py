
from custom_types.JSONL.type import JSONL
from pipelines.MANIPS.TEXTS.segment import Pipeline as TextSegmenter

class Pipeline:

    def __init__(self,
                 text_param: str = "text",
                 max_chars: int = 1000):
        self.text_param = text_param
        self.max_chars = max_chars

    def __call__(self, jsonl : JSONL) -> JSONL:
        results = []
        text_segmenter = TextSegmenter(max_chars=self.max_chars)
        for line in jsonl.lines:
            article = line[self.text_param]
            chunks = text_segmenter(article)
            results.extend([{**line, self.text_param: chunk} for chunk in chunks])
        return JSONL(results)