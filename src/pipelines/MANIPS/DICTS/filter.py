import re, string
from typing import List

def simplify(text : str) -> str:
    # lower, remove punctuation, remove multiple spaces, strip, remove accents
    res = re.sub(r'\s+', ' ', text.lower().translate(str.maketrans('', '', string.punctuation))).strip()
    # accents -> convert to same character without accent using re
    res = re.sub(r'[àáâãäå]', 'a', res)
    res = re.sub(r'[èéêë]', 'e', res)
    res = re.sub(r'[ìíîï]', 'i', res)
    res = re.sub(r'[òóôõö]', 'o', res)
    res = re.sub(r'[ùúûü]', 'u', res)
    res = re.sub(r'[ýÿ]', 'y', res)
    res = re.sub(r'[ç]', 'c', res)
    res = re.sub(r'[ñ]', 'n', res)
    
    return res
    
class Pipeline:
    def __init__(self, key : str, values : str):
        self.key = key
        self.values = values.split(',')
        self.values = [simplify(v) for v in self.values]

    def __call__(self, dics : List[dict]) -> List[dict]:
        return [d for d in dics if simplify(str(d.get(self.key, "None"))) in self.values]
    