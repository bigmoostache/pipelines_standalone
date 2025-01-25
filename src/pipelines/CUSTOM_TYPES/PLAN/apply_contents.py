from typing import List
from custom_types.PLAN.type import Plan

def count_leading_hashes(s):
    count = 0
    for char in s:
        if char == '#':
            count += 1
        else:
            break
    return count

# Example usage:
input_string = "###This is a test"
print("Number of leading #:", count_leading_hashes(input_string))

class Pipeline:
    def __init__(self, 
                 add_lead_hashes : bool = False,
                ):
        self.add_lead_hashes = add_lead_hashes
    
    def __call__(self, 
            p : Plan,
            sections : List[Plan]
            ) -> Plan:
        sections = {_.section_id: _ for _ in sections}
        def process(_plan: Plan, depth = 1):
            if self.add_lead_hashes:
                n_hashes = count_leading_hashes(_plan.prefix)
                if n_hashes > depth:
                    n_to_remove = n_hashes - depth
                    _plan.prefix = _plan.prefix[n_to_remove:]
                elif n_hashes < depth:
                    _plan.prefix = '#' * (depth - n_hashes) + _plan.prefix
                    
            if _plan.section_type != 'leaf':
                for _ in _plan.contents.subsections:
                    process(_, depth + 1)
            else:
                if _plan.section_id in sections:
                    _plan.text = sections[_plan.section_id].text
        process(p)
        return p