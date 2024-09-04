class Converter:
    @staticmethod
    def to_bytes(boolean : bool) -> bytes:
        return bytes(boolean)
    @staticmethod
    def from_bytes(b: bytes) -> bool:
        return bool(b)
    @staticmethod
    def str_preview(boolean: bool) -> str:
        return str(boolean)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='bool',
    _class = bool,
    converter = Converter,
    icon = "velite"
)