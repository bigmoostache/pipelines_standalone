import os

class Pipeline:
    __env__ = ["api_key", "api_secret", "api_url"]

    def __init__(self, 
                 format : str = "This is a pipeline with __text_1__ and __text_2__",
                 tbool : bool = True,
                 ):
        self.format = format
        assert "__text_1__" in self.format
        assert "__text_2__" in self.format
        

    def __call__(self, text_1 : str, text_2 : str) -> str:
        for env in self.__env__:
            print(f"{env}={os.environ.get(env)}")
        
        res = self.format.replace("__text_1__", text_1)
        res = res.replace("__text_2__", text_2)
        return res
