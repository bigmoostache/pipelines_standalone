from utils.data.file_systems.get_file_system import FS
import pandas as pd
from custom_types.XLSX.type import Converter, XLSX

class Pipeline:
    def __init__(self):
        self.converter = Converter

    def __call__(self, metadata : dict) -> XLSX:
        file_id = metadata['file_id']
        file_system = FS(metadata['file_system'])
        file = file_system.read_bytes(file_id)
        return self.converter.from_bytes(file)
