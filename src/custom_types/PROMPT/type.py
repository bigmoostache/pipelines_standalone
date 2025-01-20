from typing import Literal
import json
from custom_types.JSONL.type import JSONL
class PROMPT:
    def __init__(self):
        self.messages = []
    def add(self, message : str, 
            role : Literal["user", "system", "assistant"] = "user"):
        self.messages.append({"role" : role, "content" : message})
    def truncate(self, max_chars: int):
        """
        Truncates messages to ensure the total character count is below max_chars.
        Algorithm:
        - Truncate the longest message first
        - If that is not enough, move to the next longest message
        """
        total_length = sum(len(msg['content']) for msg in self.messages)

        if total_length <= max_chars:
            return  # Already under the limit

        # Keep track of original indexes
        indexed_messages = list(enumerate(self.messages))

        # Sort messages by the length of their content (descending)
        indexed_messages.sort(key=lambda item: len(item[1]['content']), reverse=True)

        for index, msg in indexed_messages:
            if total_length <= max_chars:
                break

            # Calculate how much we need to truncate
            excess = total_length - max_chars

            # Truncate the current message content
            current_length = len(msg['content'])
            truncate_length = min(current_length, excess)
            self.messages[index]['content'] = msg['content'][:current_length - truncate_length]

            # Update total length
            total_length -= truncate_length

        # No need to restore order as we only modified the original list using indexes
        
class Converter:
    extension = 'prompt'
    @staticmethod
    def to_bytes(p : PROMPT) -> bytes:
        _json = json.dumps(p.messages)
        return bytes(_json, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> PROMPT:
        loaded_str = b.decode('utf-8')
        x =  json.loads(loaded_str)
        p = PROMPT()
        p.messages = x
        return p
    @staticmethod
    def str_preview(p: PROMPT) -> str:
        return json.dumps(p.messages, indent = 2)
    
    @staticmethod
    def len(p : PROMPT) -> int:
        # in K words
        return sum*([len(x['content'].split()) for x in p.messages]) // 1000
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='prompt',
    _class = PROMPT,
    converter = Converter,
    additional_converters={
        'jsonl':lambda x : JSONL(x.messages)
        },
    icon='/micons/coffee.svg'
)