
from custom_types.PROMPT.type import PROMPT
from custom_types.JSONL.type import JSONL
from custom_types.trees.gap_analysis.type import ResponseType as Tree_Gap_AnalysisResponseType
from pipelines.CONVERSIONS.PDF.to_txt_mistral import extract_pages
from pipelines.LLMS.v3.str import Pipeline as StrPipeline, extract_code_block
    
p3 = """
################## Document A ##################

---> TOC doc A

%s

---> Relevant extracts from document A

%s

################## Document B ##################

---> TOC doc B

%s

---> Associated relevant extracts from document B

%s

################## Instructions ##################

We are currently writing section '%s' (and '%s' ONLY, NOT THE REST) of the following document, which is the 'denominator' of the two documents above.

%s

Please write the contents of THIS SECTION ONLY (%s).
It should contain the 'common denominator' of the two documents above, and should be written in the same format and style as the two documents above.
After that section, add a table summarizing similarities and differences between the two documents. Columns should be
- Aspect
- Document A
- Document B
- Similarities
- Differences

--- > It was determined that the relevant sections (of doc B) mapping to '%s' (of new doc) were

%s

---> It was determined that the relevant sections (of doc A) mapping to '%s' (of new doc) were

%s

################## Expected output format ##################
Your anser should be structured as follows:

<!-- your thought process here -->

```md
%s %s

<!-- section contents here -->

**Gap analysis**

<!-- table of similarities and differences between the two documents, in markdown format -->

```
You should write in English.
""" 
# In order of %s: TOC doc A, list_relevant_sections(mapping), content doc A, TOC doc B, relevant dob b sections, content doc B, denominator section title, TOC doc denominator, denominator section title
 
def write(res, doc_A, doc_B, task):
    res = ResponseType.model_validate(res)
    
    depth = len(task)
    diese_depth = '#' * depth
    task_doc = res.document_denominator.get_task_doc(res.document_denominator, task)
    task_doc_parents = res.document_denominator.build_parents()[tuple(task)]

    doc_A = extract_pages(doc_A)
    doc_A_sections = task_doc.retrieve_things_that_map_to_me(res.document_A, task_doc_parents)
    doc_A_useful_pages = sorted(list(set([_ for _ in doc_A_sections for _ in range(_.page_number, _.get_page_of_next(task) + 1)])))
    doc_A_pages = '\n\n'.join([doc_A.get(_, doc_A.get(_-1, '')) for _ in doc_A_useful_pages])
    doc_A_relevant_sections_titles = '\n- '+'\n- '.join([f'{_.title} (p. {_.page_number})' for _ in doc_A_sections])
    
    doc_B = extract_pages(doc_B)
    doc_B_sections = task_doc.retrieve_things_that_map_to_me(res.document_B, task_doc_parents)
    doc_B_useful_pages = sorted(list(set([_ for _ in doc_B_sections for _ in range(_.page_number, _.get_page_of_next(task) + 1)])))
    doc_B_pages = '\n\n'.join([doc_B.get(_, doc_B.get(_-1, '')) for _ in doc_B_useful_pages])
    doc_B_relevant_sections_titles = '\n- '+'\n- '.join([f'{_.title} (p. {_.page_number})' for _ in doc_B_sections])
    
    prompt = p3 % (
        res.document_A.title, doc_A_pages, 
        res.document_B.title, doc_B_pages, 
        task_doc.title, task_doc.title, res.document_denominator, task_doc.title,
        task_doc.title, doc_A_relevant_sections_titles,
        task_doc.title, doc_B_relevant_sections_titles,
        diese_depth, task_doc.title
    )
    pipe = StrPipeline()
    p = PROMPT()
    p.add(prompt, role='user')
    section = pipe(p)
    section = extract_code_block(section, 'md')
    doc_A_relevant_sections_titles = ('\n' + doc_A_relevant_sections_titles).replace('\n', '\n> ')[3:]
    doc_B_relevant_sections_titles = ('\n' + doc_B_relevant_sections_titles).replace('\n', '\n> ')[3:]
    section = f'{section}\n\n> **Sections used From document A**{doc_A_relevant_sections_titles}\n>\n> **Sections used From document B**{doc_B_relevant_sections_titles}'
    return section

class Pipeline:
    def __init__(self):
        pass
    def __call__(self,
                doc_A: str,
                doc_B: str,
                doc: dict,
                task: dict
                ) -> dict:
        _res = ResponseType.model_validate(doc)
        section = write(res, doc_A, doc_B, task)
        return {tuple(task): section}