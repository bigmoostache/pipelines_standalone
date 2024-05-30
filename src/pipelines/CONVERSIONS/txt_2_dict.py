import requests
import json
import re

class Pipeline:
    def __init__(self):
        pass 

    def __call__(self, text : str) -> dict:
        text = text.replace('\n', ' ').replace('\t', ' ')
        sub_text = text[text.find('{'):text.rfind('}')+1]
        sub_text2 = text[text.find('['):text.rfind(']')+1]
        if len(sub_text2)> len(sub_text):
            sub_text=sub_text2
        dic = json.loads(sub_text)
        return dic