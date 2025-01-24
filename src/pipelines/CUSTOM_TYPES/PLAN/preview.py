from custom_types.PLAN.type import Plan

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,
                focus: bool = False,
                include_all_bullets: bool = True
                ):
        self.focus = focus
        self.include_all_bullets = include_all_bullets
    
    def __call__(self, 
            section : Plan,
            full_plan: Plan
            ) -> str:
        def tostring(plan, focus_id : str = None, include_all_bullets : bool = True):
            isfocus = focus_id == plan.section_id
            if plan.section_type == 'leaf':
                if include_all_bullets or isfocus:
                    bullets = '\t- ' + '\n\t- '.join(plan.contents.leaf_bullet_points)
                else:
                    bullets = ''
                abstract = plan.abstract
                title = plan.title
                r = f'{plan.prefix} {plan.title}\n\t{plan.abstract}\n{bullets}'
                if not isfocus:
                    return r
                return '\n>>>// Current section of interest \n>>>' + r.replace('\n', '\n>>>')
            else:
                children = [tostring(x, focus_id, include_all_bullets) for x in plan.contents.subsections]
                children = '\n'.join(children)
                children = '\t' + children.replace('\n>>>', '__REP__').replace('\n', '\n\t').replace('__REP__', '\n>>>\t')
                return f'{plan.prefix} {plan.title}\n{plan.abstract}\n{children}'
        focus = section.section_id if self.focus else None
        return tostring(full_plan, focus, self.include_all_bullets)