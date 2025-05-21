from utils.logger import SQL_F1
from custom_types.framework_formats.TUTORIAL_DEMO.type import Converter, SimpleGraph

class Pipeline:
    def __init__(self):
        self.converter = Converter

    def __call__(self, metadata : dict) -> SimpleGraph:
        file_name = metadata['file_name']
        dataset_id = metadata['dataset_id']
        file, = SQL_F1('SELECT "file_contents" FROM "DatasetsFiles" WHERE "dataset_id" = %s AND "file_name" = %s', (dataset_id, file_name))
        file = bytes(file)
        return self.converter.from_bytes(file)
