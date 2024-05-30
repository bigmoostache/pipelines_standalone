class Pipeline:

    def __init__(self, 
                 format : str):
        self.format = format
        assert "__text_1__" in self.format
        assert "__text_2__" in self.format
        assert "__text_3__" in self.format
        assert "__text_4__" in self.format
        
    def __call__(self, text_1 : str, text_2 : str, text_3 : str, text_4 : str) -> str:
        res = self.format.replace("__text_1__", text_1)
        res = res.replace("__text_2__", text_2)
        res = res.replace("__text_3__", text_3)
        res = res.replace("__text_4__", text_4)
        return res
