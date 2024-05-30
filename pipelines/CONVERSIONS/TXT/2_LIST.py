from typing import List
import json

class Pipeline:
    def __init__(self):
        pass 

    def __call__(self, text : str) -> List[str]:
        text = text.replace('\n', ' ').replace('\t', ' ')
        sub_text = text[text.find('['):text.rfind(']')+1]
        dic = json.loads(sub_text)
        assert isinstance(dic, list)
        return dic