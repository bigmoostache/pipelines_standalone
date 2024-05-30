style = """<style>
    /* Base styles */
/* Headings */
.h2_drz, .h3_drz {
    text-align: center;
    margin-bottom: 20px;
}

/* Scroller styles */
.scroller_div_drz {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: rgba(0, 0, 0, 0.05);
    padding: 10px;
    margin-bottom: 15px;
    border-radius: 8px;
}

.scroller_range_drz {
    -webkit-appearance: none;
    width: 60%;
    height: 8px;
    margin-top: 0;
    margin-bottom: 0;
    border-radius: 5px;
    background: #ddd;
    outline: none;
    opacity: 0.7;
    -webkit-transition: .2s;
    transition: opacity .2s;
}

.scroller_range_drz:hover {
    opacity: 1;
}

.scroller_range_drz::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #666;
    cursor: pointer;
}

.scroller_range_drz::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #666;
    cursor: pointer;
}

/* Choice styles */
.choice_div_drz {
    margin-bottom: 20px;
    background-color: rgba(0, 0, 0, 0.05);
    padding: 10px;
    border-radius: 8px;
}

.choice_label_drz {
    margin-right: 20px;
}

/* Custom radio button */
.choice_div_drz {
    display: flex;
    flex-wrap: wrap;
    gap: 10px; /* Adds space between the inputs */
    align-items: center; /* Aligns items vertically */
    margin-bottom: 20px;
    background-color: rgba(0, 0, 0, 0.05);
    padding: 10px;
    border-radius: 8px;
}

.choice_input_drz {
    -webkit-appearance: none;
    appearance: none;
    margin: 0;
    font: inherit;
    color: currentColor;
    width: 1.15em;
    height: 1.15em;
    border: 2px solid gray; /* Updated border style */
    border-radius: 50%; /* Keeps it rounded */
    display: inline-flex; /* Aligns text and icon nicely, and respects the flex layout */
    justify-content: center;
    align-items: center;
}

.choice_input_drz:checked::before {
    content: "";
    width: 0.65em;
    height: 0.65em;
    border-radius: 50%;
    background-color: #666;
}


/* Results styles */
.results_div_drz {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 8px;
}

.results_span_drz {
    float: right;
}

/* Ensure the calculate script runs without visual glitch */
.scroller_range_drz:active, .choice_input_drz:active {
    transition: none;
}

</style>"""

def build_html(dic, calculate):
    title = dic["Title"]
    description = dic["Description"]
    scrollers = "\n".join([f'<div class = "scroller_div_drz"><label class = "scroller_label_drz">{x["Name"]} <br>({x["Unit"]}):</label><span  class = "scroller_span_drz" id = "{x["Variable Name"]}val"></span><input class = "scroller_range_drz" onmousemove="calculate()" onchange="calculate()" type="range" id="{x["Variable Name"]}" value="0" step="0.01", min = "0", max = "1"></div>'
                        for x in dic["Inputs"]])
    choices = "\n".join([f'<div class = "choice_div_drz">\n\t<label  class = "choice_label_drz">{x["Name"]}:</label>\n\t'+
                    "\n\t".join([f'<input  class = "choice_input_drz" type="radio" id="{y}" name="{x["Variable Name"]}" value="{y}" onclick="calculate()" {"checked" if i == 0 else ""}>{y}</input>' for i,y in enumerate(x['Options'])])
                    + '\n</div>' for x in dic["Variable Parameters"]])
    results = "\t"+'\n\t'.join([f'<div class = "results_div_drz">{x["Name"]}: <span class = "results_span_drz" id="{x["Variable Name"]}">0 {x["Unit"]}</span></div>' for x in dic["Outputs"]])

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <script>
    {calculate}
    </script>

    {style}
    </head>
    <body>
    <h2 class = "h2_drz">{title}</h2>
    <h3 class = "h3_drz">{description}</h3>

    <!-- Scrollers -->
    {scrollers}

    <!-- Multiple Choices -->
    {choices}

    <!-- Results -->
    <h3 class = "h3_drz">Results</h3>
    {results}

    <script>calculate()</script>
    </body>
    </html>
    """
    return html

class Pipeline:
    def __init__(self
                 ):
        pass

    def __call__(self, dic : dict, calculate : str) -> str:
        calculate = calculate[calculate.find("function calculate() {"):]
        calculate = calculate[:calculate.find("```")]
        return build_html(dic, calculate)