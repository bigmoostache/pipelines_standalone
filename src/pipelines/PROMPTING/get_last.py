from custom_types.PROMPT.type import PROMPT

class Pipeline:
    def __init__(self,
                 ):
        pass

    def __call__(self, p : PROMPT) -> str:
        return p.messages[-1]['content']