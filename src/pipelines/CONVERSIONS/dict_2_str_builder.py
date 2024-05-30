import re

class Pipeline:

    def __init__(self, _format : str):
        self.format = _format
        self.parameters = re.findall(r"__([A-Za-zÀ-ÖØ-öø-ÿ_-]+)__", self.format)

    def __call__(self, json : dict) -> str:
        _format = self.format
        for param in self.parameters:
            _format = _format.replace(f"__{param}__", str(json.get(param, "unknown")))
        return _format