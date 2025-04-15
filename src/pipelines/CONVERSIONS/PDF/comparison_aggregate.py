from custom_types.JSONL.type import JSONL
import numpy as np
import os, re
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from openai import OpenAI
from pydantic_core._pydantic_core import ValidationError
import re
from pipelines.LLMS.v3.client import Providers
from pipelines.LLMS.v3.structured import Pipeline as StructuredPipeline
from custom_types.PROMPT.type import PROMPT

def remove_exact_chain(s):
    def repl(m):
        num = int(m.group(1))
        dashes = m.group(2)
        # Only remove if the dash count equals the specified number.
        return "" if len(dashes) == num else m.group(0)
    
    # Match a literal '{', capture one or more digits, then a literal '}', then one or more dashes.
    return re.sub(r'\{(\d+)\}(-+)', repl, s)

# Example usage:
s = "Example text {20}-------------------- and more text."



class ChangeType(Enum):
    ADDITION = 'change: addition'
    NO_CHANGE = 'change: no change'
    FORMULATION = 'change: small change in formulation but not in meaning'
    SMALL = 'change: small change in meaning'
    SIGNIFICANT = 'change: significant change in meaning'

class ChangeImportance(Enum):
    NO_CHANGE = 'importance: no change, so not applicable'
    NONE = 'importance: totally unsignificant'
    VOCABULARY = 'importance: simple vocabulary update'
    NOTIFICATION = 'importance: deserves notification'
    WARNING = 'importance: deserves warning'
    DANGER = 'importance: major modification deserving attention'

class Change(BaseModel):
    new_formulation: str = Field(..., description = 'Extract of the new document, transcribed verbatim, but cleaned from parsing artifacts if necessary.')
    old_formulation: str = Field(..., description = 'Older version (cleaned if necessary), optional if not found in other version. Be careful: this might include several chunks of the older version, coming from different pages or sections. If so, separate them with "\n---\n". If absolutely, totally completely new, just leave this field empty. But try to put something if you can.')
    old_formulation_chunk_id: List[str] = Field(..., description = 'Older version chunk ids, example: "Chunk 321".')
    changes_description: str = Field(..., description = 'Compare the new and the old version and analyse the implications of those changes. Try to make this analysis as useful as possible for the user, PRECISELY explaning what changes and how.')
    type_of_change: ChangeType = Field(..., description = 'Level at which this text was modified')
    importance_of_change : ChangeImportance = Field(..., description = 'Importance for the user')
    CTA: Optional[str] = Field(..., description = 'Call to action to the user if needed. Make this CTA short and super synthetic.')

class Changes(BaseModel):
    changes: List[Change]

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "gpt-4.1",   
        ):
        self.structured_pipeline = pipeline = StructuredPipeline(provider=provider, model=model)
    def __call__(self, work : dict) -> JSONL:
        old = work['old']
        old = {_['chunk_id']:_ for _ in old}
        chunks = '\n\n'.join([f'>>>>>>>>>>>>>>>>>>>>>>>>>>> Chunk {o["chunk_id"]}\n{remove_exact_chain(o["text"])}' for o in work["old"]])
        prompt = f""">>>
>>> Below, extracts of the older versions of the document
>>>

{chunks}

#########################################

>>>
>>> Below, extract of new document whose changes you should analyse
>>>

{work['text']}

>>>
>>> Below, the Instructions
>>>

Please analyse the changes from the new document, extracting the changes in the provided data structure:
- new_formulation: the new version (verbatim but cleaned if necessary)
- old_formulation (optional): older version (same), optional if not found in other version
- old_formulation_chunk_id (optional): older version chunk id
- type_of_change: type of change: Addition, No change, change in formulation, small change in meaning, major change in meaning
- importance_of_change: how important could this change potentially be for the user?
- CTA (optional): call to action to the user if needed. make this CTA short and super synthetic

"""
        changes = None
        p = PROMPT()
        p.add("You are a helpful assistant that NEVER makes any mistakes", role='system')
        p.add(prompt, role='user')
        for retry in range(3):
            try:
                changes = self.structured_pipeline(p=p,output_format=Changes)
                break
            except ValidationError as e:
                continue
        if changes is None:
            raise Exception("Could not parse the changes")
        del work['old']
        changes = changes.dict()['changes']
        for i,c in enumerate(changes):
            c['change_number'] = i
            c['type_of_change'] = c['type_of_change'].name
            c['old_formulation_chunk_id'] = [re.sub(r'[^0-9]', '', _ or '') for _ in c['old_formulation_chunk_id']]
            c['importance_of_change'] = c['importance_of_change'].name
            prefix = []
            if c['old_formulation_chunk_id']:
                for _ in c['old_formulation_chunk_id']:
                    try:
                        chunk_id = int(_)
                        chunk = old[chunk_id]
                        
                        old_formulation_page_start = chunk['page_start']
                        cold_formulation_page_end = chunk['page_end']
                        old_formulation_local_index = chunk['local_index']
                        
                        pp = f'Page {old_formulation_page_start} chunk {old_formulation_local_index}' if old_formulation_page_start == cold_formulation_page_end else f'Pages {old_formulation_page_start}-{cold_formulation_page_end} chunk {old_formulation_local_index}'
                        prefix.append(pp)
                    except ValueError:
                        pass
                prefix = '' if not prefix else f'Location: {", ".join(prefix)}\n---\n'
            c['old_formulation'] = f'{prefix}{c["old_formulation"]}'
            c.update(work)
        return JSONL(lines=changes)