class HTML:
    def __init__(self, html):
        self.html = html
    def __repr__(self):
        return f"<PDF {len(self.file_as_bytes)} bytes>"
    def __str__(self):
        return repr(self)
    
class Converter:
    @staticmethod
    def to_bytes(html : HTML) -> bytes:
        return bytes(html.html, 'utf-8')
    @staticmethod
    def from_bytes(b: bytes) -> HTML:
        return HTML(b.decode('utf-8'))
    @staticmethod
    def str_preview(html : HTML) -> str:
        return html.html
    @staticmethod
    def len(html : HTML) -> int:
        # in MB
        return max(1, len(html.html) // 1048576)
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='html',
    _class = HTML,
    converter = Converter,
    additional_converters={
        'txt' : lambda x : x.html
        },
    icon = "/icons/html.svg"
)