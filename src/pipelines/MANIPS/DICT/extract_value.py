class Pipeline:
    def __init__(self,
                 key_name:str
                 ):
        self.param_name = key_name

    def __call__(self, dic : dict) -> str:
        return dic[self.key_name]