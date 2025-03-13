import json
from custom_types.HTML.type import HTML

def escape_html(text):
    """Escape special HTML characters in a string."""
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in str(text))

def process_json_value(value, indent=0):
    """Process a JSON value based on its type."""
    if isinstance(value, dict):
        return process_dict(value, indent + 1)
    elif isinstance(value, list):
        return process_list(value, indent + 1)
    elif isinstance(value, str):
        return f'<span>"{escape_html(value)}"</span>'
    elif isinstance(value, (int, float)):
        return f'<span>{value}</span>'
    elif isinstance(value, bool):
        return f'<span>{str(value).lower()}</span>'
    elif value is None:
        return '<span>null</span>'
    else:
        return escape_html(str(value))

def process_dict(json_dict, indent=0):
    """Process a JSON dictionary using a ul with bold keys."""
    if not json_dict:
        return '<span>{}</span>'
    
    html = '<ul>'
    
    for key, value in json_dict.items():
        html += f'<li><strong>{escape_html(key)}</strong>: {process_json_value(value, indent)}</li>'
    
    html += '</ul>'
    return html

def process_list(json_list, indent=0):
    """Process a JSON list."""
    if not json_list:
        return '<span>[]</span>'
    
    html = '<ol>'
    
    for item in json_list:
        html += f'<li>{process_json_value(item, indent)}</li>'
    
    html += '</ol>'
    return html

def json_to_html(json_obj):
    """Convert a JSON object to HTML representation."""
    return process_json_value(json_obj)

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, json_obj : dict) -> HTML:
        return HTML(html = json_to_html(json_obj))