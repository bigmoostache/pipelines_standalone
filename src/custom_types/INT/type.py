class Converter:
    extension = 'txt'
    @staticmethod
    def to_bytes(integer : int) -> bytes:
        return bytes(str(integer), 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> int:
        return int(b.decode('utf-8'))
    @staticmethod
    def str_preview(integer: int) -> str:
        return str(integer)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='int',
    _class = int,
    converter = Converter,
    icon="database"
)