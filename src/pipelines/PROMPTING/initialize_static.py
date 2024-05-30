from custom_types.PROMPT.type import PROMPT

class Pipeline:
    def __init__(self,
                 role:str,
                 prompt : str
                 ):
        assert role in {"user", "system", "assistant"}
        self.role = role
        self.prompt = prompt


    def __call__(self) -> PROMPT:
        p = PROMPT()
        p.add(self.prompt, role = self.role)
        return p