from typing import List
from custom_types.JSONL.type import JSONL


class Pipeline:
    def __init__(self,
                 parameter : str,
                 MAX_CHARS : int = 750,
                 INDEX_NAME : str = 'index',
                 REMOVE_PARAMS : str = '',
                 ):
        self.MAX_CHARS = MAX_CHARS
        self.parameter = parameter
        self.INDEX_NAME = INDEX_NAME
        self.REMOVE_PARAMS = set(REMOVE_PARAMS.split(',') + [parameter])
        
    def __call__(self, dicts : List[dict]) -> JSONL:
        MAX_CHARS = self.MAX_CHARS
        INDEX_NAME = self.INDEX_NAME
        PARAM_NAME = self.parameter
        def build_entries(txt):
            txt = txt.split('\n')
            last = {'# ' : '', '## ': '', '### ': '', '#### ':''}
            res = [{**last.copy(), 'content': ''}]
            for t in txt:
                break_please = False
                for k,v in last.items():
                    if t.startswith(k) and 'Figure' not in t and 'Table' not in t:
                        if last[k] != '':
                            break_please = True
                        last[k] = t
                        for _k, _v in last.items():
                            if k in _k and k != _k:
                                break_please = True
                                last[_k] = ''
                        t = ''
                l =  len(t)
                previous_l = len(res[-1]['content'])
                if break_please:
                    res.append({**last, 'content':t})
                else:
                    res[-1]['content'] = res[-1]['content'] + '\n' + t
            
            def break_smartly(entry):
                c = entry['content']
                if len(c) <= MAX_CHARS:
                    return [entry]
                lines = c.split('\n\n')
                if len(lines) <= 1: 
                    return [entry]
                breaks = []
                last_l = 0
                for l in lines:
                    if (last_l > MAX_CHARS) or len(breaks) == 0:
                        breaks.append(l)
                        last_l = len(l)
                    else:
                        breaks[-1] = breaks[-1] + '\n\n' + l
                        last_l=  len(breaks[-1])
                if len(breaks) > 1 and len(breaks[-1]) <= 0.4 * len(breaks[-2]):
                    breaks [-2] = breaks[-2] + '\n\n' + breaks[-1]
                    breaks = breaks[:-1]
                return [{**entry, 'content':x} for x in breaks]

            r =  [e for x in res for e in break_smartly(x)]
            r = [{**x, '_local_index' : i} for i,x in enumerate(r)]
            return r

        def build_all_entries(dics):
            r = [{k: v for k, v in {**x, **y}.items() if k not in self.REMOVE_PARAMS} for x in dics for y in build_entries(x[PARAM_NAME])]
            return [{**x, INDEX_NAME:i} for i,x in enumerate(r)]
        
        return JSONL(lines = build_all_entries(dicts))