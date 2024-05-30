import os
from custom_types.JSONL.type import JSONL
import re
import Levenshtein
from collections import Counter
import numpy as np

class Pipeline:
    __env__ = ["api_key", "api_secret", "api_url"]

    def __init__(self, 
                 tag_param : str = 'TAG',
                 new_tag_param : str = 'FTAG',
                 remove_strings : str = ''
                 ):
        self.tag_param = tag_param
        self.new_tag_param = new_tag_param
        self.remove_strings = [s[0].upper()+s[1:].lower() for s in remove_strings.split(',') if s]

    def __call__(self, data : JSONL) -> JSONL:
        dics = data.lines
        all_tags = [_ for d in dics for _ in d[self.tag_param]]
        all_tags = list(set(all_tags))

        def simplify(text):
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            splitted = text.split(' ')
            splitted = [_ for _ in splitted if _]
            splitted = [s[0].upper()+s[1:].lower() for s in splitted]
            if splitted[0].isnumeric():
                text = ' '.join(splitted[1:])
            else:
                text = ' '.join(splitted)
            for rs in self.remove_strings:
                text = text.replace(rs+' ', '')
                text = text.replace(' '+rs, ' ')
            return text.strip()
        all_simplified_tags = list(set([simplify(_) for _ in all_tags]))
        def distance(left, right):
            d = Levenshtein.distance(left, right)
            return d/max(len(left), len(right), 1)
        groups = {k:{k} for k in all_simplified_tags}
        for word in all_simplified_tags:
            words = [_ for _ in all_simplified_tags if distance(word, _)<=0.21]
            big_union = set().union(*[groups[k] for k in words])
            for k in words:
                groups[k] = big_union
        group_ids = list(set([' | '.join(list(v)) for k,v in groups.items()]))
        final_groups = {k:' | '.join(list(v)) for k,v in groups.items()}
        for d in dics:
            d[self.new_tag_param] = list(set([final_groups[simplify(_)] for _ in d[self.tag_param]]))
            
        cnt = Counter([_ for d in dics for _ in d[self.new_tag_param]])
        cnt = {k:v for k,v in dict(cnt).items() if 10 <= v <= 150}


        def compute_prox(word, dics, cnt):
            cnt_spe = Counter([_ for d in dics for _ in d[self.new_tag_param] if word in d[self.new_tag_param] and _ in cnt and cnt[_]>1.0])
            cnt_spe = dict(cnt_spe)
            _lambda = 0.2
            cnt_spe = {k : (_lambda*cnt_spe[k]/cnt[word]+(1-_lambda)*cnt_spe[k]/cnt[k]) for k in cnt_spe.keys()}
            def get_score(cnt_spe, dic):
                return np.mean([cnt_spe.get(_, 0) for _ in dic[self.new_tag_param]])
            TOP = np.argsort([get_score(cnt_spe, d) for d in dics])[::-1]
            return TOP[:min(200,int(2*cnt[word]))]
        count_dic = dict(cnt)
        count_dic = {k:
                    {
                        'count' : v, 
                        'idx' : [i for i,_ in enumerate(dics) if k in _[self.new_tag_param]],
                        'prox' : list(compute_prox(k, dics, cnt))
                    } 
                    for k,v in count_dic.items()
                    }
        for d in dics:
            d[self.new_tag_param] = []
        for kw, v in count_dic.items():
            for idx in v['prox']:
                dics[idx][self.new_tag_param].append(kw)
        return JSONL(dics)
        