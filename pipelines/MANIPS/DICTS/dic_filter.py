from typing import List
import re


class Pipeline:
    def __init__(self, key: str, regexp: str, input_flags: str = ""):
        self.key = key

        flags = 0
        if input_flags:
            input_flags = input_flags.lower()
            if "i" in input_flags:
                flags |= re.IGNORECASE
            if "m" in input_flags:
                flags |= re.MULTILINE
            if "x" in input_flags:
                flags |= re.VERBOSE
            if "a" in input_flags:
                flags |= re.ASCII
            if "s" in input_flags:
                flags |= re.DOTALL
            if "l" in input_flags:
                flags |= re.LOCALE

        self.is_not = False
        if regexp[0] == "!":
            self.is_not = True
            regexp = regexp[1:]
        self.regeexp = re.compile(rf"{regexp}", flags)

    def is_match(self, json_element: dict):
        if self.is_not:
            return self.key not in json_element or not self.regeexp.match(
                json_element.get(self.key)
            )
        else:
            return self.key in json_element and self.regeexp.match(
                json_element.get(self.key)
            )

    def __call__(self, json: List[dict]) -> List[dict]:
        res = [json_element for json_element in json if self.is_match(json_element)]
        return res
