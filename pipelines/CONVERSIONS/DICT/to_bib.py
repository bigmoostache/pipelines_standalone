from custom_types.BIB.type import BIB

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, bib : dict) -> BIB:
        defaults = {k: ('' if v == str else [] if v == list else {} if v == dict else None) for k, v in BIB.__annotations__.items()}
        return BIB(**{**defaults, **{k: v for k, v in bib.items() if k in BIB.__annotations__}})