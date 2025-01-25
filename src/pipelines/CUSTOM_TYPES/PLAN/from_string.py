from custom_types.PLAN.type import Plan
from pipelines.utils.yaml import robust_safe_load
from pipelines.CUSTOM_TYPES.PLAN.plan_output import Pipeline as LLMPlanOutputPipeline
from custom_types.PROMPT.type import PROMPT

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self,
                 model : str = "gpt-4o",
                 base_url : str = "https://api.openai.com/v1",
                 temperature : float = 1,
                 top_p : float = 1
                 ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.base_url = base_url
    
    def __call__(self, 
            t : str
            ) -> Plan:
        try:
            dico = robust_safe_load(t)
            dico = dico['document']
            return Plan.parse_obj(dico)
        except:
            prompt = PROMPT()
            prompt.add(f'{t}\n\n Please rewrite this plan verbatim in the provided data structure.', 'user')
            return LLMPlanOutputPipeline(
                model=self.model,
                base_url=self.base_url,
                temperature=self.temperature,
                top_p=self.top_p
            )(t)