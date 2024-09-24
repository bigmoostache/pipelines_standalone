from custom_types.KONEKT.type import GenericType

class Pipeline:
    def __init__(self):
        pass        
    def __call__(self, konekt : GenericType) -> str:
        return konekt.to_markdown()