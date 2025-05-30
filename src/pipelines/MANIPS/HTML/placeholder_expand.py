from bs4 import BeautifulSoup, Comment
from custom_types.HTML.type import HTML

class Pipeline:
    """
    Pipeline that expands contracted HTML by replacing placeholder strings 
    with original content elements using exact string matching.
    """
    
    def __init__(self):
        pass
    
    def __call__(self, contracted_data: dict) -> HTML:
        """
        Expand contracted HTML by replacing placeholder strings with original content.
        
        Args:
            contracted_data: Dictionary with 'new_contracted_html' and 'replacements'
            
        Returns:
            HTML: Reconstructed HTML object
        """
        html_content = contracted_data['new_contracted_html']
        replacements = contracted_data['replacements']
        
        # Replace each placeholder string with its original content
        for placeholder_str, original_content in replacements.items():
            # Count occurrences of the placeholder string
            occurrence_count = html_content.count(placeholder_str)
            
            if occurrence_count == 0:
                raise ValueError(f"Placeholder not found in HTML: {placeholder_str}")
            elif occurrence_count > 1:
                raise ValueError(f"Multiple occurrences of placeholder found ({occurrence_count}): {placeholder_str}")
            
            # Replace the single occurrence
            html_content = html_content.replace(placeholder_str, original_content)
        
        return HTML(html=html_content)