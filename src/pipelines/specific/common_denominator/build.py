
from custom_types.PROMPT.type import PROMPT
from custom_types.JSONL.type import JSONL
from custom_types.HTML.type import HTML
from custom_types.trees.gap_analysis.type import ResponseType as Tree_Gap_AnalysisResponseType
from typing import List
import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.smarty import SmartyExtension

template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
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
    def __init__(self, 
                css: str = '',
                template: str = template
                ):
        self.css = css
        self.template = template
    def __call__(self,
                doc: dict,
                sections_contents: dict
                ) -> HTML:
        sections_contents = {
            tuple([int(_) for _ in k.split(',')]): v for k, v in sections_contents.items()
        } # convert back the keys to tuples
        _res = Tree_Gap_AnalysisResponseType.model_validate(doc)
        html = markdown.markdown(
            _res.document_denominator.build(sections_contents, 1, []), 
            extensions=[
                TableExtension(),
                FencedCodeExtension(),
                CodeHiliteExtension(),
                SmartyExtension(),
            ]
        )
        return HTML(
            html=self.template.replace('__HTML__', html).replace('__CSS__', self.css)
            )