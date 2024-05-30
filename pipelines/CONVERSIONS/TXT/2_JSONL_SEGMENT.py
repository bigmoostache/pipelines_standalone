from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self,
                 MAX_CHARS : int = 10000,
                 parameter : str = 'chunk',
                 index_name: str = 'index'
                 ):
        self.MAX_CHARS =  MAX_CHARS
        self.param = parameter
        self.index_name = index_name

    def __call__(self, txt : str) -> JSONL:
        for i in range(25):
            txt = txt.replace(' \n', '\n')
        txt = txt.split('.\n')
        txt = [a+'.' for a in txt[:-1]] + [txt[-1]]
        res = [txt[0]]
        for t in txt[1:]:
            t = t.strip()
            if t and (t[0].islower() and t[0].isalpha()):
                res[-1] = res[-1] + '\n' + t
            else:
                res.append(t)
        MAX_LEN = self.MAX_CHARS
        res2 = [res[0]]
        for i,t in enumerate(res[1:]):
            l = len(t)
            if len(res2[-1]) + l > MAX_LEN:
                res2.append(t)
            else:
                res2[-1] = res2[-1] + '\n' + t
        if len(res2)>1 and len(res2[-1])<=0.3*len(res2[-2]):
            res2[-2] = res2[-2] + '\n' + res2[-1]
            res2 = res2[:-1]
        return JSONL(lines= [{self.param:t, self.index_name:i} for i,t in enumerate(res2)])