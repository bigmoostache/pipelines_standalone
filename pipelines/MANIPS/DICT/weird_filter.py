class Pipeline:
    def __init__(self,
                 values:str
                 ):
        self.values = set([_.lower().strip() for _ in values.split(',')])


    def __call__(self, dic : dict, dic_analysis : dict) -> dict:
        return {k:v for k,v in dic.items() if dic_analysis.get(k, '???').lower().strip() in self.values}