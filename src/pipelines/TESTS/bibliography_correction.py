import re

class Pipeline:
    def __init__(self):
        pass
        
    def __call__(self, markdown_content : str) -> str:

        # 1.Split text before and after the Bibliography
        # Split the txt_markdown_v1 string at "## Bibliography"
        txt_markdown_v1 = markdown_content
        split_index = txt_markdown_v1.find("## Bibliography")
        
        if split_index != -1:
            txt_markdown_v1_before_biblio_v1 = txt_markdown_v1[:split_index]
            txt_markdown_v1_after_biblio_v1 = txt_markdown_v1[split_index:]
        else:
            txt_markdown_v1_before_biblio_v1 = txt_markdown_v1
            txt_markdown_v1_after_biblio_v1 = "" # or handle the case where the string isn't found
        
        # **2. extract_numbers_in_brackets BEFORE Biblio with index and values. Exemple ['index_v1: 0, ref_number_v1: 2', 'index_v1: 1, ref_number_v1: 19'**
        def extract_numbers_in_brackets(text):
          """Extracts numbers enclosed in square brackets from a given text."""
          output = []
          matches = re.findall(r"\[(\d+)\]", text)
          for i, match in enumerate(matches):
            output.append(f"index_v1: {i}, ref_number_v1: {match}")
          return output
        
        # Assuming markdown_to_jsonl contains the string you want to analyze
        index_and_value_before_biblio_v1 = extract_numbers_in_brackets(txt_markdown_v1_before_biblio_v1)
        # print(index_and_value_before_biblio_v1)
        
        # **3.Unique ref_number BEfore unique_ref_numbers_before_biblio_v1**
        # prompt: keep the untique "ref_number_v1" from variabe index_and_value_v1. Make a function
        
        def get_unique_ref_numbers(index_and_value_list):
            """
            Extracts unique ref_number_v1 values from a list of strings.
        
            Args:
                index_and_value_list: A list of strings in the format "index_v1: X, ref_number_v1: Y".
        
            Returns:
                A set containing the unique ref_number_v1 values.
            """
            ref_numbers = set()
            for item in index_and_value_list:
                try:
                    parts = item.split(',')
                    ref_number_str = parts[1].split(':')[1].strip()
                    ref_number = int(ref_number_str)  # Convert to integer
                    ref_numbers.add(ref_number)
                except (IndexError, ValueError):
                    print(f"Warning: Invalid format in item '{item}'. Skipping.")
            return ref_numbers
        
        unique_ref_numbers_before_biblio_v1 = get_unique_ref_numbers(index_and_value_before_biblio_v1)
        # unique_ref_numbers_before_biblio_v1
        
        # **3bis. ALL extract_references_and_citation_after_biblio_v1**
        # prompt: structure variable extract_references_after_biblio_v1 like this ref_number_after_biblio_v1: [number], ref_after_biblio_v1: 'text'
        
        def extract_references_after_biblio(text):
            """
            Extracts references and their corresponding numbers after the bibliography.
            Returns a list of dictionaries, where each dictionary has 'ref_number_after_biblio_v1' and 'ref_after_biblio_v1'.
            """
            references = []
            for match in re.finditer(r"\[(\d+)\](.*?)(?=(?:\[(\d+)\]|$))", text, re.DOTALL):
                number = match.group(1)
                text_after_number = match.group(2).strip()
                references.append({
                    'ref_number_after_biblio_v1': int(number),  # Convert to integer
                    'ref_after_biblio_v1': text_after_number
                })
            return references
        
        # Example usage (assuming markdown_to_jsonl_after_biblio_v1 is defined)
        extract_references_and_citation_after_biblio_v1 = extract_references_after_biblio(txt_markdown_v1_after_biblio_v1)
        # print(f"Test: extract_references_and_citation_after_biblio_v1:")
        # extract_references_and_citation_after_biblio_v1
        
        
        # 4. Clean up biblio v1 with article cited. Unique v1 after Biblio num v1, re, num v2 unique_ref_number_and_ref_after_biblio_v1
        # prompt: only keep the ref_number_after_biblio_v1 values that match the unique_ref_numbers_before_biblio_v1's numbers
        
        def filter_references(unique_ref_numbers, references_after_biblio):
            """
            Filters references to keep only those whose numbers match the unique reference numbers.
            """
            filtered_references = []
            for ref in references_after_biblio:
                if ref['ref_number_after_biblio_v1'] in unique_ref_numbers:
                    filtered_references.append(ref)
            return filtered_references
        
        unique_ref_number_and_ref_after_biblio_v1 = filter_references(unique_ref_numbers_before_biblio_v1, extract_references_and_citation_after_biblio_v1)
        # unique_ref_number_and_ref_after_biblio_v1
        
        # # 5. ALL Reindexing all blblio v1
        
        # # prompt: for unique_ref_number_and_ref_after_biblio_v1 add an index for each item starting at n=1
        
        # Assuming the previous code is already executed and
        # unique_ref_number_and_ref_after_biblio_v1 is defined
        
        def add_index_to_references(references):
            """Adds an index to each item in the references list, starting at n=1."""
            for i, ref in enumerate(references):
                ref['index'] = i + 1  # Add the index starting from 1
            return references
        
        unique_ref_number_and_ref_and_index_after_biblio_v1 = add_index_to_references(unique_ref_number_and_ref_after_biblio_v1)
        # unique_ref_number_and_ref_and_index_after_biblio_v1
        
        
        
        
        # 5bis. Rename 'index' by 'ref_number_after_biblio_v2'
        # prompt: for unique_ref_number_and_ref_and_index_after_biblio_v1 rename 'index' by 'ref_number_after_biblio_v2'
        
        # Assuming the previous code is already executed and
        # unique_ref_number_and_ref_and_index_after_biblio_v1 is defined
        
        def rename_index_in_references(references):
            """Renames the 'index' key to 'ref_number_after_biblio_v2' in each dictionary."""
            for ref in references:
                if 'index' in ref:
                    ref['ref_number_after_biblio_v2'] = ref.pop('index')
            return references
        
        unique_ref_number_and_ref_and_index_after_biblio_v1 = rename_index_in_references(unique_ref_number_and_ref_and_index_after_biblio_v1)
        # unique_ref_number_and_ref_and_index_after_biblio_v1
        
        
        # **6. Replace ref_number_after_biblio_v2 in ref_number_bedore_biblio_v1**
        # prompt: in unique_ref_number_and_ref_and_indexv2_after_biblio_v1 for each item match with index_and_value_before_biblio_v1 based ref_number_after_biblio_v1's value.
        # Add 'ref_number_after_biblio_v2' to index_and_value_before_biblio_v1
        
        def add_ref_number_after_biblio_v2(index_and_value_before, ref_after_biblio):
            """Adds 'ref_number_after_biblio_v2' to items in index_and_value_before based on matching ref_number_v1."""
        
            # Create a dictionary for faster lookup of ref_number_after_biblio_v2
            ref_number_map = {}
            for ref in ref_after_biblio:
                ref_number_map[ref['ref_number_after_biblio_v1']] = ref['ref_number_after_biblio_v2']
        
            updated_index_and_value = []
            for item in index_and_value_before:
              try:
                  parts = item.split(',')
                  ref_number_v1_str = parts[1].split(':')[1].strip()
                  ref_number_v1 = int(ref_number_v1_str)
                  if ref_number_v1 in ref_number_map:
                      item += f", ref_number_after_biblio_v2: {ref_number_map[ref_number_v1]}"
                  updated_index_and_value.append(item)
              except (IndexError, ValueError):
                  print(f"Warning: Invalid format in item '{item}'. Skipping.")
                  updated_index_and_value.append(item) # Append even if invalid to maintain original list length
                  continue
            return updated_index_and_value
        
        index_v1_and_ref_num_v1_and_ref_num_v2_before_biblio = add_ref_number_after_biblio_v2(index_and_value_before_biblio_v1, unique_ref_number_and_ref_and_index_after_biblio_v1)
        # index_v1_and_ref_num_v1_and_ref_num_v2_before_biblio
        
        
        
        # 7. Remove ref_number_v1 and only keep index before bliblio and matching ref_number_after_biblio_v2
        # prompt: from index_v1_and_ref_num_v1_and_ref_num_v2_before_biblio only keep index_v1, ref_number_after_biblio_v2.
        
        # Assuming index_v1_and_ref_num_v1_and_ref_num_v2_before_biblio is defined from the previous code
        
        def extract_index_and_ref_num_v2(data):
            """Extracts index_v1 and ref_number_after_biblio_v2 from the input data."""
            extracted_data = []
            for item in data:
                try:
                    parts = item.split(',')
                    index_v1 = int(parts[0].split(':')[1].strip())
                    ref_number_after_biblio_v2 = int(parts[2].split(':')[1].strip())
                    extracted_data.append({'index_v1': index_v1, 'ref_number_after_biblio_v2': ref_number_after_biblio_v2})
                except (IndexError, ValueError):
                    print(f"Warning: Invalid format in item '{item}'. Skipping.")
            return extracted_data
        
        index_v1_and_ref_num_v2 = extract_index_and_ref_num_v2(index_v1_and_ref_num_v1_and_ref_num_v2_before_biblio)
        # index_v1_and_ref_num_v2
        
        
        
        # **8. Replace number in brackets before biblio v2 by v1**
        # prompt: in markdown_to_jsonl_before_biblio_v1 replace the numbers in brackets [] using their index by the values in ref_number_after_biblio_v2 index_v1_and_ref_num_v2.
        # index_v1 = index and value of ref_number_after_biblio_v2 = value of number
        
        def replace_numbers_in_brackets(text, replacements):
            """Replaces bracketed numbers in text with values from replacements."""
            # Sort replacements by index_v1 in descending order to avoid issues with overlapping replacements
            replacements.sort(key=lambda x: x['index_v1'], reverse=True)
        
            for replacement in replacements:
                index_v1 = replacement['index_v1']
                ref_number_after_biblio_v2 = replacement['ref_number_after_biblio_v2']
        
                # Construct the regex pattern to match the bracketed number at the specified index
                pattern = r"\[(\d+)\]"  # Match [number]
                matches = list(re.finditer(pattern, text))
                if 0 <= index_v1 < len(matches):
                  match = matches[index_v1]
                  original_number = match.group(0)
                  text = text[:match.start()] + f"[{ref_number_after_biblio_v2}]" + text[match.end():]
        
            return text
        
        txt_markdown_v1_before_biblio_v2 = replace_numbers_in_brackets(txt_markdown_v1_before_biblio_v1, index_v1_and_ref_num_v2)
        # txt_markdown_v1_before_biblio_v2
        
        
        
        
        # ***9. Create Biblio structure ***
        # prompt: struture unique_ref_number_and_ref_and_index_after_biblio_v1 like this:
        # [value of ref_number_after_biblio_v2] value of ref_after_biblio_v1 skip a line and [value of ref_number_after_biblio_v2] value of ref_after_biblio_v1
        # store it in a markdown named biblio_v2_markdown
        
        # Assuming unique_ref_number_and_ref_and_index_after_biblio_v1 is defined
        
        biblio_v2_markdown = ""
        for item in unique_ref_number_and_ref_and_index_after_biblio_v1:
            biblio_v2_markdown += f"[{item['ref_number_after_biblio_v2']}] {item['ref_after_biblio_v1']}\n\n"
        
        # Save the markdown string to a file named biblio_v2_markdown.md
        # with open("biblio_v2_markdown.md", "w") as f:
        #   f.write(biblio_v2_markdown)
        # biblio_v2_markdown
        # print(biblio_v2_markdown)
        
        
        
        
        # 10. Adding title to Bibliography
        # prompt: add to biblio_v2_markdown on top ## Bibliography, skip a line and the rest of the content
        
        biblio_v2_with_title_markdown = "## Bibliography\n\n" + biblio_v2_markdown
        
        # print(biblio_v2_with_title_markdown)
        
        
        
        
        # **11. Combine content and bibilio**
        # prompt: combine txt_markdown_v1_before_biblio_v2 followed by biblio_v2_with_title_markdown
        
        # Combine txt_markdown_v1_before_biblio_v2 and biblio_v2_with_title_markdown
        final_markdown_v2 = txt_markdown_v1_before_biblio_v2 + biblio_v2_with_title_markdown
        
        # final_markdown_v2
        
        
        
        
        
        # 12 .remove unused sourced from biblio
        # prompt: From extract_references_and_citation_after_biblio_v1remove the values in ref_number_after_biblio_v1 matching the values in unique_ref_numbers_before_biblio_v1
        
        def filter_references(unique_ref_numbers, references_after_biblio):
            """
            Filters references to remove those whose numbers are present in unique_ref_numbers.
            """
            filtered_references = []
            for ref in references_after_biblio:
                if ref['ref_number_after_biblio_v1'] not in unique_ref_numbers:
                    filtered_references.append(ref)
            return filtered_references
        
        unused_ref_number_and_ref_after_biblio_v1 = filter_references(unique_ref_numbers_before_biblio_v1, extract_references_and_citation_after_biblio_v1)
        # unused_ref_number_and_ref_after_biblio_v1
        
        
        
        
        # **13. Create unused sources**
        # prompt: Create a line at the top named "##Unused Sources", skip a line and in unused_ref_number_and_ref_after_biblio_v1 only keep the value of ref_after_biblio_v1 and strucuture it like this: - value of ref_after_biblio_v1. Store all of it in unused_ref_number_and_ref_after_biblio_v2
        
        unused_ref_number_and_ref_after_biblio_v2 = ""
        unused_ref_number_and_ref_after_biblio_v2 += "##Unused Sources\n\n"
        for ref in unused_ref_number_and_ref_after_biblio_v1:
            unused_ref_number_and_ref_after_biblio_v2 += f"- {ref['ref_after_biblio_v1']}\n"
        unused_ref_number_and_ref_after_biblio_v2
        # print(unused_ref_number_and_ref_after_biblio_v2)
        
        
        # 14. Append unused sources
        # prompt: Append unused_ref_number_and_ref_after_biblio_v2 at the end of final_markdown_v2
        
        final_markdown_v2 = final_markdown_v2 + unused_ref_number_and_ref_after_biblio_v2
        return final_markdown_v2
