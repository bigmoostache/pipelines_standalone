import json
from custom_types.JSON.type import BytesEncoder, bytes_decoder

class JSONL:
    def __init__(self, lines):
        self.lines = lines
        
class Converter:
    @staticmethod
    def to_bytes(ent : JSONL) -> bytes:
        return bytes("\n".join([json.dumps(x, cls=BytesEncoder) for x in ent.lines]), 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> JSONL:
        r = b.decode('utf-8')
        if not r:
            return JSONL([])
        return JSONL([json.loads(x, object_hook=bytes_decoder) for x in r.split("\n")])
    @staticmethod
    def str_preview(ent: JSONL) -> str:
        return "\n".join([json.dumps(x, indent=4, cls=BytesEncoder) for x in ent.lines])
    @staticmethod
    def len(ent : JSONL) -> int:
        return len(ent.lines)

from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='jsonl',
    _class = JSONL,
    converter = Converter,
    icon="/icons/js.svg"
)