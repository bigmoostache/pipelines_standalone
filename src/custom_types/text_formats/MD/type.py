from pydantic import BaseModel
class MD:
    md: str
    
class Converter:
    @staticmethod
    def to_bytes(MD) -> bytes:
        return bytes(MD.md, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> MD:
        return MD(md=b.decode('utf-8'))
    @staticmethod
    def len(txt : MD) -> int:
        return max(1, len(MD.md) // 1048576)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='md',
    _class = MD,
    converter = Converter,
    additional_converters={
        'json':lambda x : {'__text__':x}
        },
    visualiser = "https://vis.deepdocs.net/md"
)
