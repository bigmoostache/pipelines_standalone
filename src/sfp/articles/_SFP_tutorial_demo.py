from utils.data.file_systems.get_file_system import FS
from custom_types.framework_formats.TUTORIAL_DEMO.type import Converter, SimpleGraph

class Pipeline:
    def __init__(self):
        self.converter = Converter

    def __call__(self, metadata : dict) -> SimpleGraph:
        file_id = metadata['file_id']
        file_system = FS(metadata['file_system'])
        file = file_system.read_bytes(file_id)
        return self.converter.from_bytes(file)
