
import re

class Pipeline:

    def __init__(self):
        pass


    def __call__(self, article :str) -> str:

        article = remove_tables_and_pages(article)
        article = remove_images_and_captions(article)

        return article
    


def remove_tables_and_pages(article):
    
    lines = re.split(r'\n(?!\n)', article)

    # Find idx to delete
    idx_to_delete = []
    register = False
    for idx,line in enumerate(lines):

        # Delete page start

        if line.startswith("<!-- PAGE"): 
            idx_to_delete.append(idx)
            continue

        # Delete tables

        if line.startswith("<!--TABLE"):
            idx_to_delete.append(idx)
            register = True
            continue

        if line.startswith("<!--END"):
            idx_to_delete.append(idx)
            register = False
            continue

        if register == True:
            idx_to_delete.append(idx)
            continue
    # Delete lines using their idx
    lines = [line for idx,line in enumerate(lines) if idx not in idx_to_delete]

    cleaned_article = '\n'.join(lines)

    return cleaned_article


def remove_images_and_captions(article):


    matches = [[m.group(0), (m.start(), m.end() - 1)] for m in re.finditer(r'(?!\\n\\n)([^\n]|\\n(?!\\n))+', article)]
    paragraphs, split_idx = zip(*matches)

    idx_to_delete = []
    for idx,paragraph in enumerate(paragraphs):

        if paragraph.startswith("![Image"):
                idx_to_delete.append(idx)
                # Look on next paragrahs for caption:
                if idx<len(paragraphs)-1:
                    # If in the first 10 characters there is somegthing similar to Fig or Figure we save the caption
                    if len(paragraphs[idx+1]) >= 10 and bool(re.search(r'\b(figure|fig)\b', paragraphs[idx+1][:10], re.IGNORECASE)):
                        idx_to_delete.append(idx+1)
    
    # Delete paragraphs using their idx
    paragraphs = [par for idx,par in enumerate(paragraphs) if idx not in idx_to_delete]            
                    
    # Join paragraphs using double lineskip

    cleaned_article = '\n\n'.join(paragraphs)

    return cleaned_article
