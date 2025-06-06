from custom_types.XLSX.type import XLSX
from custom_types.PROMPT.type import PROMPT

class Pipeline:
    def __init__(self, 
        prompt: str = "The column __column__ is plain text, containing data of all sorts. Please create a json schema fitting the data you observe in it, that contains only bool, numbers, categorical (if so detail the categories) and nones. Only define the schema, don't build the deduces new table. Also, please limit yourself to maximum 7 parameters."
        ):
        self.prompt = prompt
        
    def __call__(self,
                xlsx : XLSX,
                p: PROMPT
                ) -> PROMPT:
        assert len(xlsx.sheets.keys()) == 1, "This pipeline only supports single-sheet XLSX files"
        key = list(xlsx.sheets.keys())[0]
        p.add(self.prompt.replace("__column__", key), 'user')
        return p
        