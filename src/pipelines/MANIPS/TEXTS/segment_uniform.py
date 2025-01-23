from custom_types.JSONL.type import JSONL

# -*- coding: utf-8 -*-
import re
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|me|edu)"
digits = "([0-9])"
multiple_dots = r'\.{2,}'

def split_into_sentences(text: str) -> list[str]:
    """
    Split the text into sentences.

    If the text contains substrings "<prd>" or "<stop>", they would lead 
    to incorrect splitting because they are used as markers for splitting.

    :param text: text to be split into sentences
    :type text: str

    :return: list of sentences
    :rtype: list[str]
    """
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    text = re.sub(multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = [s.strip() for s in sentences]
    if sentences and not sentences[-1]: sentences = sentences[:-1]
    return sentences

class Pipeline:
    def __init__(self, 
                 n_chars : int):
        self.n_chars = n_chars
        
    def __call__(self, x : str) -> JSONL:

        max_length = self.n_chars

        # 1. Try to split on actual sections
        chunks = re.split(r'(?=\n(?:#|##|###|####) )', x)

        new_chunks = []
        for chunk in chunks:
            local_chunks = [chunk]
            # 2. Split on double line breaks if not sufficient
            def split_double_breaks(_):
                return [_] if len(_)<= max_length else re.split(r'(?=\n\n)', _)
            local_chunks = [_ for __ in local_chunks for _ in split_double_breaks(__)]
            
            # 3. Split again on line breaks if not sufficient
            def split_line_breaks(_):
                return [_] if len(_)<= max_length else re.split(r'(?=\n)', _)
            local_chunks = [_ for __ in local_chunks for _ in split_line_breaks(__)]
            
            # 4. Split again on sentences if not sufficient
            def split_sentences(_):
                return [_] if len(_)<= max_length else split_into_sentences(_)
            local_chunks = [_ for __ in local_chunks for _ in split_sentences(__)]

            # 5. Split again on characters if not sufficient
            def split_chars(_):
                if len(_)<= max_length:
                    return [_]
                return [_[k*max_length:(k+1)*max_length] for k in range(1+len(_)//max_length)]
            local_chunks = [_ for __ in local_chunks for _ in split_chars(__)]

            # 6. Join them
            _chunks = [[]]
            for c in local_chunks:
                left, right = sum(map(len, _chunks[-1])), len(c)
                new =  (left >= max_length)
                if new:
                    _chunks.append([c])
                else:
                    _chunks[-1].append(c)
                    
            local_chunks = [(' '.join(_)).replace('  ', ' ') for _  in _chunks]
            new_chunks += local_chunks
        chunks = new_chunks 

        # 7. Join them
        _chunks = [[]]
        for i,c in enumerate(chunks[::-1]):
            left, right = sum(map(len, _chunks[-1])), len(c)
            new =  (left >= max_length)
            if new:
                _chunks[-1] = _chunks[-1][::-1]
                _chunks.append([c])
            else:
                _chunks[-1].append(c)
                if i+1 == len(chunks):
                    _chunks[-1] = _chunks[-1][::-1]

        chunks = [(' '.join(_)).replace('  ', ' ').replace('\n ', '\n') for _  in _chunks[::-1]]
        return JSONL(lines=[{'text': _, 'chunk_id':i} for i,_ in enumerate(chunks)])
        