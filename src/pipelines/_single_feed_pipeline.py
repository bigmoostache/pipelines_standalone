from pipelines.utils.logger import log, result

class Pipeline:
    def __init__(self):
        pass
    def __call__(self) -> dict:
        raise Exception("This pipeline is not meant to be called")


