from custom_types.PROMPT.type import PROMPT
import re

class Pipeline:
    def __init__(self,
                 new_param: str = 'missing_tags' 
                 ):
        self.new_param = new_param

    def __call__(self, 
                references : str,
                prompt: PROMPT,
                dico: dict
                ) -> dict:
        simple_pattern = r"<ref (\d+) *\/>"
        double_pattern = r"<ref (\d+) *: *(\d+) *\/?>"
        simple_refs = re.findall(simple_pattern, references)
        double_refs = re.findall(double_pattern, references)
        all_refs = set(simple_refs + [_ for _, __ in double_refs])
        
        redaction = prompt.messages[-1]['content']
        redaction_simple_refs = re.findall(simple_pattern, redaction)
        redaction_double_refs = re.findall(double_pattern, redaction)
        redaction_all_refs = set(redaction_simple_refs + [_ for _, __ in redaction_double_refs])
        
        missing_tags = list(all_refs - redaction_all_refs)
        missing_tags = [f'<ref {a}/>' for a in missing_tags]
        missing_tags = ', '.join(missing_tags)
        
        invented_double_refs = list(set(redaction_double_refs) - set(double_refs))
        invented_double_refs = [f'<ref {a} : {b}/>' for a, b in invented_double_refs]
        
        invented_simple_refs = list(set(redaction_simple_refs) - set(simple_refs))
        invented_simple_refs = [f'<ref {a}/>' for a in invented_simple_refs]
        
        invented = ', '.join(invented_double_refs + invented_simple_refs)
        
        res = f'Missing tags: {missing_tags}'
        if invented:
            res += f'\n\nInvented tags TO ABSOLUTELY REMOVE: {invented}'
        dico[self.new_param] = res
        return dico