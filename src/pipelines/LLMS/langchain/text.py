from custom_types.PROMPT.type import PROMPT
from custom_types.LLM.type import LLM

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 p : PROMPT,
                 llm : LLM
                 ) -> str:
        return llm(p.messages).content

