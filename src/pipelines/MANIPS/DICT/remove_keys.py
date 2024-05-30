class Pipeline:
    def __init__(self,
                 keys_to_keep:str,
                 remove_them_instead : bool = False
                 ):
        self.remove_them_instead = remove_them_instead
        self.values = set([_.strip() for _ in keys_to_keep.split(',')])


    def __call__(self, dic : dict) -> dict:
        if not self.remove_them_instead:
            return {k:v for k,v in dic.items() if k in self.values}
        return {k:v for k,v in dic.items() if k not in self.values}