from custom_types.JSONL.type import JSONL
import numpy as np
import os, re
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
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


class ComparisonType(Enum):
    IDENTICAL = 'comparison: identical requirements'
    SIMILAR = 'comparison: similar requirements with minor differences'
    COMPLEMENTARY = 'comparison: complementary requirements'
    CONFLICTING = 'comparison: conflicting requirements'
    UNIQUE_A = 'comparison: requirement only present in document A'
    UNIQUE_B = 'comparison: requirement only present in document B'

class RequirementStrictness(Enum):
    EQUAL = 'strictness: equal in both documents'
    A_STRICTER = 'strictness: document A has stricter requirement'
    B_STRICTER = 'strictness: document B has stricter requirement'
    NOT_COMPARABLE = 'strictness: requirements not directly comparable'
    NOT_APPLICABLE = 'strictness: not applicable (unique to one document)'

class RequirementAnalysis(BaseModel):
    topic: str = Field(..., description = 'The topic or category of the requirement (e.g., "Documentation", "Testing", "Approval Process")')
    document_a_formulation: str = Field(..., description = 'Extract from document A, transcribed verbatim but cleaned from parsing artifacts if necessary. If requirement not present in document A, leave empty.')
    document_a_chunk_id: List[str] = Field(..., description = 'Document A chunk ids, example: "Chunk 321". Empty list if not present in document A.')
    document_b_formulation: str = Field(..., description = 'Extract from document B, transcribed verbatim but cleaned from parsing artifacts if necessary. If requirement not present in document B, leave empty.')
    document_b_chunk_id: List[str] = Field(..., description = 'Document B chunk ids, example: "Chunk 321". Empty list if not present in document B.')
    comparison_type: ComparisonType = Field(..., description = 'The relationship between the requirements in both documents')
    requirement_strictness: RequirementStrictness = Field(..., description = 'Which document has the stricter requirement')
    least_constraining_requirement: str = Field(..., description = 'The least constraining requirement extracted from either document. This should be a clear, actionable statement that represents the minimum acceptable standard between both documents.')
    analysis: str = Field(..., description = 'Detailed analysis of the differences between the two requirements and justification for the selected least constraining requirement.')

class Requirements(BaseModel):
    requirements: List[RequirementAnalysis]

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "gpt-4.1",   
        ):
        self.structured_pipeline = pipeline = StructuredPipeline(provider=provider, model=model)
    
    def __call__(self, work : dict) -> JSONL:
        doc_a = work['document_a']
        doc_b = work['document_b']
        
        doc_a_chunks = {_['chunk_id']:_ for _ in doc_a}
        doc_b_chunks = {_['chunk_id']:_ for _ in doc_b}
        
        chunks_a = '\n\n'.join([f'>>>>>>>>>>>>>>>>>>>>>>>>>>> Chunk {o["chunk_id"]}\n{remove_exact_chain(o["text"])}' for o in doc_a])
        chunks_b = '\n\n'.join([f'>>>>>>>>>>>>>>>>>>>>>>>>>>> Chunk {o["chunk_id"]}\n{remove_exact_chain(o["text"])}' for o in doc_b])
        
        prompt = f""">>>
>>> Below, extracts from Document A (first manufacturer procedure)
>>>

{chunks_a}

#########################################

>>>
>>> Below, extracts from Document B (second manufacturer procedure)
>>>

{chunks_b}

>>>
>>> Below, the Instructions
>>>

Please analyze the two documents and identify the requirements in each document. Compare them and extract the least constraining requirements from both documents (the "smaller common denominators"). Provide your analysis in the specified data structure:

- topic: The topic or category of the requirement
- document_a_formulation: Extract from document A (verbatim but cleaned if necessary)
- document_a_chunk_id: Document A chunk id(s)
- document_b_formulation: Extract from document B (verbatim but cleaned if necessary)
- document_b_chunk_id: Document B chunk id(s)
- comparison_type: The relationship between the requirements (identical, similar, complementary, conflicting, unique to A, unique to B)
- requirement_strictness: Which document has the stricter requirement (equal, A stricter, B stricter, not comparable, not applicable)
- least_constraining_requirement: The least constraining requirement extracted from either document. This should be a clear, actionable statement representing the minimum acceptable standard.
- analysis: Detailed analysis of the differences and justification for your selection of the least constraining requirement.

Group similar requirements by topic. For each topic, identify all relevant requirements from both documents and compare them.
When determining the least constraining requirement:
1. If the requirements are identical, use the common requirement.
2. If the requirements differ in strictness, choose the less strict version.
3. If a requirement is unique to one document, evaluate if it should be included based on its necessity.
4. If requirements conflict, propose a solution that satisfies both while being minimally constraining.

The final list of requirements should represent the minimum set of requirements that would satisfy both manufacturers' procedures.
"""
        requirements = None
        p = PROMPT()
        p.add("You are a helpful assistant specializing in regulatory document analysis. You excel at comparing documents and identifying the least constraining requirements across them.", role='system')
        p.add(prompt, role='user')
        
        for retry in range(3):
            try:
                requirements = self.structured_pipeline(p=p, output_format=Requirements)
                break
            except ValidationError as e:
                continue
                
        if requirements is None:
            raise Exception("Could not parse the requirements analysis")
            
        # Process the output
        requirements_list = requirements.dict()['requirements']
        for i, req in enumerate(requirements_list):
            req['requirement_number'] = i
            req['comparison_type'] = req['comparison_type'].name
            req['requirement_strictness'] = req['requirement_strictness'].name
            
            # Process document A chunk information
            prefix_a = []
            if req['document_a_chunk_id']:
                req['document_a_chunk_id'] = [re.sub(r'[^0-9]', '', _ or '') for _ in req['document_a_chunk_id']]
                for chunk_id_str in req['document_a_chunk_id']:
                    try:
                        chunk_id = int(chunk_id_str)
                        chunk = doc_a_chunks[chunk_id]
                        
                        page_start = chunk['page_start']
                        page_end = chunk['page_end']
                        local_index = chunk['local_index']
                        
                        pp = f'Page {page_start} chunk {local_index}' if page_start == page_end else f'Pages {page_start}-{page_end} chunk {local_index}'
                        prefix_a.append(pp)
                    except (ValueError, KeyError):
                        pass
                prefix_a = '' if not prefix_a else f'Document A Location: {", ".join(prefix_a)}\n---\n'
                req['document_a_formulation'] = f'{prefix_a}{req["document_a_formulation"]}'

            # Process document B chunk information
            prefix_b = []
            if req['document_b_chunk_id']:
                req['document_b_chunk_id'] = [re.sub(r'[^0-9]', '', _ or '') for _ in req['document_b_chunk_id']]
                for chunk_id_str in req['document_b_chunk_id']:
                    try:
                        chunk_id = int(chunk_id_str)
                        chunk = doc_b_chunks[chunk_id]
                        
                        page_start = chunk['page_start']
                        page_end = chunk['page_end']
                        local_index = chunk['local_index']
                        
                        pp = f'Page {page_start} chunk {local_index}' if page_start == page_end else f'Pages {page_start}-{page_end} chunk {local_index}'
                        prefix_b.append(pp)
                    except (ValueError, KeyError):
                        pass
                prefix_b = '' if not prefix_b else f'Document B Location: {", ".join(prefix_b)}\n---\n'
                req['document_b_formulation'] = f'{prefix_b}{req["document_b_formulation"]}'
                
            # Add metadata
            req.update({
                'document_a_title': work.get('document_a_title', 'Document A'),
                'document_b_title': work.get('document_b_title', 'Document B'),
                'analysis_date': work.get('analysis_date', '')
            })
            
        return JSONL(lines=requirements_list)