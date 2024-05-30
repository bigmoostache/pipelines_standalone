from typing import List
import re
import os
import dotenv


class Pipeline:
    __env__ = ["image_token"]

    def __init__(self):
        pass


    def __call__(self,  article :str) -> List[dict]:

        image_token = os.environ.get("image_token")

        image_key = "image"
        caption_key = "caption"


        # Remove tables and pages indicator
        article = remove_tables_and_pages(article)

        output = []

        # Split by paragraphs
        matches = [[m.group(0), (m.start(), m.end() - 1)] for m in re.finditer(r'(?!\\n\\n)([^\n]|\\n(?!\\n))+', article)]
        paragraphs, split_idx = zip(*matches)

        # Extract images
        for i,paragraph in enumerate(paragraphs):

            if paragraph.startswith("![Image"):
                caption = None
                image = paragraph

                # Get only the link of the image
                match = re.search(r'\((.*?)\)',paragraph)
                assert match, "Error; something went wrong when extracting the link of the image line using Regex"
                image = match.group(1)

                # insert the token of the image at the end for acces:
                image = image.replace("None", image_token)

                # Look on next paragrah for caption:
                if i<len(paragraphs)-1:
                    # If in the first 10 characters there is somegthing similar to Fig or Figure we save the caption
                    if len(paragraphs[i+1]) >= 10 and bool(re.search(r'\b(figure|fig)\b', paragraphs[i+1][:10], re.IGNORECASE)):
                        caption = paragraphs[i+1]

                # Append the result
                output.append(
                    {
                        image_key:image,
                        caption_key:caption
                        }
                )
        
        return output
        


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

