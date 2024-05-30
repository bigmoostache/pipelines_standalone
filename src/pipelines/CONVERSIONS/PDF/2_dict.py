from custom_types.PDF.type import PDF

class Pipeline:
    def __init__(self, param: str = "PDF"):
        self.param = param 

    def __call__(self, pdf : PDF) -> dict:
        return {self.param : pdf.file_as_bytes}