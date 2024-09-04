BYTES = bytes

class Converter:
    @staticmethod
    def to_bytes(obj) -> bytes:
        return obj
    @staticmethod
    def from_bytes(b: bytes) -> bytes:
        return b
    @staticmethod
    def str_preview(b: bytes) -> str:
        return f"File of {len(b)} bytes"
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='bytes',
    _class = BYTES,
    converter = Converter,
    icon = "assembly"
)