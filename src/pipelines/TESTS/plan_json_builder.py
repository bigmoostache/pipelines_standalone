from custom_types.JSONL.type import JSONL

class Pipeline:
    def __init__(self, 
                 ):
        pass
        
    def __call__(self, x : str) -> JSONL:
        x = x.split('\n## ')
        subsections = []
        for i, y in enumerate(x):
            title = y.split('\n')[0].replace('## ', '').strip()
            y = '\n'.join(y.split('\n')[1:]).strip()
            z = y.split('\n### ')
            res = {'title':title, "section" : i+1}
            for j,a in enumerate(z):
                subtitle = a.split('\n')[0].replace('### ', '').strip()
                a = '\n'.join(a.split('\n')[1:])
                d = a.find('Details:')
                abstract = a[:d].replace('Abstract: ', '').strip()
                contents = [_.strip() for _ in a[d:].split('\n')[1:] if _.strip()]
                contents = [_[1:] if _.startswith('-') else _ for _ in contents]
                subsections.append( {**res, 'subtitle':subtitle, 'show_subtitle':'### '+subtitle if j>0 else f'## {res["title"]}\n### {subtitle}', 'subsection' : j+1, 'abstract':abstract, 'contents':contents} )
        subsections = [{**_, 'index':i} for i,_ in enumerate(subsections)]
        return JSONL(subsections)
    
example_input = """
## 1. General Principles of Classification
### 1. Historical Context and Evolution of Knee Arthroplasty Classification
Abstract: This subsection will explore the historical development of knee arthroplasty, highlighting the transition from early surgical techniques to the modern era of TKA, UKA, and PFA. It will discuss the origins of CPKA and the evolution of arthroplasty classification, emphasizing the role of MeSH in standardizing terminology within the medical literature.
Details:
	-Brief introduction to the development of knee arthroplasty procedures.
	-Transition from early arthroplasty techniques to modern TKA and PKA.
	-The emergence of UKA as an alternative to TKA for isolated compartmental OA.
	-Historical use of PFA and its integration into knee arthroplasty options.
	-The initial concept of CPKA and its early clinical applications.
	-Evolution of terminology and classification from historical texts to current literature.
	-The role of medical subject headings (MeSH) in standardizing knee arthroplasty terminology.

### 2. Anatomical and Procedural Foundations for Classification
Abstract: This subsection will delve into the anatomical compartments of the knee and their implications for arthroplasty, defining TKA and PKA. It will clarify the variations of UKA and the role of PFA, introducing CPKA configurations. The necessity for a standardized classification system to accurately describe these procedures will be underscored.
Details:
	-The significance of the knee's anatomical compartments in arthroplasty.
	-Criteria for distinguishing between TKA and PKA based on the extent of disease.
	-Definition and variations of UKA, including medial, lateral, and bicompartmental types.
	-The specific role of PFA in addressing patellofemoral joint disease.
	-Introduction to the various configurations of CPKA and their clinical indications.
	-The rationale behind the need for a standardized classification system in PKA.

## 2. Modes of Fixation
### 1. Historical and Biomechanical Foundations of Fixation in Knee Arthroplasty
Abstract: This subsection will delve into the historical progression of fixation methods in knee arthroplasty, highlighting the shift from cemented to cementless techniques. It will discuss the biomechanical principles that inform fixation choices, including the interplay between implant design, bone quality, and patient anatomy. Historical success rates and their influence on current surgical practices will also be examined.
Details:
	-Overview of the evolution of fixation methods in knee arthroplasty.
	-The transition from cemented to cementless and hybrid fixation techniques.
	-Biomechanical principles that guide the choice of fixation.
	-The influence of implant design on fixation stability.
	-The role of bone quality and patient anatomy in determining fixation strategy.
	-Historical success rates of different fixation methods and their impact on surgical practice.

### 2. Clinical Outcomes and Longevity: Cemented vs. Cementless Fixation
Abstract: This subsection will compare the clinical outcomes associated with cemented and cementless fixation methods, including implant longevity and revision rates. It will explore how different fixation approaches affect postoperative pain, recovery, and complication rates, drawing on registry data and patient-reported outcomes to assess overall patient satisfaction.
Details:
	-Comparative analysis of revision rates for cemented and cementless fixation.
	-Discussion on the longevity of implants with different fixation modes.
	-The impact of fixation method on postoperative pain and recovery.
	-Review of registry data on the performance of cemented and cementless implants.
	-The influence of fixation on the incidence of complications such as aseptic loosening.
	-Patient-reported outcomes and satisfaction levels associated with each fixation type.
"""