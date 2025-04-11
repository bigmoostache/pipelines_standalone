import re

class DOCX:
    def __init__(self, file_as_bytes):
        self.file_as_bytes = file_as_bytes
    def __repr__(self):
        return self.file_as_bytes
    def __str__(self):
        return self.file_as_bytes

class Converter:
    extension = 'docx'
    @staticmethod
    def to_bytes(docx : DOCX) -> bytes:
        return docx.file_as_bytes
    @staticmethod
    def from_bytes(b: bytes) -> DOCX:
        return DOCX(b)
    @staticmethod
    def len(docx : DOCX) -> int:
        return 1

from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='docx',
    _class = DOCX,
    converter = Converter,
    icon="/icons/doc.svg"
)