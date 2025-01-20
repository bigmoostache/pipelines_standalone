class ZIP:
    def __init__(self, zip : bytes):
        self.zip = zip
        
class Converter:
    @staticmethod
    def to_bytes(ent : ZIP) -> bytes:
        return ent.zip
    @staticmethod
    def from_bytes(b: bytes) -> ZIP:
        return ZIP(b)
    @staticmethod
    def str_preview(ent: ZIP) -> str:
        return "No preview available"
    @staticmethod
    def len(ent : ZIP) -> int:
        return len(ent.zip)

from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='zip',
    _class = ZIP,
    converter = Converter,
    icon="/icons/zip.svg"
)