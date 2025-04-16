from custom_types.JSONL.type import JSONL
import numpy as np
import os

class Pipeline:
    def __init__(self):
        pass
        
    def __call__(self, concatenated: JSONL) -> JSONL:
        # Define the order of columns for the output
        column_order = [
            'topic', 
            'document_a_title',
            'document_a_chunk_id',
            'document_a_formulation', 
            'document_b_title',
            'document_b_chunk_id',
            'document_b_formulation', 
            'comparison_type', 
            'requirement_strictness', 
            'least_constraining_requirement',
            'analysis'
        ]
        
        # Sort by topic for better readability
        concatenated.lines.sort(key=lambda x: x.get('topic', ''))
        
        # Filter columns to only include those in column_order
        concatenated.lines = [{k: v.get(k, None) for k in column_order} for v in concatenated.lines]
        
        # If there are page numbers to adjust, handle them
        for line in concatenated.lines:
            # Process document A chunk information if it contains page references
            if 'document_a_chunk_id' in line and line['document_a_chunk_id']:
                line['document_a_chunk_id'] = [
                    f"Chunk {chunk_id}" for chunk_id in line['document_a_chunk_id']
                ]
                
            # Process document B chunk information if it contains page references
            if 'document_b_chunk_id' in line and line['document_b_chunk_id']:
                line['document_b_chunk_id'] = [
                    f"Chunk {chunk_id}" for chunk_id in line['document_b_chunk_id']
                ]
        
        # Rename columns to more human-readable names
        renames = {
            'topic': 'Topic',
            'document_a_title': 'Document A',
            'document_a_chunk_id': 'Document A Reference',
            'document_a_formulation': 'Document A Requirement',
            'document_b_title': 'Document B',
            'document_b_chunk_id': 'Document B Reference',
            'document_b_formulation': 'Document B Requirement',
            'comparison_type': 'Comparison Type',
            'requirement_strictness': 'Requirement Strictness',
            'least_constraining_requirement': 'Least Constraining Requirement',
            'analysis': 'Analysis'
        }
        
        # Apply the renames
        concatenated.lines = [{renames.get(k, k): v for k, v in line.items()} for line in concatenated.lines]
        
        return concatenated