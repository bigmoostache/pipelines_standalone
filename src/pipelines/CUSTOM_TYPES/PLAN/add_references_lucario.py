from custom_types.PLAN.type import Plan
from custom_types.LUCARIO.type import LUCARIO

class Pipeline:
    def __init__(self, 
                 ):
        pass
    
    def __call__(self, 
            p : Plan,
            lucario: LUCARIO
            ) -> Plan:
        p.lucario = lucario
        return p