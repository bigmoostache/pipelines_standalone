from custom_types.PROMPT.type import PROMPT
import datetime

def execute_and_replace(dic, code_string):
    dic['__date__'] = str(datetime.datetime.now())
    # Function to safely evaluate expressions using variables from the dictionary
    def evaluate_expression(expression, local_vars):
        try:
            # Evaluate the expression using variables from the dictionary
            return str(eval(expression, {}, local_vars))
        except Exception as e:
            # In case of any error, return an error message instead of causing a crash
            return f"Error in expression: {expression} - {e}"

    # Detect and replace code snippets within the string
    result_string = ""
    start_idx = 0
    while True:
        # Find the next occurrence of '{{'
        start = code_string.find("{{", start_idx)
        if start == -1:
            # No more occurrences
            result_string += code_string[start_idx:]
            break

        # Add everything before '{{' to the result
        result_string += code_string[start_idx:start]

        # Find the matching '}}'
        end = code_string.find("}}", start)
        if end == -1:
            # No closing '}}' found, just append the rest and break
            result_string += code_string[start:]
            break

        # Extract the expression inside '{{ ... }}'
        expression = code_string[start + 2:end].strip()

        # Evaluate and replace
        evaluated = evaluate_expression(expression, dic)
        result_string += evaluated

        # Move the search index past the '}}'
        start_idx = end + 2

    return result_string

class Pipeline:
    def __init__(self,
                 role:str,
                 format : str
                 ):
        assert role in {"user", "system", "assistant"}
        self.role = role
        self.format = format

    def __call__(self, dic : dict) -> PROMPT:
        prompt = execute_and_replace(dic, self.format)
        p = PROMPT()
        p.add(prompt, role = self.role)
        return p