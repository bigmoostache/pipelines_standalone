class Converter:
    @staticmethod
    def to_bytes(integer : float) -> bytes:
        return bytes(str(integer), 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> float:
        return float(b.decode('utf-8'))
    @staticmethod
    def str_preview(number: float) -> str:
        return str(number)
    @staticmethod
    def len(number : float) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='float',
    _class = float,
    converter = Converter,
    icon = "/icons/exe.svg"
)