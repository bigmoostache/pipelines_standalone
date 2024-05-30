from pipelines.MANIPS.TEXTS.segment import Pipeline as SegmentPipeline
from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self,
                 text_param : str,
                 new_text_param : str,
                 max_chars : int):
        self.max_chars = max_chars
        self.text_param = text_param
        self.new_text_param = new_text_param

    def __call__(self, json : dict) -> JSONL:
        text = json[self.text_param]
        pipe = SegmentPipeline(max_chars=self.max_chars)
        segments = pipe(text)
        results = [{**json, self.new_text_param : segment} for segment in segments]
        return JSONL(results)