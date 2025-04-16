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
            'requirement_a',
            'document_b_title',
            'document_b_chunk_id',
            'requirement_b',
            'comparison_type',
            'requirement_importance',
            'least_stringent',
            'comparison_description',
            'notes'
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
            'requirement_a': 'Document A Requirement',
            'document_b_title': 'Document B',
            'document_b_chunk_id': 'Document B Reference',
            'requirement_b': 'Document B Requirement',
            'comparison_type': 'Comparison Type',
            'requirement_importance': 'Requirement Importance',
            'least_stringent': 'Least Stringent Requirement',
            'comparison_description': 'Analysis',
            'notes': 'Additional Notes'
        }
        
        # Apply the renames
        concatenated.lines = [{renames.get(k, k): v for k, v in line.items()} for line in concatenated.lines]
        
        return concatenated