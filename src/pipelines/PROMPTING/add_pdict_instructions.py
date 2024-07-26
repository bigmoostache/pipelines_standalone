from custom_types.PROMPT.type import PROMPT
from custom_types.PDICT.type import PDICT

class Pipeline:
    def __init__(self,
                 role:str,
                 before : str,
                 after : str,
                 ask_justifications : bool = False
                 ):
        assert role in {"user", "system", "assistant"}
        self.role = role
        self.before = before
        self.after = after
        self.ask_justifications = ask_justifications


    def __call__(self, p : PROMPT, pdict : PDICT) -> PROMPT:
        p.add(
            self.before + pdict.__str__(ask_justifications = self.ask_justifications) + self.after, 
            role = self.role)
        return p