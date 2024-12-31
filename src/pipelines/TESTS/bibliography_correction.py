import re

class Pipeline:
    def __init__(self):
        pass
        
    def __call__(self, markdown_content : str) -> str:

        def extract_numbers_before_bibliography(markdown_text):
            """
            Extracts numbers in brackets before "## Bibliography" from markdown text.
            """

            bibliography_index = markdown_text.find("## Bibliography")
            if bibliography_index == -1:
                text_to_search = markdown_text
            else:
                text_to_search = markdown_text[:bibliography_index]

            number_pattern = r"\[(\d+)\]"  # Regular expression to match numbers in brackets
            matches = re.findall(number_pattern, text_to_search)

            number_dict = {}
            for i, match in enumerate(matches):
                number_dict[i] = int(match)

            return number_dict


        cited_biblio_index_and_ref_number_v1 = extract_numbers_before_bibliography(markdown_content)
        cited_biblio_index_and_ref_number_v1


        ref_numbers_after_bibliography_v1 = []

        # Split the markdown content at "## Bibliography" and consider the part after it
        try:
            bibliography_section = markdown_content.split("## Bibliography")[1]
        except IndexError:
            print("No '## Bibliography' section found in the markdown content.")
            bibliography_section = ""

        # Use a regular expression to find numbers in brackets after "## Bibliography"
        matches = re.findall(r"\[(\d+)\]", bibliography_section)

        # Extract the numbers and convert them to integers
        for match in matches:
            try:
                ref_numbers_after_bibliography_v1.append(int(match))
            except ValueError:
                print(f"Skipping invalid number: {match}")


        #Main: keep only the unique numbers in the values from cited_biblio_index_and_ref_number_v

        unique_numbers_cited = list(set(cited_biblio_index_and_ref_number_v1.values()))

        #Main: Give me the articles not used

        unused_numbers_index = []
        for number in ref_numbers_after_bibliography_v1:
            if number not in unique_numbers_cited:
                unused_numbers_index.append(number)

        #Main: after ## Bibliography the number in bracket and the text that comes with it. Store in an array.
        all_bibliography_entries_v1 = []

        # Split the markdown content at "## Bibliography" and consider the part after it
        try:
            bibliography_section = markdown_content.split("## Bibliography")[1]
        except IndexError:
            print("No '## Bibliography' section found in the markdown content.")
            bibliography_section = ""

        # Use a regular expression to find entries like "[1] Some text"
        # This regex is more robust and handles variations in spacing and punctuation
        matches = re.findall(r"\[(\d+)\](.*?)(?=(?:\[\d+\]|$))", bibliography_section, re.DOTALL)

        # Store the matches in the array
        for match in matches:
            number = int(match[0])
            text = match[1].strip()  # Remove leading/trailing whitespace
            all_bibliography_entries_v1.append([number, text])

        #Main: Transform all_bibliography_entries_v1 variable in a dict.

        all_bibliography_dict_v1 = {}
        for entry in all_bibliography_entries_v1:
            all_bibliography_dict_v1[entry[0]] = entry[1]

        #Main: Unsued Biblio

        unused_biblio_ref = {}
        count = 0
        for number in unused_numbers_index:
            if number in all_bibliography_dict_v1:
                unused_biblio_ref[number] = all_bibliography_dict_v1[number]
                count += 1

        #Main:  Unsued Biblio in Markdown

        unused_biblio_markdown = ""
        for value in unused_biblio_ref.values():
            unused_biblio_markdown += f"- {value}\n\n"

        filtered_bibliography_v1 = {}
        for key, value in all_bibliography_dict_v1.items():
            if key in unique_numbers_cited:
                filtered_bibliography_v1[key] = value

        #Main:  Indexing filtered_bibliography_v1

        new_indexed_bibliography = {}
        for index, (key, value) in enumerate(filtered_bibliography_v1.items()):
            new_indexed_bibliography[index + 1] = {key: value}

        #Main:  Rearrange indexing of cited_biblio
        # Assuming cited_biblio_index_and_ref_number_v1 and new_indexed_bibliography are defined as in the previous code.

        updated_cited_biblio_with_ref_new_index = {}

        for index, ref_number in cited_biblio_index_and_ref_number_v1.items():
            found_match = False
            for parent_key, child_dict in new_indexed_bibliography.items():
                for child_key, _ in child_dict.items():
                    if ref_number == child_key:
                        updated_cited_biblio_with_ref_new_index[index] = parent_key
                        found_match = True
                        break  # Exit the inner loop if a match is found
                if found_match:
                    break #Exit the outer loop if a match is found

        #Main: Update the markdown with cited ref new index

        def update_markdown_references(markdown_content, updated_cited_biblio_with_ref_new_index):
            """Updates the markdown numbers in brackets using the values from updated_cited_biblio_with_ref_new_index."""

            for old_index, new_index in updated_cited_biblio_with_ref_new_index.items():
                markdown_content = re.sub(rf"\[{old_index}\]", f"[{new_index}]", markdown_content)

            return markdown_content

        updated_markdown_content = update_markdown_references(markdown_content, updated_cited_biblio_with_ref_new_index)

        #Main:  Updated biblio
        updated_biblio_markdown = ""
        for parent_key, child_dict in new_indexed_bibliography.items():
            for child_key, child_value in child_dict.items():
                updated_biblio_markdown += f"[{parent_key}] {child_value}\n\n"

        # Main: replace old biblio by updated biblio to file

        updated_and_final_markdown = updated_markdown_content.split("## Bibliography")[0] + "## Bibliography\n" + updated_biblio_markdown

        return updated_and_final_markdown

