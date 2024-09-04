
class TYPE:
    def __init__(self,
                 extension : str,
                 _class,
                 converter,
                 inputable : bool = True,
                 additional_converters : dict = {},
                 visualiser = "",
                 icon = "document" # material icon name, see https://material.io/resources/icons/
            ):
        self.extension = extension
        self.customclass = _class
        self.converter = converter
        self.inputable = inputable
        self.additional_converters = additional_converters
        self.visualiser = visualiser
        self.icon = icon