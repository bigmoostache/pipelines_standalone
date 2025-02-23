from utils.data.file_systems.get_file_system import FS
from custom_types.PDF.type import Converter, PDF

class Pipeline:
    def __init__(self):
        self.converter = Converter

    def __call__(self, metadata : dict) -> PDF:
        file_id = metadata['file_id']
        file_system = FS(metadata['file_system'])
        file = file_system.read_bytes(file_id)
        pdf = self.converter.from_bytes(file)
        pdf.file_name = metadata.get('file_name', 'document.pdf')
        return pdf
