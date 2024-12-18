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
    
    @staticmethod
    def len(txt : str) -> int:
        return max(1, len(txt) // 1048576)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='txt',
    _class = TXT,
    converter = Converter,
    additional_converters={
        'json':lambda x : {'__text__':x}
        },
    visualiser = "https://visualizations.croquo.com/txt",
    icon='/icons/txt.svg'
)
