from custom_types.text_formats.MD.type import MD

class Pipeline:
    def __init__(self):
        pass 

    def __call__(self, text : str) -> MD:
        return MD(md=text)