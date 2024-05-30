import re

class Pipeline:
    def __init__(self):
        pass
        
    def __call__(self, text : str) -> str:
        return re.sub(r'\[\d{1,2}\]', '', text)
