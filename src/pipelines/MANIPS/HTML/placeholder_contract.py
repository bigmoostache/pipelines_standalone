from bs4 import BeautifulSoup, Comment
from custom_types.HTML.type import HTML

class Pipeline:
    """
    Pipeline that contracts HTML by replacing paragraphs, images, tables, and lists
    with placeholders, storing full placeholder strings as keys for robust expansion.
    Only replaces top-level elements (not nested within other replaceable elements).
    """
    
    def __init__(self):
        pass
    
    def __call__(self, html: HTML) -> dict:
        """
        Contract HTML by replacing content elements with placeholders.
        Only processes top-level elements, ignoring nested ones.
        
        Args:
            html: HTML object containing the HTML string
            
        Returns:
            dict: Contains 'new_contracted_html' and 'replacements'
        """
        soup = BeautifulSoup(html.html, 'html.parser')
        replacements = {}
        
        # Find all potentially replaceable elements
        all_replaceable = soup.find_all(['p', 'img', 'table', 'ul', 'ol'])
        
        # Filter to only top-level elements (no ancestors that are also replaceable)
        top_level_elements = []
        for element in all_replaceable:
            is_top_level = True
            # Check if any ancestor is also in the replaceable list
            for ancestor in element.find_parents(['p', 'img', 'table', 'ul', 'ol']):
                if ancestor in all_replaceable:
                    is_top_level = False
                    break
            
            if is_top_level:
                top_level_elements.append(element)
        
        # Process top-level elements by type
        # Counters for each type
        p_counter = 0
        img_counter = 0
        table_counter = 0
        list_counter = 0
        
        for element in top_level_elements:
            if element.name == 'p':
                placeholder_id = f"paragraph_{p_counter}"
                
                # Store original content
                original_content = str(element)
                
                # Get first 100 characters of text content
                text_content = element.get_text()
                truncated_text = text_content[:100]
                if len(text_content) > 100:
                    truncated_text += "..."
                
                # Create placeholder paragraph with truncated text
                placeholder = soup.new_tag('p', id=placeholder_id)
                placeholder.string = truncated_text
                
                # Use the full placeholder string as key
                placeholder_str = str(placeholder)
                replacements[placeholder_id] = original_content
                
                element.replace_with(placeholder)
                p_counter += 1
                
            elif element.name == 'img':
                placeholder_id = f"image_{img_counter}"
                
                # Store original content
                original_content = str(element)
                
                # Create placeholder image with hidden_src
                placeholder = soup.new_tag('img', id=placeholder_id)
                
                # Copy all attributes except src
                for attr, value in element.attrs.items():
                    if attr != 'src':
                        placeholder[attr] = value
                
                # Set src to 'hidden_src'
                placeholder['src'] = 'hidden_src'
                
                # Use the full placeholder string as key
                placeholder_str = str(placeholder)
                replacements[placeholder_id] = original_content
                
                element.replace_with(placeholder)
                img_counter += 1
                
            elif element.name == 'table':
                placeholder_id = f"table_{table_counter}"
                
                # Store original content
                original_content = str(element)
                
                # Create placeholder table with first 2 rows + etc.
                placeholder = soup.new_tag('table', id=placeholder_id)
                
                # Copy table attributes
                for attr, value in element.attrs.items():
                    if attr != 'id':  # Don't copy original id
                        placeholder[attr] = value
                
                # Get all rows
                rows = element.find_all('tr')
                
                # Add first 2 rows
                for i, row in enumerate(rows[:2]):
                    # Deep copy the row
                    new_row = soup.new_tag('tr')
                    for attr, value in row.attrs.items():
                        new_row[attr] = value
                    new_row.append(BeautifulSoup(str(row), 'html.parser').tr)
                    placeholder.append(new_row.tr if new_row.tr else new_row)
                
                # Add "etc." row if there are more than 2 rows
                if len(rows) > 2:
                    etc_row = soup.new_tag('tr')
                    etc_cell = soup.new_tag('td')
                    etc_cell.string = "etc."
                    etc_row.append(etc_cell)
                    placeholder.append(etc_row)
                
                # Use the full placeholder string as key
                placeholder_str = str(placeholder)
                replacements[placeholder_id] = original_content
                
                element.replace_with(placeholder)
                table_counter += 1
                
            elif element.name in ['ul', 'ol']:
                list_type = element.name  # 'ul' or 'ol'
                placeholder_id = f"list_{list_counter}"
                
                # Store original content
                original_content = str(element)
                
                # Create placeholder list with first 2 items
                placeholder = soup.new_tag(list_type, id=placeholder_id)
                
                # Copy list attributes
                for attr, value in element.attrs.items():
                    if attr != 'id':  # Don't copy original id
                        placeholder[attr] = value
                
                # Get all list items
                list_items = element.find_all('li')
                
                # Add first 2 items (truncated to 100 chars each)
                for i, item in enumerate(list_items[:2]):
                    new_item = soup.new_tag('li')
                    
                    # Copy item attributes
                    for attr, value in item.attrs.items():
                        new_item[attr] = value
                    
                    # Get text content and truncate to 100 chars
                    item_text = item.get_text()
                    truncated_item_text = item_text[:100]
                    if len(item_text) > 100:
                        truncated_item_text += "..."
                    
                    new_item.string = truncated_item_text
                    placeholder.append(new_item)
                
                # Add "etc." item if there are more than 2 items
                if len(list_items) > 2:
                    etc_item = soup.new_tag('li')
                    etc_item.string = "etc."
                    placeholder.append(etc_item)
                
                # Use the full placeholder string as key
                placeholder_str = str(placeholder)
                replacements[placeholder_id] = original_content
                
                element.replace_with(placeholder)
                list_counter += 1
        
        return {
            'new_contracted_html': str(soup),
            'replacements': replacements
        }