class Pipeline:
    def __init__(self,
                 param_name:str
                 ):
        self.param_name = param_name


    def __call__(self, value : str, dic : dict) -> dict:
        dic[self.param_name] = value
        return dic