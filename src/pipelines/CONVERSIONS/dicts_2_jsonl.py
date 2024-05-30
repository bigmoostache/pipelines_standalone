from typing import List 
import dotenv
from custom_types.JSONL.type import JSONL

dotenv.load_dotenv()

class Pipeline:

    def __init__(self):
        pass

    def __call__(self, json : List[dict]) -> JSONL:
        return JSONL(json)