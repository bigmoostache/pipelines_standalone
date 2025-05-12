from pydantic import BaseModel, Field, create_model
from typing import Literal, List, Any, Union, Optional
import random, json
from tqdm.auto import tqdm
from pydantic_core._pydantic_core import ValidationError
from custom_types.PROMPT.type import PROMPT

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
    code                           : Optional[str] = Field(None, description = "Small optional code for this criteria. Shorter than name, no special characters and no spaces.")
    def get_tuple(self):
        return (EXCLUSION, Field(..., description = self.exclusion_criteria_description))

class InclusionCriteria(BaseModel):
    inclusion_criteria_description : str = Field(..., description = "Describe precisely the situation where this inclusion criteria should be applied.")
    name                           : str = Field(..., description = "The name of the selection criteria. Should be upper, no special characters, spaces replaced by underscores and no numbers.")
    code                           : Optional[str] = Field(None, description = "Small optional code for this criteria. Shorter than name, no special characters and no spaces.")
    def get_tuple(self):
        return (INCLUSION, Field(..., description = self.inclusion_criteria_description))

def special_join(vals : List[str]) -> str:
    return '- ' + '\n- '.join(vals)
   
class SELECT(BaseModel):
    selection_criteria : List[Union[ExclusionCriteria, InclusionCriteria]] = Field(..., description = "List of selection criteria") 
    langage            : Optional[str] = Field(None, description = "Language of the selection grid. Possible values are 'en' or 'fr'. Default is 'en'.")
    use_codes          : Optional[bool] = Field(None, description = "If True, the codes will be used in the final decision. If False, the codes will not be used. Default is True.")
    
    def get_model(self):
        return create_model("Data", **{e.name : e.get_tuple() for e in self.selection_criteria})
    
    def __call__(self, 
                 prompt,
                 *,
                 model : str,
                 provider: str = 'openai'
                ):
        from pipelines.LLMS.v3.structured import Providers, Pipeline as StructuredPipeline
        # First two calls
        output_format = self.get_model()
        pipe = lambda : StructuredPipeline(
                            provider=provider,
                            model=model,
                        )(prompt, output_format, mode='structured')
        
        events = []
        for _ in tqdm(range(2)):
            for _ in range(3):
                try:
                    events.append(pipe())
                    break
                except ValidationError:
                    pass
                raise ValueError("Failed to get a valid response from the model.")
            
        # Check if a tie-break is needed
        # We will do that by checking if for any criterion there is a conflict that cannot be resolved by just picking a majority.
        
        # Let's gather all decisions for all criteria
        all_decisions = {}
        for criteria in self.selection_criteria:
            decisions = [event.__dict__[criteria.name].decision for event in events]
            all_decisions[criteria.name] = decisions
        
        # Determine if there's a conflict that requires a third call
        # A "conflict" here means a tie that cannot be resolved between the two initial calls.
        need_third_call = False
        for criteria in self.selection_criteria:
            decisions = all_decisions[criteria.name]
            # If there are exactly 2 calls, a conflict would be a direct contradiction:
            # For ExclusionCriteria: one says EXCLUDE and the other says KEEP or EXCL_MAYBE (i.e., no agreement)
            # For InclusionCriteria: one says INCLUDE and the other says NO_INCLUDE or INCL_MAYBE (i.e., no agreement)
            # Or any scenario where they differ.
            
            if len(set(decisions)) > 1:
                # More than one unique decision across the two calls means no unanimous agreement.
                # We will perform a tie-break by making a third call.
                need_third_call = True
                break
        
        # If needed, make a third call
        if need_third_call:
            for _ in range(3):
                try:
                    events.append(pipe())
                    break
                except ValidationError:
                    pass
                raise ValueError("Failed to get a valid response from the model.")
        
        # Now determine the final decisions
        # If we called three times, we have at most a 3-way vote.
        # If we have only two calls, we have a 2-way decision.
        
        res = {}
        recap = []
        for criteria in self.selection_criteria:
            if isinstance(criteria, ExclusionCriteria):
                is_exclusion = True
                justification_field = "e_justification"
                unsure_decision = EXCL_MAYBE
            else:
                is_exclusion = False
                justification_field = "i_justification"
                unsure_decision = INCL_MAYBE
            
            decisions = [event.__dict__[criteria.name].decision for event in events]
            
            # Count the occurrences of each decision
            decision_counts = {}
            for d in decisions:
                decision_counts[d] = decision_counts.get(d, 0) + 1
            
            # If we did not go for third call, we have 2 votes, otherwise 3.
            total_calls = len(events)
            
            # Sort decisions by their count
            sorted_decisions = sorted(decision_counts.items(), key=lambda x: x[1], reverse=True)
            
            if len(sorted_decisions) == 0:
                # No decisions made; default to 'unsure'
                final_decision = UNSURE
                score = 0
            elif len(sorted_decisions) == 1:
                # Only one unique decision
                final_decision, count = sorted_decisions[0]
                score = (count / total_calls) * 100
            else:
                # There are multiple different decisions
                top_decision, top_count = sorted_decisions[0]
                second_decision, second_count = sorted_decisions[1]
                
                if top_count > second_count:
                    # Clear winner
                    final_decision = top_decision
                    score = (top_count / total_calls) * 100
                else:
                    # If there's still a tie even after the third call, we resort to the unsure logic.
                    # If uncertain, default to the "maybe" decision.
                    final_decision = unsure_decision
                    score = (top_count / total_calls) * 100
            
            # Compile justification strings
            justification = special_join([
                f'Decision: {event.__dict__[criteria.name].decision} - {event.__dict__[criteria.name].__dict__[justification_field]}' 
                for event in events
            ])
            # Populate the results
            res[criteria.name] = final_decision
            
            if criteria.code is not None and self.use_codes:
                letter = 'E' if is_exclusion else 'I'
                if final_decision in {EXCLUDE, INCLUDE}:
                    res[f'{criteria.name}_code'] = f'{criteria.code} ({letter})'
                    recap.append(f'{criteria.code} ({letter})')
                elif final_decision == EXCL_MAYBE:
                    res[f'{criteria.name}_code'] = f'{criteria.code} ({letter}) - unsure'
                    recap.append(f'{criteria.code} ({letter}) - unsure')
                elif final_decision == INCL_MAYBE:
                    res[f'{criteria.name}_code'] = f'{criteria.code} ({letter}) - unsure'
                    recap.append(f'{criteria.code} ({letter}) - unsure')
                else:
                    res[f'{criteria.name}_code'] = ''
            res[f'{criteria.name}_score'] = score
            res[f'{criteria.name}_justification'] = justification
            
        inclusion_decisions = [res[c.name] for c in self.selection_criteria if isinstance(c, InclusionCriteria)]
        exclusion_decisions = [res[c.name] for c in self.selection_criteria if isinstance(c, ExclusionCriteria)]
        
        # Determine overall inclusion/exclusion flags
        if any(_==INCLUDE for _ in inclusion_decisions):
            res['at_least_one_inclusion_criteria_is_respected'] = 'true'
        elif all(_==INCL_MAYBE for _ in inclusion_decisions) and len(inclusion_decisions) > 0:
            res['at_least_one_inclusion_criteria_is_respected'] = UNSURE
        else:
            res['at_least_one_inclusion_criteria_is_respected'] = 'false'
            
        if len(inclusion_decisions) > 0:
            if all(_==INCLUDE for _ in inclusion_decisions):
                res['all_inclusion_criteria_are_respected'] = 'true'
            elif any(_==NO_INCLUDE for _ in inclusion_decisions):
                res['all_inclusion_criteria_are_respected'] = 'false'
            else:
                res['all_inclusion_criteria_are_respected'] = UNSURE
        else:
            # If no inclusion criteria, default to false (no criteria to respect)
            res['all_inclusion_criteria_are_respected'] = 'false'
        
        if any(_==EXCLUDE for _ in exclusion_decisions):
            res['at_least_one_exclusion_criteria_is_respected'] = 'true'
        elif any(_==EXCL_MAYBE for _ in exclusion_decisions) and len(exclusion_decisions) > 0:
            res['at_least_one_exclusion_criteria_is_respected'] = UNSURE
        else:
            res['at_least_one_exclusion_criteria_is_respected'] = 'false'
        if self.use_codes:
            res['recap'] = ', '.join(recap)
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
        'json':lambda x : x.model_dump()
        },
    icon='/micons/deepsource.svg',
    visualiser = "https://vis.deepdocs.net/select",
)