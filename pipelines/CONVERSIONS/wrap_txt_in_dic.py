import requests
import json
import re

class Pipeline:
    def __init__(self, param : str):
        self.param = param

    def __call__(self, text1 : str) -> dict:
        return {self.param:text1}