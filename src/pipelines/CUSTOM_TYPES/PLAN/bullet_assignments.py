from custom_types.PLAN.type import Plan, Reference
from custom_types.JSONL.type import JSONL
from pipelines.utils.simplify import simplify

class Pipeline:
    def __init__(self, 
                max_groups_per_element : int = 1,
                elements_per_group : int = 1,
                min_elements_per_list : int = 1,
                ):
        self.__dict__.update(locals())
        self.__dict__.pop("self")
        
    
    def __call__(self, 
            p : Plan,
            ) -> JSONL:
        assert p.lucario is not None, 'lucario is None'
        p.lucario.update()
        sections = JSONL(lines = p.aggregate_bullet_points())
        results = p.lucario.anchored_top_k(
            queries = [_ for section in sections.lines for _ in section['bullets']],
            groups_ids = [i for i,section in enumerate(sections.lines) for _ in section['bullets']],
            max_groups_per_element=self.max_groups_per_element,
            elements_per_group=self.elements_per_group,
            min_elements_per_list=self.min_elements_per_list
        )
        for r in results:
            r['section_id'] = [sections.lines[_]['section_id'] for _ in r['assigned_to']]
        return JSONL(lines = results)