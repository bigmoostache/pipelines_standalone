import re

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 text : str) -> str:
        text = re.sub(r'[^\w\s]', '', text)
        return str(len([x for x in text.split() if len(x)>2]))