import os, openai
from custom_types.PROMPT.type import PROMPT
from custom_types.XTRK.type import DataStructure, _create_model

_ = """We are preparing a data extraction pipeline. Our issue is the following:
the extraction grid is too big to fir in our pipeline. to solve this issue, we are going to remove from that grid the parameters which have a very low probability of being found by the pipeline (ie the ones that are NOT present in the document). For each of the parameters in the provided json schema, provide
* A probability between 0 and 1 of that parameter being present
   - 0.0 = ABSOLUTELY no doubt, not present anywhere  
   - 0.1 = No doubt, definitely not present anywhere  
   - 0.2 = Not present  
   - 0.3 = Small doubt, but seems either not present, or remotely present, but only indirectly/differently than expected  
   - 0.4 = Some doubt, vague traces or indirect presence possible, though still unlikely  
   - 0.5 = Unclear — presence is ambiguous or equally likely/unlikely; may depend on interpretation or definition  
   - 0.6 = Some signs point to it being present, but nothing conclusive; possible under certain conditions  
   - 0.7 = Likely present in some form, though perhaps not in the expected way or consistently  
   - 0.8 = Strong evidence of presence, fairly confident  
   - 0.9 = Very likely present; only a tiny doubt remains  
   - 1.0 = ABSOLUTELY certain, fully and clearly present  
Let me know if you'd like a visual version of this (like a scale or chart), or if you want the language tuned further for a specific domain.
Use the scale correctly, it's important, as it will be used to sort the parameters afterwards.
* A boolean (true/false). true means keep, false means not present, reject. As a reminder, here is the list of the parameters:
%s
If you forget any, you will be HEAVILY penalized. HEAVILY. If you just lazy out and return always the same value for each parameter, you will be HEAVILY penalized. HEAVILY. Score pertinantly and accurately, you will be rewarded with a lot of money for that. Also, I've been trying to make this pipeline work for hours now, I'm that close to jumping from the window. So just please do things right. Thanks mate ;)
"""

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 model : str = "o3-mini",
                 max_number_of_parameters : int = 50,
                 ):
        self.model = model
        self.max_number_of_parameters = max_number_of_parameters
    def __call__(self, 
                 text : str,
                 grid : DataStructure
                 ) -> DataStructure:
        # 1. Build the prompt
        p = PROMPT()
        p.add(text)
        params = '\n'.join([f'{_[0]} - {_[1]}' for f in grid.fields for _ in f.get_params_list()])
        p.add(_ % params)
        # 2. Call the model
        client = openai.OpenAI(api_key=os.environ.get("openai_api_key"))
        dic = client.beta.chat.completions.parse(
            model = self.model,
            messages = p.messages,
            response_format = grid.create_evaluation_model()  
        )
        dic = dic.choices[0].message.parsed
        dic = {
            dic.param_name: dic for dic in dic.evaluations
        }
        # 3. Sort the parameters
        root_fields = {_.object_name for _ in grid.fields}
        def note(param) -> float:
            note = dic.get(param, None)
            note = note.value if note is not None else None
            if note is not None and param in dic and note <= 0.4:
                return note
            elif param in root_fields:
                return 1.1 # let's keep the root ones :)
            elif note is not None:
                return note
            return 0.5
        all_fields = {_[0]: note(_[0]) for f in grid.fields for _ in f.get_params_list()}
        fields = list(all_fields.keys())
        fields.sort(key=lambda x: all_fields[x], reverse=True)
        
        # 4. Keep only the best parameters
        fields = fields[:self.max_number_of_parameters]
        grid = DataStructure.filter_fields(grid, fields)
        # 5. Return the grid
        return grid
        