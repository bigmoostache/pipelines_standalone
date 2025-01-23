from custom_types.PROMPT.type import PROMPT

class Pipeline:
    def __init__(self,
                 role:str,
                 limit:int=0
                 ):
        assert role in {"user", "system", "assistant"}
        self.role = role
        self.limit = limit
    def __call__(self, prompt : str) -> PROMPT:
        p = PROMPT()
        if self.limit:
            prompt = prompt[:self.limit]
        p.add(prompt, role = self.role)
        return p