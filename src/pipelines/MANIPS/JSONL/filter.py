import re, string
from custom_types.JSONL.type import JSONL


def simplify(text : str) -> str:
    if not isinstance(text, str):
        return text
    if not text:
        return text
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
    
class Pipeline:
    def __init__(self,
                 jsonl_param:str,
                 jsonl_value:str,
                 equals : bool = True,
                 remove_nans: bool = False
                 ):
        self.jsonl_param = jsonl_param
        self.jsonl_value = simplify(jsonl_value)
        self.equals = equals
        self.remove_nans = remove_nans
        


    def __call__(self, jsonl : JSONL) -> JSONL:
        if self.equals:
            res = [d for d in jsonl.lines if simplify(d.get(self.jsonl_param, "")) == self.jsonl_value]
        else:
            res = [d for d in jsonl.lines if simplify(d.get(self.jsonl_param, "")) != self.jsonl_value]
        if self.remove_nans:
            res = [d for d in jsonl.lines if d.get(self.jsonl_param, None) is not None]
        return JSONL(lines = res)
        