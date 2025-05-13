from custom_types.PLAN.type import Plan
from pipelines.utils.yaml import robust_safe_load
from pipelines.CUSTOM_TYPES.PLAN.plan_output import Pipeline as LLMPlanOutputPipeline
from custom_types.PROMPT.type import PROMPT
from pipelines.LLMS.v3.client import Providers

class Pipeline:
    def __init__(self,
                 model : str = "gpt-4o",
                 base_url : str = "https://api.openai.com/v1",
                 provider: Providers = "openai",
                 temperature : float = 1,
                 top_p : float = 1
                 ):
        self.pipeline = lambda p : LLMPlanOutputPipeline(
            provider=provider, 
            model=model
        )(p)
    
    def __call__(self, 
            t : str
            ) -> Plan:
        try:
            dico = robust_safe_load(t)
            dico = dico['document']
            return Plan.parse_obj(dico)
        except:
            prompt = PROMPT()
            prompt.add(f'{t}\n\n---\n\nPlease rewrite this plan verbatim in the provided data structure.', 'user')
            return self.pipeline(prompt)