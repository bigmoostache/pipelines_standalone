from typing import Union, List, Optional
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup, NavigableString, Tag
from custom_types.HTML.type import HTML
import re, json
from custom_types.SOTA.type import SOTA, VersionedText, Version, Author, VersionedInformation, Language, VersionedListVersionedText, Converter as SOTAConverter, Sections

vt = lambda x: VersionedText(versions={-1: x})

class HTML_H_TREE(BaseModel):
    title: str = Field(..., description="Title of the HTML node")
    contents: Union[str, List["HTML_H_TREE"]] = Field(..., description="Contents of the HTML node")
    
    def prrint(self, depth: int = 0) -> str:
        """Print the tree structure with indentation."""
        indent = ' ' * (depth * 2)
        if isinstance(self.contents, str):
            return f"{indent}{self.title}: ..."
        else:
            result = f"{indent}{self.title}:\n"
            for child in self.contents:
                result += child.prrint(depth + 1) + '\n'
            return result.strip()
    
    def num_chars(self) -> int:
        """Calculate the total number of characters in the node."""
        if isinstance(self.contents, str):
            return len(self.title) + len(self.contents)
        else:
            return sum([c.num_chars() for c in self.contents]) + len(self.title)
    
    @classmethod
    def from_html(cls, html_string: str) -> "HTML_H_TREE":
        """
        Create HTML_H_TREE from HTML string with enhanced title detection.
        The title + contents should always equal the original html_string.
        """
        if not html_string or not html_string.strip():
            return cls(title='', contents=html_string)
        
        soup = BeautifulSoup(html_string, 'html.parser')
        
        # Find the first heading tag in the HTML
        first_heading = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if first_heading:
            # Find the position of the first heading in the original string
            heading_html = str(first_heading)
            heading_pos = html_string.find(heading_html)
            
            if heading_pos != -1:
                # Split at the heading position
                title_part = html_string[:heading_pos]
                contents_part = html_string[heading_pos:]
                
                # If there's content before the heading, use it as title
                if title_part.strip():
                    return cls(title=title_part, contents=contents_part)
                else:
                    # If heading is at the start, use the heading as title
                    heading_end = heading_pos + len(heading_html)
                    return cls(title=heading_html, contents=html_string[heading_end:])
        
        # No heading found, or heading detection failed
        return cls(title='', contents=html_string)
    
    def split(self, positions: List[int]):
        """Split the contents at given positions."""
        assert isinstance(self.contents, str), "Cannot split a non-string content"
        positions = [0] + positions + [len(self.contents)]
        new_strings = [self.contents[positions[i]:positions[i+1]] for i in range(len(positions) - 1)]
        self.contents = [self.from_html(s) for s in new_strings if s.strip()]

def get_element_html(element) -> str:
    """Get the complete HTML string of an element."""
    if isinstance(element, NavigableString):
        return str(element)
    elif isinstance(element, Tag):
        return str(element)
    else:
        return str(element) if element else ""

def calculate_text_length_for_splitting(element, exclude_images=True) -> int:
    """Calculate text length for splitting decisions, excluding images if specified."""
    if isinstance(element, NavigableString):
        return len(str(element).strip())
    
    if isinstance(element, Tag):
        if exclude_images and element.name in ['img', 'figure']:
            return 0
        
        # Get text content only for length calculation
        text_content = element.get_text()
        return len(text_content.strip())
    
    return len(str(element).strip()) if element else 0

def find_heading_level(tag) -> Optional[int]:
    """Extract heading level from tag name (h1 -> 1, h2 -> 2, etc.)."""
    if tag and tag.name and tag.name.startswith('h'):
        try:
            return int(tag.name[1])
        except (ValueError, IndexError):
            return None
    return None

def find_split_positions(html_string: str, max_section_length: int) -> List[int]:
    """
    Find positions where the HTML should be split based on heading tags.
    Returns relative positions within the string.
    """
    soup = BeautifulSoup(html_string, 'html.parser')
    
    # Calculate content length for splitting decision
    content_length = calculate_text_length_for_splitting(soup)
    
    # If content is under threshold, no splitting needed
    if content_length <= max_section_length:
        return []
    
    # Find all heading tags in the content
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    if not headings:
        return []
    
    # Detect the highest h-tag level (lowest number) available
    heading_levels = []
    for h in headings:
        level = find_heading_level(h)
        if level is not None:
            heading_levels.append(level)
    
    if not heading_levels:
        return []
        
    highest_level = min(heading_levels)
    
    # Get positions of headings at the highest level
    split_positions = []
    for h in headings:
        if find_heading_level(h) == highest_level:
            heading_html = str(h)
            pos = html_string.find(heading_html)
            if pos != -1 and pos > 0:  # Don't split at position 0
                split_positions.append(pos)
    
    return sorted(list(set(split_positions)))

def parse_html_to_tree(html_string: str, max_section_length: int = 3000) -> HTML_H_TREE:
    """
    Parse HTML string into a hierarchical tree structure using only HTML_H_TREE.from_html 
    and HTML_H_TREE.split methods.
    
    Args:
        html_string: The HTML content to parse
        max_section_length: Maximum length for a section before splitting
    
    Returns:
        Single HTML_H_TREE object representing the document structure
    """
    def split_recursively(node: HTML_H_TREE, depth: int = 0) -> None:
        """Recursively split a node if needed."""
        # Prevent infinite recursion
        if depth > 50:
            return
        
        # Only split if contents is a string
        if not isinstance(node.contents, str):
            # If contents is already a list, recursively process each child
            for child in node.contents:
                split_recursively(child, depth + 1)
            return
        
        # Find split positions for this node's contents
        split_positions = find_split_positions(node.contents, max_section_length)
        
        if split_positions:
            # Split the node at the found positions
            node.split(split_positions)
            
            # Recursively process each new child
            if isinstance(node.contents, list):
                for child in node.contents:
                    split_recursively(child, depth + 1)
    
    # Create initial tree from the entire HTML string
    root = HTML_H_TREE.from_html(html_string)
    
    # Handle document title detection for root
    soup = BeautifulSoup(html_string, 'html.parser')
    document_title = "Document"
    
    # Look for title tag first
    title_tag = soup.find('title')
    if title_tag and title_tag.get_text().strip():
        document_title = title_tag.get_text().strip()
    else:
        # Look for the first h1 tag as potential title
        first_h1 = soup.find('h1')
        if first_h1 and first_h1.get_text().strip():
            document_title = first_h1.get_text().strip()
    
    # If root has empty title, use the detected document title
    if not root.title.strip():
        # We need to preserve the constraint that title + contents = original string
        # So we'll create a new root structure
        if root.contents == html_string:  # This should be true for from_html with empty title
            root = HTML_H_TREE(title=document_title, contents=html_string)
        else:
            # Adjust to maintain the constraint
            root.title = document_title
    
    # Apply recursive splitting
    split_recursively(root)
    
    return root

def transfer(sota, node, information_id: int = None, root: bool = False, hardcoded_prompt: str = ''):
    if root:
        # Create root information
        sota.information[sota.mother_id] = VersionedInformation.create_text(node.title, Sections(sections=[]), node.title, node.title)
        sota.title = vt(node.title)
        
        # Process the contents directly without complex wrapper structure
        if isinstance(node.contents, str):
            # If root contents is a string, create a single section
            abstract = f'<p><em>Below is the TEMPLATE for that section. </em></p><hr><p>{node.contents}</p>'
            new_info = VersionedInformation.create_text("Content", node.contents, node.contents, "Content")
            new_info.ai_pipelines_to_run = [json.dumps({
                'name': 'rewrite', 
                'params': {
                    'references_mode': 'allow', 
                    'additional_instructions': hardcoded_prompt, 
                    'final_comment': False
                }
            })]
            new_id = sota.get_new_id(sota.information)
            sota.information[new_id] = new_info
            sota.information[sota.mother_id].sections.append(new_id)
        else:
            # Process each child section
            for n in node.contents:
                transfer(sota, n, information_id=sota.mother_id, hardcoded_prompt=hardcoded_prompt)
        return
    
    # Handle non-root nodes
    information_id = information_id if information_id else sota.mother_id
    information = sota.get_last(sota.information[information_id].versions, sota.versions_list(-1))
    
    if not isinstance(node.contents, str):
        # Create a new information node for this section
        new_info = VersionedInformation.create_text(node.title, Sections(sections=[]), node.title, node.title)
        new_id = sota.get_new_id(sota.information)
        sota.information[new_id] = new_info
        
        # Process all children
        for n in node.contents:
            transfer(sota, n, information_id=new_id, hardcoded_prompt=hardcoded_prompt)
    else:
        # Leaf node - create content section
        abstract = f'<p><em>Below is the TEMPLATE for that section. </em></p><hr><p>{node.contents}</p>'
        new_info = VersionedInformation.create_text(node.title, node.contents, node.contents, node.title)
        new_info.ai_pipelines_to_run = [json.dumps({
            'name': 'rewrite', 
            'params': {
                'references_mode': 'allow', 
                'additional_instructions': hardcoded_prompt, 
                'final_comment': False
            }
        })]
        new_id = sota.get_new_id(sota.information)
        sota.information[new_id] = new_info
    
    # Add this section to the parent
    information.sections.append(new_id)

class Pipeline:
    def __init__(self, 
                 char_th: int = 3500,
                 hardcoded_prompt: str = 'Please rewrite this section, filling the missing information using the provided context and data. Preserve the structure of the section, your role is to fill the template. Is there is any missing information, please specify it, embedded in the text, in red. If everything is already filled, then your task is trivial: just rewrite everything verbatim. Be AS EXHAUSTIVE AS POSSIBLE., any missing data will be heavily punished.'
                 ):
        self.char_th = char_th
        self.hardcoded_prompt = hardcoded_prompt
        
    def __call__(self, html: HTML) -> SOTA:
        new_sota = SOTA.get_empty()
        # Parse HTML using only from_html and split methods
        soup = BeautifulSoup(html.html, 'html.parser')
        body = soup.body
        html_body = str(body) if body else html.html
        r = parse_html_to_tree(html_body, self.char_th)
        print(r.prrint())
        transfer(
            new_sota,
            r,
            root=True,
            hardcoded_prompt=self.hardcoded_prompt
        )
        return new_sota