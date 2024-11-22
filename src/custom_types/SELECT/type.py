from pydantic import BaseModel, Field, create_model
from typing import Literal, List, Any, Union
import random, json, openai
from tqdm.auto import tqdm

EXCLUDE = 'exclude'
KEEP = 'keep'
EXCL_MAYBE = 'unsure, so keep for now'

INCLUDE = 'include'
NO_INCLUDE = 'do not include'
INCL_MAYBE = 'unsure, so include for now'

UNSURE = 'unsure'

class EXCLUSION(BaseModel):
    e_justification  : str = Field(..., description = 'Analyse the article to determine whether or not it should be excluded.')
    decision       : Literal[EXCLUDE, KEEP, EXCL_MAYBE] = Field(..., description = 'Your final action. Inconsistency with the justification above would lead to dramatic consequences and heavily penalized notation of your response, so make sure your answer fits the justification you provided.')
class INCLUSION(BaseModel):
    i_justification : str = Field(..., description = 'Analyse the article to determine whether or not it verifies this inclusion criteria.')
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
        
class SELECT(BaseModel):
    selection_criteria : List[Union[ExclusionCriteria, InclusionCriteria]] = Field(..., description = "List of selection criteria") 
    
    def get_model(self):
        random.shuffle(self.selection_criteria)
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
                model='gpt-4o',
                messages=messages,
                response_format=self.get_model()
            ).choices[0].message.parsed
            for _ in tqdm(range(rerolls))
        ]
        res = {}
        for criteria in self.selection_criteria:
            results = [_.__dict__[criteria.name] for _ in events]
            decisions = [_.decision for _ in results]
            if isinstance(criteria, ExclusionCriteria):
                if len(list(set(decisions))) == 1:
                    value, justification, score = decisions[0], results[0].e_justification, 100
                elif EXCLUDE in decisions and KEEP in decisions:
                    value, justification, score = UNSURE, 'Conflicting choices', 0
                else:
                    unsures = [_ for _ in results if _.decision == EXCL_MAYBE]
                    sures =  [_ for _ in results if _.decision != EXCL_MAYBE]
                    assert len(unsures) + len(sures) == len(results)
                    if len(unsures) > len(sures):
                        value, justification, score = UNSURE, unsures[0].e_justification, 0
                    else:
                        value, justification, score = sures[0].decision, sures[0].e_justification, len(sures) * 100. / len(results) 
            else:
                if len(list(set(decisions))) == 1:
                    value, justification, score = decisions[0], results[0].i_justification, 100
                elif INCLUDE in decisions and NO_INCLUDE in decisions:
                    value, justification, score = UNSURE, 'Conflicting choices', 0
                else:
                    unsures = [_ for _ in results if _.decision == INCL_MAYBE]
                    sures =  [_ for _ in results if _.decision != INCL_MAYBE]
                    assert len(unsures) + len(sures) == len(results)
                    if len(unsures) > len(sures):
                        value, justification, score = UNSURE, unsures[0].i_justification, 0
                    else:
                        value, justification, score = sures[0].decision, sures[0].i_justification, len(sures) * 100. / len(results) 
            res[f'{criteria.name}'] = value
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