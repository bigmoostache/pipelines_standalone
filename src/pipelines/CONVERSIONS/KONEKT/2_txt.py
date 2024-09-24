from custom_types.KONEKT.type import Result

class Pipeline:
    def __init__(self):
        pass        
    def __call__(self, konekt : Result) -> str:
        return konekt.to_markdown()