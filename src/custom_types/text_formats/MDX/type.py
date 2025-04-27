from pydantic import BaseModel
class MDX:
    mdx: str
    

class Converter:
    @staticmethod
    def to_bytes(MDX) -> bytes:
        return bytes(MDX.mdx, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> MDX:
        return MDX(mdx=b.decode('utf-8'))
    @staticmethod
    def len(txt : MDX) -> int:
        return max(1, len(MDX.mdx) // 1048576)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='mdx',
    _class = MDX,
    converter = Converter,
    additional_converters={
        'json':lambda x : {'__text__':x}
        },
    visualiser = "https://vis.deepdocs.net/md"
)
