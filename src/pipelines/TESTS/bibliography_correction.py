import re

import re

# ------------------------------------------------------------------------
# 1. Split text before and after the Bibliography
# ------------------------------------------------------------------------
def split_text_at_bibliography(text, marker="## Bibliography"):
    split_index = text.find(marker)
    if split_index != -1:
        return text[:split_index], text[split_index:]
    else:
        return text, ""


# ------------------------------------------------------------------------
# 2. Extract numbers in brackets BEFORE bibliography
# ------------------------------------------------------------------------
def extract_numbers_in_brackets(text):
    """Extract numbers enclosed in square brackets, returning a list of
    strings in the format 'index_v1: X, ref_number_v1: Y'.
    """
    output = []
    matches = re.findall(r"\[(\d+)\]", text)
    for i, match in enumerate(matches):
        output.append(f"index_v1: {i}, ref_number_v1: {match}")
    return output


# ------------------------------------------------------------------------
# 3. Get unique reference numbers BEFORE bibliography
# ------------------------------------------------------------------------
def get_unique_ref_numbers(index_and_value_list):
    """Extract unique ref_number_v1 values (as integers) from a list
    of strings in the format 'index_v1: X, ref_number_v1: Y'.
    """
    ref_numbers = set()
    for item in index_and_value_list:
        try:
            parts = item.split(',')
            ref_number_str = parts[1].split(':')[1].strip()
            ref_number = int(ref_number_str)
            ref_numbers.add(ref_number)
        except (IndexError, ValueError):
            print(f"Warning: Invalid format in item '{item}'. Skipping.")
    return ref_numbers


# ------------------------------------------------------------------------
# 3bis. Extract references AFTER bibliography
# ------------------------------------------------------------------------
def extract_references_after_biblio(text):
    """
    Extract references and their corresponding numbers after the bibliography.
    Returns a list of dictionaries with:
      'ref_number_after_biblio_v1': int
      'ref_after_biblio_v1': str
    """
    references = []
    # This pattern captures [number] and the text until the next [number] or EOF
    for match in re.finditer(r"\[(\d+)\](.*?)(?=(?:\[(\d+)\]|$))", text, re.DOTALL):
        number = int(match.group(1))
        ref_text = match.group(2).strip()
        references.append({
            'ref_number_after_biblio_v1': number,
            'ref_after_biblio_v1': ref_text
        })
    return references


# ------------------------------------------------------------------------
# 4. Filter references AFTER bibliography to only keep matching references
# ------------------------------------------------------------------------
def filter_references_to_keep(unique_ref_numbers, references_after_biblio):
    """
    Filters references to keep only those whose numbers match the unique
    reference numbers that appeared before the bibliography.
    """
    filtered = []
    for ref in references_after_biblio:
        if ref['ref_number_after_biblio_v1'] in unique_ref_numbers:
            filtered.append(ref)
    return filtered


# ------------------------------------------------------------------------
# 5. Reindex references starting at 1
# ------------------------------------------------------------------------
def add_index_to_references(references):
    """Adds an 'index' key to each item, starting at 1."""
    for i, ref in enumerate(references):
        ref['index'] = i + 1
    return references


# ------------------------------------------------------------------------
# 5bis. Rename 'index' to 'ref_number_after_biblio_v2'
# ------------------------------------------------------------------------
def rename_index_in_references(references):
    """Renames the 'index' key to 'ref_number_after_biblio_v2'."""
    for ref in references:
        if 'index' in ref:
            ref['ref_number_after_biblio_v2'] = ref.pop('index')
    return references


# ------------------------------------------------------------------------
# 6. Add 'ref_number_after_biblio_v2' to bracketed references BEFORE bibliography
# ------------------------------------------------------------------------
def add_ref_number_after_biblio_v2(index_and_value_before, ref_after_biblio):
    """Adds 'ref_number_after_biblio_v2' to items in index_and_value_before
    based on matching the 'ref_number_v1' with 'ref_number_after_biblio_v1'.
    """
    # Create a dictionary for faster lookup
    ref_map = {}
    for ref in ref_after_biblio:
        ref_map[ref['ref_number_after_biblio_v1']] = ref['ref_number_after_biblio_v2']

    updated_items = []
    for item in index_and_value_before:
        try:
            parts = item.split(',')
            ref_number_v1_str = parts[1].split(':')[1].strip()
            ref_number_v1 = int(ref_number_v1_str)
            if ref_number_v1 in ref_map:
                item += f", ref_number_after_biblio_v2: {ref_map[ref_number_v1]}"
        except (IndexError, ValueError):
            print(f"Warning: Invalid format in item '{item}'. Skipping.")
        updated_items.append(item)

    return updated_items


# ------------------------------------------------------------------------
# 7. From the merged data, only keep index_v1 and ref_number_after_biblio_v2
# ------------------------------------------------------------------------
def extract_index_and_ref_num_v2(data):
    """Extracts index_v1 and ref_number_after_biblio_v2 from the list of strings."""
    extracted_data = []
    for item in data:
        try:
            parts = item.split(',')
            index_v1 = int(parts[0].split(':')[1].strip())
            ref_number_after_biblio_v2 = int(parts[2].split(':')[1].strip())
            extracted_data.append({
                'index_v1': index_v1,
                'ref_number_after_biblio_v2': ref_number_after_biblio_v2
            })
        except (IndexError, ValueError):
            print(f"Warning: Invalid format in item '{item}'. Skipping.")
    return extracted_data


# ------------------------------------------------------------------------
# 8. Replace bracketed numbers BEFORE biblio with reindexed numbers
# ------------------------------------------------------------------------
def replace_numbers_in_brackets(text, replacements):
    """Replaces bracketed numbers in 'text' with values from 'replacements'
    based on the bracket match index.
    """
    # Sort replacements in descending order of index_v1
    # to prevent messing up earlier matches as we replace
    replacements.sort(key=lambda x: x['index_v1'], reverse=True)

    pattern = r"\[(\d+)\]"
    matches = list(re.finditer(pattern, text))

    for repl in replacements:
        idx = repl['index_v1']
        new_num = repl['ref_number_after_biblio_v2']

        if 0 <= idx < len(matches):
            match = matches[idx]
            text = text[:match.start()] + f"[{new_num}]" + text[match.end():]

    return text


# ------------------------------------------------------------------------
# 9. Build new bibliography structure (markdown)
# ------------------------------------------------------------------------
def build_biblio_v2_markdown(references):
    """Constructs a markdown string for the new bibliography."""
    md = ""
    for ref in references:
        md += f"[{ref['ref_number_after_biblio_v2']}] {ref['ref_after_biblio_v1']}\n\n"
    return md


# ------------------------------------------------------------------------
# 10. Add title to bibliography
# ------------------------------------------------------------------------
def prepend_bibliography_title(biblio_markdown):
    """Adds '## Bibliography' as a title to the bibliography section."""
    return "## Bibliography\n\n" + biblio_markdown


# ------------------------------------------------------------------------
# 12. Filter out unused references from the original after-biblio list
# ------------------------------------------------------------------------
def filter_unused_references(unique_ref_numbers, references_after_biblio):
    """Removes references whose numbers are present in 'unique_ref_numbers'."""
    filtered = []
    for ref in references_after_biblio:
        if ref['ref_number_after_biblio_v1'] not in unique_ref_numbers:
            filtered.append(ref)
    return filtered


# ------------------------------------------------------------------------
# 13. Create markdown for unused sources
# ------------------------------------------------------------------------
def create_unused_sources_markdown(unused_references):
    """Constructs a markdown section listing the unused sources."""
    md = "##Unused Sources\n\n"
    for ref in unused_references:
        md += f"- {ref['ref_after_biblio_v1']}\n"
    return md




class Pipeline:
    def __init__(self):
        pass
        
    def __call__(self, txt_markdown_v1 : str) -> str:

        # 1. Split text
        txt_markdown_v1_before_biblio_v1, txt_markdown_v1_after_biblio_v1 = split_text_at_bibliography(txt_markdown_v1)

        # 2. Extract bracketed references BEFORE biblio
        index_and_value_before_biblio_v1 = extract_numbers_in_brackets(txt_markdown_v1_before_biblio_v1)

        # 3. Get unique references BEFORE biblio
        unique_ref_numbers_before_biblio_v1 = get_unique_ref_numbers(index_and_value_before_biblio_v1)

        # 3bis. Extract references AFTER biblio
        extract_references_and_citation_after_biblio_v1 = extract_references_after_biblio(txt_markdown_v1_after_biblio_v1)

        # 4. Keep only matching references AFTER biblio
        unique_ref_number_and_ref_after_biblio_v1 = filter_references_to_keep(
            unique_ref_numbers_before_biblio_v1,
            extract_references_and_citation_after_biblio_v1
        )

        # 5. Reindex references (add 'index')
        unique_ref_number_and_ref_after_biblio_v1 = add_index_to_references(unique_ref_number_and_ref_after_biblio_v1)

        # 5bis. Rename 'index' to 'ref_number_after_biblio_v2'
        unique_ref_number_and_ref_after_biblio_v1 = rename_index_in_references(unique_ref_number_and_ref_after_biblio_v1)

        # 6. Attach 'ref_number_after_biblio_v2' to bracketed refs BEFORE biblio
        index_v1_and_ref_num_v1_and_ref_num_v2_before_biblio = add_ref_number_after_biblio_v2(
            index_and_value_before_biblio_v1,
            unique_ref_number_and_ref_after_biblio_v1
        )

        # 7. From that, only keep index_v1 and ref_number_after_biblio_v2
        index_v1_and_ref_num_v2 = extract_index_and_ref_num_v2(index_v1_and_ref_num_v1_and_ref_num_v2_before_biblio)

        # 8. Replace bracketed numbers in the BEFORE biblio text
        txt_markdown_v1_before_biblio_v2 = replace_numbers_in_brackets(txt_markdown_v1_before_biblio_v1, index_v1_and_ref_num_v2)

        # 9. Build the new bibliography structure
        biblio_v2_markdown = build_biblio_v2_markdown(unique_ref_number_and_ref_after_biblio_v1)

        # 10. Add "## Bibliography" title
        biblio_v2_with_title_markdown = prepend_bibliography_title(biblio_v2_markdown)

        # 11. Combine the new text with the new bibliography
        final_markdown_v2 = txt_markdown_v1_before_biblio_v2 + biblio_v2_with_title_markdown

        # 12. Filter out unused references
        unused_ref_number_and_ref_after_biblio_v1 = filter_unused_references(
            unique_ref_numbers_before_biblio_v1,
            extract_references_and_citation_after_biblio_v1
        )

        # 13. Create markdown for unused sources
        unused_ref_number_and_ref_after_biblio_v2 = create_unused_sources_markdown(unused_ref_number_and_ref_after_biblio_v1)

        # 14. Append unused sources to final
        final_markdown_v2 += unused_ref_number_and_ref_after_biblio_v2
        
        return final_markdown_v2