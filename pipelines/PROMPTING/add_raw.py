from custom_types.PROMPT.type import PROMPT

class Pipeline:
    def __init__(self,
                 role:str
                 ):
        assert role in {"user", "system", "assistant"}
        self.role = role

    def __call__(self, p : PROMPT, prompt : str) -> PROMPT:
        p.add(prompt, role = self.role)
        return p