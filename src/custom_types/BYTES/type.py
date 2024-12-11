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
    @staticmethod
    def len(b: bytes) -> int:
        # in MB
        return max(1, len(b) // 1048576)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='bytes',
    _class = BYTES,
    converter = Converter,
    icon = "/icons/exe.svg"
)