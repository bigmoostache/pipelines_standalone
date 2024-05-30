import requests
import json
import re

class Pipeline:
    def __init__(self, param : str, param2 : str):
        self.param = param
        self.param2 = param2

    def __call__(self, text1 : str, text2 : str) -> dict:
        return {self.param:text1, self.param2:text2}