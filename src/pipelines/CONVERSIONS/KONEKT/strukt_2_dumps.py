from custom_types.KONEKT.type import GenericType

class Pipeline:
    def __init__(self):
        pass        
    def __call__(self, konekt : GenericType) -> str:
        return konekt.model_dump_json(indent=2)