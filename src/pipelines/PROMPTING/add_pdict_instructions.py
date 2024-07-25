from custom_types.PROMPT.type import PROMPT
from custom_types.PDICT.type import PDICT

class Pipeline:
    def __init__(self,
                 role:str,
                 before : str,
                 after : str,
                 ):
        assert role in {"user", "system", "assistant"}
        self.role = role
        self.before = before
        self.after = after


    def __call__(self, p : PROMPT, pdict : PDICT) -> PROMPT:
        p.add(
            self.before + str(pdict) + self.after, 
            role = self.role)
        return p