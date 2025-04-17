
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

class Pipeline:
    def __init__(self, css: str = ''):
        self.css = css
    def __call__(self,
                doc: dict,
                sections_contents: dict
                ) -> HTML:
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
            html=f'<html><head><style>{self.css}</style></head><body>{html}</body></html>'
            )