from custom_types.HTML.type import HTML
from custom_types.PROMPT.type import PROMPT
from pipelines.LLMS_v2.str_output import Pipeline as LLM

default_prompt ="""
# HTML Section Headers Formatter

## Task
Rewrite the given document with proper HTML heading tags while preserving all original content.

## Instructions
1. Format the document by adding appropriate HTML heading tags (h1-h6)
2. The document's title must be wrapped in an <h1> tag
3. Use only ONE <h1> tag for the entire document
4. All section headings should use h2-h6 tags in a hierarchical structure
5. Maintain proper heading hierarchy - never skip levels (e.g., don't go from h2 to h4)
6. Do not modify any content - only add heading tags to existing section titles
7. Return the complete HTML-formatted document

## Output Format
Your response must follow this structure:
1. Brief explanation of what you did
2. The formatted HTML inside code blocks:
```html
<your formatted HTML here>
```
"""
def parse_and_verify(res: str) -> str:
    count = res.count("```html")
    # rule 1 - Ensure ```html exists, and only once
    assert count == 1, f"Expected 1 ```html, got {count}"
    position = res.index("```html") + len("```html")
    res = res[position:]
    count = res.count("```")
    # rule 2 - Ensure ``` exists, and only once
    assert count == 1, f"Expected 1 ```, got {count}"
    position = res.index("```")
    res = res[:position]
    # 3. Check correct structure of h tags: 
    soup = BeautifulSoup(res, 'html.parser')
    tag_list = []
    for child in soup.children:
        child_tag = child.name
        if childt_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            tag_list.append(child_tag)
    # rule 3 - Check that the document starts with a h1 tag, and that there is only one h1 tag in the document
    assert len(soup.children) > 0, f"Expected at least one tag, got {len(soup.children)}"
    assert soup.children[0].name == 'h1', f"First tag is not h1, got {soup.children[0].name}"
    assert tag_list.count('h1') == 1, f"Expected 1 h1, got {tag_list.count('h1')}"
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
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 model : str = "gpt-4-1106-preview",
                 prompt : str = default_prompt):
        self.model = model
        self.prompt = prompt

    def __call__(self, doc: HTML) -> HTML:
        prompt = PROMPT()
        prompt.add(doc.html, role="user")
        prompt.add(self.prompt, role="system")
        pipeline = LLM(model = self.model)
        res = pipeline(prompt)
        return HTML(html=parse_and_verify(res))