from bs4 import BeautifulSoup, Comment
from custom_types.HTML.type import HTML

class Pipeline:
    """
    Pipeline that expands contracted HTML by replacing placeholder elements
    with original content elements using BeautifulSoup to find elements by ID.
    """
   
    def __init__(self, param: str = 'new_contracted_html'):
        self.param = param  # Parameter to use for the new contracted HTML key
   
    def __call__(self, contracted_data: dict) -> HTML:
        """
        Expand contracted HTML by replacing placeholder elements with original content.
       
        Args:
            contracted_data: Dictionary with 'new_contracted_html' and 'replacements'
           
        Returns:
            HTML: Reconstructed HTML object
        """
        html_content = contracted_data[self.param]
        replacements = contracted_data['replacements']
       
        # Parse the contracted HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Replace each placeholder element with its original content
        for placeholder_id, original_content in replacements.items():
            # Find the element with this ID
            placeholder_element = soup.find(id=placeholder_id)
            
            if placeholder_element is None:
                continue # raise ValueError(f"Placeholder element with ID '{placeholder_id}' not found in HTML")
            
            # Parse the original content to reconstruct the element
            original_soup = BeautifulSoup(original_content, 'html.parser')
            
            # Get the reconstructed element (should be a single element since we stored str(element))
            original_element = original_soup.find()
            
            if original_element is None:
                raise ValueError(f"Could not parse original content for placeholder '{placeholder_id}'")
            
            # Replace the placeholder with the original element
            placeholder_element.replace_with(original_element)
       
        return HTML(html=str(soup))