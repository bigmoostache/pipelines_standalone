class Pipeline:
    def __init__(self,
                 param_name : str,
                 expression : str
                 ):
        self.param_name = param_name
        self.expression = expression


    def __call__(self, dic : dict) -> dict:
        dic[self.param_name] = eval(self.expression, {}, dic)
        return dic