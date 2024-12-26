class Pipeline:
    def __init__(self):
        pass 
    def __call__(self, input : str) -> str:
        raise Exception("This pipeline is meant to fail.")