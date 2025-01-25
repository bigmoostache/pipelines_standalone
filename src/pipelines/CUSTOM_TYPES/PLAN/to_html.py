from custom_types.PLAN.type import Plan

class Pipeline:
    def __init__(self,
                 css: str,
                 template: str
                 ):
        self.css = css
        self.template = template
    
    def __call__(self, 
            p : Plan
            ) -> Plan:
        return p.to_html(self.template, self.css)