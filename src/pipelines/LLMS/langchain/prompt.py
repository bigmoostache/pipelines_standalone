from custom_types.PROMPT.type import PROMPT
from custom_types.LLM.type import LLM

class Pipeline:
    def __init__(self, role: str = 'assistant'):
        self.role = role
    def __call__(self, 
                 p : PROMPT,
                 llm : LLM
                 ) -> PROMPT:
        p.add(llm(p.messages).content, self.role)
        return p

