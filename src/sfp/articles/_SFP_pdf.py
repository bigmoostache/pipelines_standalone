from utils.data.file_systems.get_file_system import FS
from custom_types.PDF.type import Converter, PDF
from utils.converter import auto_convert

class Pipeline:
    def __init__(self):
        self.converter = Converter

    def __call__(self, metadata : dict) -> PDF:
        file_id = metadata['file_id']
        file_system = FS(metadata['file_system'])
        return auto_convert(
            metadata.get('file_type', 'pdf'),
            'pdf',
            file_system.read_bytes(file_id)
        )
