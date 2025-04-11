from utils.data.file_systems.get_file_system import FS
from custom_types.DOCX.type import Converter, DOCX

class Pipeline:
    def __init__(self):
        self.converter = Converter

    def __call__(self, metadata : dict) -> DOCX:
        file_id = metadata['file_id']
        file_system = FS(metadata['file_system'])
        file = file_system.read_bytes(file_id)
        pdf = self.converter.from_bytes(file)
        return pdf
