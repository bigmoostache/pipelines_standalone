from pydantic import BaseModel, Field, create_model
from typing import Literal, List, Any, Union
import random, json, openai
from tqdm.auto import tqdm

EXCLUDE = 'exclude'
KEEP = 'keep'
EXCL_MAYBE = 'unsure, so keep for now'
EXL_TOGETHER = f'"{EXCLUDE}". "{KEEP}" or "{EXCL_MAYBE}"'

INCLUDE = 'include'
NO_INCLUDE = 'do not include'
INCL_MAYBE = 'unsure, so include for now'
INCL_TOGETHER = f'"{INCLUDE}". "{NO_INCLUDE}" or "{INCL_MAYBE}"'

UNSURE = 'unsure'

class EXCLUSION(BaseModel):
    e_justification  : str = Field(..., description = f'Analyse the article to determine whether or not it should be excluded. Your analysis should be highly detailed and precise: at least a full paragraph, weighing the pros and cons of whether or not the article should be excluded based on this specific criteria only. Only at THE END of your justification should you state your final decision. If you fail to deliver a complete and detailed justification, or that your decision comes at the beginning of your justification, you will be heavily penalized and will be required to redo the task. Possible decisions are {EXL_TOGETHER}.')
    decision       : Literal[EXCLUDE, KEEP, EXCL_MAYBE] = Field(..., description = 'Your final action. Inconsistency with the justification above would lead to dramatic consequences and heavily penalized notation of your response, so make sure your answer fits the justification you provided.')
class INCLUSION(BaseModel):
    i_justification : str = Field(..., description = f'Analyse the article to determine whether or not it verifies this inclusion criteria. Your analysis should be highly detailed and precise: at least a full paragraph, weighing the pros and cons of whether or not the article should be included based on this specific criteria only. Only at THE END of your justification should you state your final decision. If you fail to deliver a complete and detailed justification, or that your decision comes at the beginning of your justification, you will be heavily penalized and will be required to redo the task. Possible decisions are {INCL_TOGETHER}.')
    decision      : Literal[INCLUDE, NO_INCLUDE, INCL_MAYBE] = Field(..., description = 'Your final decision.  Inconsistency with the justification above would lead to dramatic consequences and heavily penalized notation of your response, so make sure your answer fits the justification you provided.')

class ExclusionCriteria(BaseModel):
    exclusion_criteria_description  : str = Field(..., description = "Describe precisely the situation where this exclusion criteria should be applied.")
    name                            : str = Field(..., description = "The name of the exclusion criteria. Should be upper, no special characters, spaces replaced by underscores and no numbers.")
    def get_tuple(self):
        return (EXCLUSION, Field(..., description = self.exclusion_criteria_description))

class InclusionCriteria(BaseModel):
    inclusion_criteria_description : str = Field(..., description = "Describe precisely the situation where this inclusion criteria should be applied.")
    name                           : str = Field(..., description = "The name of the selection criteria. Should be upper, no special characters, spaces replaced by underscores and no numbers.")
    def get_tuple(self):
        return (INCLUSION, Field(..., description = self.inclusion_criteria_description))

def special_join(vals : List[str]) -> str:
    return '- ' + '\n- '.join(vals)
   
class SELECT(BaseModel):
    selection_criteria : List[Union[ExclusionCriteria, InclusionCriteria]] = Field(..., description = "List of selection criteria") 
    
    def get_model(self):
        return create_model("Data", **{e.name : e.get_tuple() for e in self.selection_criteria})
    
    def __call__(self, 
                 messages,
                 *,
                 openai_api_key : str,
                 model : str, 
                 rerolls : int = 1
                ):
        client = openai.OpenAI(api_key=openai_api_key)
        events = [
            client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=self.get_model()
            ).choices[0].message.parsed
            for _ in tqdm(range(rerolls))
        ]
        res = {}
        for criteria in self.selection_criteria:
            # Extract all decisions for the current criteria
            decisions = [event.__dict__[criteria.name].decision for event in events]
            decision_counts = {}
            for decision in decisions:
                decision_counts[decision] = decision_counts.get(decision, 0) + 1
            
            # Sort decisions by count in descending order
            sorted_decisions = sorted(decision_counts.items(), key=lambda x: x[1], reverse=True)
            
            if len(sorted_decisions) == 0:
                # No decisions made; default to 'unsure'
                final_decision = UNSURE
                score = 0
            elif len(sorted_decisions) == 1:
                # Only one unique decision
                final_decision, count = sorted_decisions[0]
                score = (count / rerolls) * 100
            else:
                top_decision, top_count = sorted_decisions[0]
                second_decision, second_count = sorted_decisions[1]
                
                if top_count > second_count:
                    # Clear winner
                    final_decision = top_decision
                    score = (top_count / rerolls) * 100
                elif top_count == second_count:
                    # Tie between top two decisions
                    # Determine the 'unsure' decision based on criteria type
                    if isinstance(criteria, ExclusionCriteria):
                        unsure_decision = EXCL_MAYBE
                    else:
                        unsure_decision = INCL_MAYBE
                    
                    # Calculate the probability of 'unsure'
                    unsure_count = decision_counts.get(unsure_decision, 0)
                    unsure_probability = unsure_count / rerolls
                    
                    # Decide based on probability
                    if random.random() < unsure_probability:
                        final_decision = unsure_decision
                        score = unsure_probability * 100
                    else:
                        # If not choosing 'unsure', randomly choose between the tied decisions
                        final_decision = random.choice([top_decision, second_decision])
                        score = (top_count / rerolls) * 100
                else:
                    # More than two decisions with different counts
                    final_decision = top_decision
                    score = (top_count / rerolls) * 100
            
            # Compile justification strings
            if isinstance(criteria, ExclusionCriteria):
                justification = special_join([f'Decision: {event.__dict__[criteria.name].decision} - {event.__dict__[criteria.name].e_justification}' for event in events])
            else:
                justification = special_join([f'Decision: {event.__dict__[criteria.name].decision} - {event.__dict__[criteria.name].i_justification}' for event in events])
            
            # Populate the results
            res[f'{criteria.name}'] = final_decision
            res[f'{criteria.name}_score'] = score
            res[f'{criteria.name}_justification'] = justification
            
        inclusion_decisions = [_ for _ in self.selection_criteria if isinstance(_, InclusionCriteria)]
        exclusion_decisions = [_ for _ in self.selection_criteria if isinstance(_, ExclusionCriteria)]
        
        inclusion_decisions = [res[c.name] for c in self.selection_criteria if isinstance(c, InclusionCriteria)]
        exclusion_decisions = [res[c.name] for c in self.selection_criteria if isinstance(c, ExclusionCriteria)]
        
        if any(_==INCLUDE for _ in inclusion_decisions):
            res['at_least_one_inclusion_criteria_is_respected'] = 'true'
        elif all(_==INCL_MAYBE for _ in inclusion_decisions):
            res['at_least_one_inclusion_criteria_is_respected'] = UNSURE
        else:
            res['at_least_one_inclusion_criteria_is_respected'] = 'false'
            
        if all(_==INCLUDE for _ in inclusion_decisions):
            res['all_inclusion_criteria_are_respected'] = 'true'
        elif any(_==NO_INCLUDE for _ in inclusion_decisions):
            res['all_inclusion_criteria_are_respected'] = 'false'
        else:
            res['all_inclusion_criteria_are_respected'] = UNSURE
        
        if any(_==EXCLUDE for _ in exclusion_decisions):
            res['at_least_one_exclusion_criteria_is_respected'] = 'true'
        elif any(_==EXCL_MAYBE for _ in exclusion_decisions):
            res['at_least_one_exclusion_criteria_is_respected'] = UNSURE
        else:
            res['at_least_one_exclusion_criteria_is_respected'] = 'false'
        return res
            
class Converter:
    @staticmethod
    def to_bytes(obj : SELECT) -> bytes:
        return bytes(obj.model_dump_json(), encoding = 'utf-8')
         
    @staticmethod
    def from_bytes(obj : bytes) -> 'SELECT':
        return SELECT.parse_obj(json.loads(obj.decode('utf-8')))
    
    @staticmethod
    def len(obj : SELECT) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='select',
    _class = SELECT,
    converter = Converter,
    additional_converters={
        'json':lambda x : x.to_dict()
        },
    icon='/micons/deepsource.svg',
    visualiser = "https://visualizations.croquo.com/select",
)