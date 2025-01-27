from custom_types.JSONL.type import JSONL
import numpy as np
import os
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from openai import OpenAI

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
    old_formulation: Optional[str] = Field(..., description = 'Older version (cleaned if necessary), optional if not found in other version')
    old_formulation_chunk_id: Optional[str] = Field(..., description = 'Older version chunk id, example: "Chunk 321"')
    changes_description: str = Field(..., description = 'Compare the new and the old version and analyse the implications of those changes.')
    type_of_change: ChangeType = Field(..., description = 'Level at which this text was modified')
    importance_of_change : ChangeImportance = Field(..., description = 'Importance for the user')
    CTA: Optional[str] = Field(..., description = 'call to action to the user if needed. make this CTA short and super synthetic')

class Changes(BaseModel):
    changes: List[Change]

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self):
        pass
    def __call__(self, work : dict) -> JSONL:
        old = work['old']
        old = {_['chunk_id']:_ for _ in old}
        chunks = '\n\n'.join([f'>>>>>>>>>>>>>>>>>>>>>>>>>>> Chunk {o["chunk_id"]}\n{o["text"]}' for o in work["old"]])
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
        client = OpenAI(api_key=os.environ.get("openai_api_key"))

        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that NEVER makes any mistakes"},
                {"role": "user", "content": prompt}
            ],
            response_format=Changes,
        )

        changes = completion.choices[0].message.parsed
        del work['old']
        changes = changes.dict()['changes']
        for i,c in enumerate(changes):
            c['change_number'] = i
            c['type_of_change'] = c['type_of_change'].name
            c['old_formulation_chunk_id'] = (c['old_formulation_chunk_id'] or '').lower().replace('chunk ', '')
            c['importance_of_change'] = c['importance_of_change'].name
            if c['old_formulation_chunk_id']:
                try:
                    chunk_id = int(c['old_formulation_chunk_id'])
                    chunk = old[chunk_id]
                    c['old_formulation_page_start'] = chunk['page_start']
                    c['old_formulation_page_end'] = chunk['page_end']
                    c['old_formulation_local_index'] = chunk['local_index']
                    c['old_formulation_raw'] = chunk['text']
                except ValueError:
                    pass
            c.update(work)
        return JSONL(lines=changes)