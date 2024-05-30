import json

def build_html(dic):
    calculate = "function calculate() {\n\t"\
            +"\n\n\t".join([f'var {x["Variable Name"]}_log = parseFloat(document.getElementById(\'{x["Variable Name"]}\').value); // {x["Name"]}\n' 
                                + (f'\tvar {x["Variable Name"]} = ({x["Range"][0]}**(1-{x["Variable Name"]}_log))*({x["Range"][1]}**{x["Variable Name"]}_log)\n' if x["Range"][0] > 0 else f'\tvar {x["Variable Name"]} = ({x["Range"][0]}*(1-{x["Variable Name"]}_log))+({x["Range"][1]}*{x["Variable Name"]}_log)\n')
                                + f'\tdocument.getElementById(\'{x["Variable Name"]}val\').innerText = {x["Variable Name"]}.toFixed(2) + \' {x["Unit"]}\''
                                for x in dic["Inputs"]]) \
            + '\n\n\n' + '\n\n\n'.join([
                f'\tvar {x["Variable Name"]} = document.querySelector(\'input[name="{x["Variable Name"]}"]:checked\').value;\n' +
                f'\tvar {x["Variable Name"]}Index = {x["Options"]}.indexOf({x["Variable Name"]});\n\n' + 
                '\n\n'.join([
                    f'\tvar {y["Variable Name"]}Options = {y["Values"]};\n' + 
                    f'\tvar {y["Variable Name"]} = {y["Variable Name"]}Options[{x["Variable Name"]}Index] // {y["Name"]}'
                    for y in x["Values"]
                ])
            for x in dic["Variable Parameters"]]) \
            + '\n\n\n' + '\n'.join([
                f'\tvar {x["Variable Name"]} = {x["Value"]}; // {x["Name"]}'
                for x in dic["Parameters"]
            ]) \
            + f'\n\n/* Use the description below to correct and complete this function :\n {json.dumps(dic["Outputs"], indent = 4)} */ \n\n' \
            + '\n'.join([
                f'\tdocument.getElementById(\'{x["Variable Name"]}\').innerText = {x["Variable Name"]}.toFixed(2) + \' {x["Unit"]}\';'
                for x in dic["Outputs"]
            ]) + "\n}"

    return calculate
class Pipeline:
    def __init__(self
                 ):
        pass

    def __call__(self, dic : dict) -> str:
        return build_html(dic)