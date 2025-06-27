from custom_types.HTML.type import HTML
from custom_types.PROMPT.type import PROMPT
from bs4 import BeautifulSoup
from pipelines.LLMS.v3.client import Providers
from pipelines.LLMS.v3.str import Pipeline as LLM

default_prompt ="""
# HTML Section Headers Formatter

## Task
Rewrite the given document with proper HTML heading tags while preserving all original content.

## Instructions
1. Clean this document
2. Remove any table of contents, page numbers, footers, headers, and other artifacts that are not part of the main content. Leave the rest!!!
3. Keep the paragraph ids, table ids, image ids and list ids intact!!! (This is very important, those ids, such as id="paragraph_1", id="table_2", etc. MUST remain unchanged). The document was contracted to make your job easier, but those ids will be used later to reconstruct the original document, so they must remain intact.
4. The document's title must be wrapped in an <h1> tag
5. Use only ONE <h1> tag for the entire document: if there currently are any, relegate them and shift the whole hierarchy down
6. All section headings should use h2-h6 tags in a hierarchical structure
7. Maintain proper heading hierarchy - never skip levels (e.g., don't go from h2 to h4)
8. Return the complete HTML-formatted document

The purpose of your work is both to
- Clean the document from unnecessary artifacts
- Create a clean header structure that will be parsed in order to convert this html to a proper tree structure

To be more detailed, here is the python function that will be used to verify your output:
```python
def parse_and_verify(res: str) -> str:
    count = res.count("```html")
    # rule 1 - Ensure ```html exists, and only once
    assert count == 1, f"Expected 1 ```html, got {count}"
    position = res.index("```html") + len("```html")
    res = res[position:]
    count = res.count("```")
    # And that ``` exists after, and only once
    assert count == 1, f"Expected 1 ```, got {count}"
    position = res.index("```")
    res = res[:position]
    # rule 2 - Document should start with '<h1>' -> YOU SHOULD ADD THIS AT THE VERY BEGINNING IF NECESSARY, even if it means inventing a title
    assert res.strip().startswith('<h1>'), f"Document does not start with <h1>, got: {res[:50]}..."  # Check first 50 chars for context
    # 3. Check correct structure of h tags: 
    soup = BeautifulSoup(res, 'html.parser')
    tag_list = []
    at_least_one = False
    for i,child in enumerate(soup.children):
        if not str(child).strip():
            continue
        at_least_one = True
        if i == 0:
            # rule 3 - Check that the document starts with a h1 tag, and that there is only one h1 tag in the document
            assert child.name == 'h1', f"First tag is not h1, got {child.name}"
        child_tag = child.name
        if child_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            tag_list.append(child_tag)
    assert at_least_one, f"Expected at least one tag, got 0"
    # rule 4 - Check that the tags are in correct order: skipping from h1 to h3, for example, is not allowed
    # Examples: h3 can be followed by h2, h3 or h4, but not h5
    prev = 1
    for tag in tag_list[1:]:
        curr = int(tag[1])
        assert (curr <= prev or curr == prev + 1), f"Tag {tag} is not in correct order, prev: {prev}, curr: {curr}"
        prev = curr
    # 4. We're good
    return res
```

## Output Format
Your response must follow this structure:
1. Repeat the instructions
2. Provide the formatted HTML inside code blocks:
```html
<h1>Document Title</h1> (or the actual title if you see it)
...
```
"""

def parse_and_verify(res: str) -> str:
    count = res.count("```html")
    # rule 1 - Ensure ```html exists, and only once
    assert count == 1, f"Expected 1 ```html, got {count}"
    position = res.index("```html") + len("```html")
    res = res[position:]
    count = res.count("```")
    # And that ``` exists after, and only once
    assert count == 1, f"Expected 1 ```, got {count}"
    position = res.index("```")
    res = res[:position]
    # rule 2 - Document should start with '<h1>' -> YOU SHOULD ADD THIS AT THE VERY BEGINNING IF NECESSARY, even if it means inventing a title
    if not res.strip().startswith('<h1'):, f"Document does not start with <h1>, got: {res[:50]}..."  # Check first 50 chars for context
        # 'add <h1>Document Title</h1>' at the beginning
        res = '<h1>Document Title</h1>\n' + res.strip()
    # 3. Check correct structure of h tags: 
    soup = BeautifulSoup(res, 'html.parser')
    tag_list = []
    at_least_one = False
    for i,child in enumerate(soup.children):
        if not str(child).strip():
            continue
        at_least_one = True
        if i == 0:
            # rule 3 - Check that the document starts with a h1 tag, and that there is only one h1 tag in the document
            assert child.name == 'h1', f"First tag is not h1, got {child.name}"
        child_tag = child.name
        if child_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            tag_list.append(child_tag)
    assert at_least_one, f"Expected at least one tag, got 0"
    # rule 4 - Check that the tags are in correct order: skipping from h1 to h3, for example, is not allowed
    # Examples: h3 can be followed by h2, h3 or h4, but not h5
    prev = 1
    for tag in tag_list[1:]:
        curr = int(tag[1])
        assert (curr <= prev or curr == prev + 1), f"Tag {tag} is not in correct order, prev: {prev}, curr: {curr}"
        prev = curr
    # 4. We're good
    return res
            
class Pipeline:
    def __init__(self, 
                 model : str = "gpt-4.1",
                 provider: Providers = 'openai',
                 prompt : str = default_prompt):
        self.model = model
        self.prompt = prompt
        self.provider = provider

    def __call__(self, doc: HTML) -> HTML:
        prompt = PROMPT()
        prompt.add(doc.html, role="user")
        prompt.add(self.prompt, role="system")
        pipeline = LLM(model = self.model, provider=self.provider)
        res = pipeline(prompt)
        return HTML(html=parse_and_verify(res))