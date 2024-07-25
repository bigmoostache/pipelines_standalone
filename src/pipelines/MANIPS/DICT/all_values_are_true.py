class Pipeline:
    def __init__(self,
                 param_name : str,
                 ):
        self.param_name = param_name


    def __call__(self, dic : dict) -> dict:
        val = True 
        for k,v in dic.items():
            val = val and isinstance(v, bool) and v
        dic[self.param_name] = val
        return dic