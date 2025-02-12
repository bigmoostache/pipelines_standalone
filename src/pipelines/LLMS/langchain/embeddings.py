from custom_types.PROMPT.type import PROMPT
from custom_types.LLM.type import LLM
from typing import List

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, 
                 texts: List[str],
                 llm : LLM
                 ) -> str:
        assert llm.llm_category == 'embeddings', 'LLM category must be embeddings when used in this pipeline'
        return llm(texts)