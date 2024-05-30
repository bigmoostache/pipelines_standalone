from typing import List 
from pipelines.MANIPS.TEXTS.segment import Pipeline as Segment

class Pipeline:
    def __init__(self, 
                 parameter : str,
                 max_chars: int = 1000,
                 new_index_name : str = "index",
                 paragraphs_name : str = "paragraphs",
                 remove_big : bool = False
                 ):
        self.parameter = parameter
        self.new_index_name = new_index_name
        self.max_chars = max_chars
        self.paragraphs_name = paragraphs_name
        self.remove_big = remove_big

    def __call__(self, json : dict) -> List[dict]:
        if self.parameter not in json:
            raise 
        article = json[self.parameter]
        paragraphs = Segment(self.max_chars)(article)
        results = [{**json, self.new_index_name: i, self.paragraphs_name: paragraph} for i, paragraph in enumerate(paragraphs)]
        if self.remove_big:
            results = [{k:v for k,v in x.items() if k!=self.parameter} for x in results]
        return results