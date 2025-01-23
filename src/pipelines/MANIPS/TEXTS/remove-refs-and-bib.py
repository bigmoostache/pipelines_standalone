import re

def splitter(x):
    # Pattern to match headings
    pattern = re.compile(r'^(#{1,4})\s*(.*)$', re.MULTILINE)
    matches = list(pattern.finditer(x))
    
    # Prepare the list of {'title': ..., 'content': ...}
    results = []
    for i, match in enumerate(matches):
        start_idx = match.end()  # End of the match (start of content)
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(x)
        content = x[start_idx:end_idx]  # Extract content between headings
        results.append((match.group(1).strip(), match.group(2).strip(), content))
    return results

def clean_text(input_string):
    lower_string = input_string.lower()
    # Remove special characters and numbers using regex
    cleaned_string = re.sub(r'[^a-z\s]', '', lower_string).replace(' ', '')
    return cleaned_string

def process(text):
    bibliographie = ['bibliography', 'references', 'works cited', 'cited works', 'sources', 'citations', 
    'literature cited', 'further reading', 'additional reading', 'resources', 
    'références', 'bibliographie', 'ouvrages cités', 'sources citées', 
    'littérature citée', 'lectures complémentaires']
    bibliographie = {clean_text(_) for _ in bibliographie}
    r = splitter(text)
    r2 = [_ for _ in r if clean_text(_[1]) not in bibliographie]
    if len(r2) != len(r) - 1:
        return text
    return ''.join(f'{_} {__}{___}' for _, __, ___ in r2)

def remove_refs(text):
    text = re.sub(r'\[\s*\d+\s*\]', '', text)
    text = re.sub(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', '', text)
    return text

class Pipeline:
    def __init__(self):
        pass
        
    def __call__(self, text : str) -> str:
        text = process(text)
        text = remove_refs(text)
        return text
