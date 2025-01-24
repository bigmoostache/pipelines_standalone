import re, string
from typing import List
from pipelines.utils.useless import Pipeline

def simplify(text : str) -> str:
    if not isinstance(text, str):
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
    return res