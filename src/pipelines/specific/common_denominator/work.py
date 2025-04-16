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

# New enum classes for document comparison
class ComparisonType(Enum):
    IDENTICAL = 'comparison: identical requirements'
    SIMILAR = 'comparison: similar requirements with minor differences'
    DOC_A_STRICTER = 'comparison: document A has stricter requirements'
    DOC_B_STRICTER = 'comparison: document B has stricter requirements'
    CONFLICTING = 'comparison: conflicting requirements'
    UNIQUE_TO_A = 'comparison: requirement only found in document A'
    UNIQUE_TO_B = 'comparison: requirement only found in document B'

class RequirementImportance(Enum):
    CRITICAL = 'importance: critical regulatory requirement'
    HIGH = 'importance: high business impact'
    MEDIUM = 'importance: medium business impact'
    LOW = 'importance: low business impact'
    INFORMATIONAL = 'importance: informational only'

class Comparison(BaseModel):
    requirement_a: str = Field(..., description = 'Extract from document A, transcribed verbatim, cleaned from parsing artifacts if necessary.')
    requirement_b: str = Field(..., description = 'Extract from document B, transcribed verbatim, cleaned from parsing artifacts if necessary. If not found in document B, leave empty.')
    document_a_chunk_id: List[str] = Field(..., description = 'Document A chunk ids, example: "Chunk 321".')
    document_b_chunk_id: List[str] = Field(..., description = 'Document B chunk ids, example: "Chunk 321". If not found in document B, leave empty.')
    comparison_description: str = Field(..., description = 'Compare the requirements and analyze the implications of their differences. Explain precisely what differs and how.')
    comparison_type: ComparisonType = Field(..., description = 'Type of comparison between the requirements')
    requirement_importance: RequirementImportance = Field(..., description = 'Importance of this requirement')
    least_stringent: str = Field(..., description = 'The least stringent version of this requirement that would satisfy both documents. If requirements are conflicting, propose a compromise.')
    notes: Optional[str] = Field(None, description = 'Additional notes or considerations about this comparison.')

class Comparisons(BaseModel):
    comparisons: List[Comparison]

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
>>> Below, extracts of document A (first manufacturer procedure)
>>>

{chunks}

#########################################

>>>
>>> Below, extract of document B (second manufacturer procedure)
>>>

{work['text']}

>>>
>>> Below, the Instructions
>>>

Please compare the two manufacturer procedures and analyze the differences between them, using the provided data structure:

- requirement_a: Extract from document A (verbatim but cleaned if necessary)
- requirement_b: Extract from document B (verbatim but cleaned if necessary). If a matching requirement is not found in document B, leave empty.
- document_a_chunk_id: Document A chunk ids
- document_b_chunk_id: Document B chunk ids. If not found in document B, leave empty.
- comparison_description: Compare the requirements and explain PRECISELY what differs and how. Analyze the implications of these differences.
- comparison_type: Type of comparison between the requirements (identical, similar, document A stricter, document B stricter, conflicting, unique to A, unique to B)
- requirement_importance: How important is this requirement (critical, high, medium, low, informational)
- least_stringent: Provide the least stringent version of this requirement that would satisfy both documents. If requirements are conflicting, propose a compromise.
- notes (optional): Additional notes or considerations about this comparison.

Focus on identifying matching requirements from both documents and determining which version is less stringent. For each pair of related requirements, provide the least stringent version that would still be acceptable. If a requirement appears in only one document, decide if it should be included in the final least stringent procedure.
"""
        comparisons = None
        p = PROMPT()
        p.add("You are a helpful assistant that NEVER makes any mistakes", role='system')
        p.add(prompt, role='user')
        for retry in range(3):
            try:
                comparisons = self.structured_pipeline(p=p,output_format=Comparisons)
                break
            except ValidationError as e:
                continue
        if comparisons is None:
            raise Exception("Could not parse the comparisons")
        del work['old']
        comparisons = comparisons.dict()['comparisons']
        for i,c in enumerate(comparisons):
            c['comparison_number'] = i
            c['comparison_type'] = c['comparison_type'].name
            c['document_a_chunk_id'] = [re.sub(r'[^0-9]', '', _ or '') for _ in c['document_a_chunk_id']]
            c['document_b_chunk_id'] = [re.sub(r'[^0-9]', '', _ or '') for _ in c['document_b_chunk_id']]
            c['requirement_importance'] = c['requirement_importance'].name
            
            # Process document A location information
            prefix_a = []
            if c['document_a_chunk_id']:
                for _ in c['document_a_chunk_id']:
                    try:
                        chunk_id = int(_)
                        chunk = old[chunk_id]
                        
                        doc_a_page_start = chunk['page_start']
                        doc_a_page_end = chunk['page_end']
                        doc_a_local_index = chunk['local_index']
                        
                        pp = f'Page {doc_a_page_start} chunk {doc_a_local_index}' if doc_a_page_start == doc_a_page_end else f'Pages {doc_a_page_start}-{doc_a_page_end} chunk {doc_a_local_index}'
                        prefix_a.append(pp)
                    except ValueError:
                        pass
                prefix_a = '' if not prefix_a else f'Location in Document A: {", ".join(prefix_a)}\n---\n'
            c['requirement_a'] = f'{prefix_a}{c["requirement_a"]}'
            c.update(work)
        return JSONL(lines=comparisons)