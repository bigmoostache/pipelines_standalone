TXT = str

class Converter:
    @staticmethod
    def to_bytes(txt) -> bytes:
        return bytes(txt, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> str:
        return b.decode('utf-8')
    @staticmethod
    def str_preview(txt: str) -> str:
        return txt
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='txt',
    _class = TXT,
    converter = Converter,
    visualiser = "https://visuals.croquo.com/txt",
    icon='/icons/txt.svg'
)
