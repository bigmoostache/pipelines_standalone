class Pipeline:

    ''' Takes a value out of dictionary using its key'''
    def __init__(self,
                 key_name:str
                 ):
        self.key_name = key_name

    def __call__(self, dic : dict) -> str:
        return str(dic[self.key_name])