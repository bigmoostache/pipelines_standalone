from custom_types.PROMPT.type import PROMPT

def execute_and_replace(dic, code_string):
    # Function to safely evaluate expressions using variables from the dictionary
    code_string = code_string.replace('\{', '_[_').replace('\}', '_]_')
    def evaluate_expression(expression, local_vars):
        try:
            # Evaluate the expression using variables from the dictionary
            return str(eval(expression, {}, local_vars))
        except Exception as e:
            # In case of any error, return the error message
            return f"Error in expression: {expression} - {e}"

    # Detect and replace code snippets within the string
    result_string = ""
    start_idx = 0
    while True:
        start_idx = code_string.find("{", start_idx)
        if start_idx == -1:
            break
        end_idx = code_string.find("}", start_idx)
        if end_idx == -1:
            break
        # Extract the expression within the brackets
        expression = code_string[start_idx + 1:end_idx]
        # Evaluate the expression and replace it in the string
        result_string += code_string[:start_idx] + evaluate_expression(expression, dic)
        code_string = code_string[end_idx + 1:]
        start_idx = 0

    result_string += code_string
    result_string = result_string.replace('_[_', '{').replace('_]_', '}')
    return result_string

class Pipeline:
    def __init__(self,
                 role:str,
                 format : str
                 ):
        assert role in {"user", "system", "assistant"}
        self.role = role
        self.format = format

    def __call__(self, p : PROMPT, dic : dict) -> PROMPT:
        prompt = execute_and_replace(dic, self.format)
        p.add(prompt, role = self.role)
        return p