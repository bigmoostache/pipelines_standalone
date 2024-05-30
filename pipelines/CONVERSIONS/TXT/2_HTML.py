from typing import List
import json
import markdown2
from custom_types.HTML.type import HTML

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Classic HTML Structure</title>
    <style>
__CSS__
    </style>
</head>
<body>
    <main>
__HTML__
    </main>
</body>
</html>
"""
class Pipeline:
    def __init__(self, css : str = ""):
        self.css = css 

    def __call__(self, markdown : str) -> HTML:
        html = markdown2.markdown(markdown) 
        return HTML(TEMPLATE.replace('__HTML__', html).replace('__CSS__', self.css))