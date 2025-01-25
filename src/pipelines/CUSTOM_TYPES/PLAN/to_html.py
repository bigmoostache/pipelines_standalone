from custom_types.PLAN.type import Plan
from custom_types.HTML.type import HTML

class Pipeline:
    def __init__(self,
                 css: str,
                 template: str
                 ):
        self.css = css
        self.template = template
    
    def __call__(self, 
            p : Plan
            ) -> HTML:
        return HTML(p.to_html(self.template, self.css))