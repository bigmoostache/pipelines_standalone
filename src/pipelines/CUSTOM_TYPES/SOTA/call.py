from custom_types.SOTA.type import SOTA, VersionedInformation, extract_references
from custom_types.JSONL.type import JSONL
from custom_types.PROMPT.type import PROMPT
from custom_types.LUCARIO.type import LUCARIO, Document
from pipelines.CONVERSIONS.JSONL.to_txt import Pipeline as JSONL2Txt
from pipelines.LLMS_v2.json_dict_output import Pipeline as LLMS_v2
import json
from typing import Literal
from openai import OpenAI
import logging

def build_references(sota : SOTA, information_id: int, references: Literal['allow', 'restrict', 'free']) -> JSONL:
    logging.debug(f'Building references for information_id {information_id} with mode {references}')
    if references == 'allow':
        allow_external, force_keep_documents, force_keep_chunks = True, True, True
    elif references == 'restrict':
        allow_external, force_keep_documents, force_keep_chunks = False, True, True
    elif references == 'free':
        allow_external, force_keep_documents, force_keep_chunks = True, False, True
    res = sota.build_references(information_id=information_id, allow_external=allow_external, force_keep_documents=force_keep_documents, force_keep_chunks=force_keep_chunks)
    res = JSONL([_ for _ in res if information_id in _['assigned_to']])
    for _ in res.lines:
        _['text'] = '\t'.join([] + _['text'].splitlines(True))
    to_txt_pipe = JSONL2Txt(
        formatting=sota.t('', {'': {
                'en': '<reference informationid="{referenced_information}" position="{chunk_id}">\n\t<!-- Refer to this chunk as "<reference informationid="{referenced_information}" position="{chunk_id}"/>"  -->\n{text}\n</reference informationid="{referenced_information}" position="{chunk_id}">',
                'fr': '<reference informationid="{referenced_information}" position="{chunk_id}">\n\t<!-- Référez-vous à cet extrait comme "<reference informationid="{referenced_information}" position="{chunk_id}"/>"  -->\n{text}\n</reference informationid="{referenced_information}" position="{chunk_id}">'
            }}),
        sort_by='position',
        joiner=sota.t('', {'': {
                'en': '\n\n\n====================== NEW DOCUMENT ============================\n\n\n',
                'fr': '\n\n\n====================== NOUVEAU DOCUMENT ============================\n\n\n'
            }}),
        grouped=True,
        group_by='referenced_information',
        group_format=sota.t('', {'': {
                'en': '# Reference {referenced_information}\n>> To cite inline this article as a whole: "<reference informationid="{referenced_information}" />"\n>> Context for this document: {reference}',
                'fr': '# Référence {referenced_information}\n>> Pour citer en ligne cet article dans son ensemble: "<reference informationid="{referenced_information}" />"\n>> Contexte pour ce document: {reference}'
            }}),
        group_joiner='?\n\n...\n\n'
    )
    text = to_txt_pipe(res)
    return text

def get_html_format(sota : SOTA):
    logging.debug('Building HTML format prompt')
    format_prompt = {"format": {
        "en": "```html\t\n<p>Examples:</p>\n<ul>\n    <li>\n        <p>bullet</p>\n    </li>\n    <li>\n        <p>points</p>\n        <ul>\n            <li>\n                <p>nested</p>\n            </li>\n            <li>\n                <p>bullet points</p>\n            </li>\n        </ul>\n    </li>\n</ul>\n<p></p>\n<ol>\n    <li>\n        <p>numbered</p>\n    </li>\n    <li>\n        <p>list</p>\n        <ol>\n            <li>\n                <p>nested</p>\n            </li>\n            <li>\n                <p>numbered list</p>\n            </li>\n        </ol>\n    </li>\n</ol>\n<table style=\"min-width: 50px\">\n    <colgroup>\n        <col style=\"min-width: 25px\">\n        <col style=\"min-width: 25px\">\n    </colgroup>\n    <tbody>\n        <tr>\n            <th colspan=\"1\" rowspan=\"1\">\n                <p>Example</p>\n            </th>\n            <th colspan=\"1\" rowspan=\"1\">\n                <p>Table</p>\n            </th>\n        </tr>\n        <tr>\n            <td colspan=\"1\" rowspan=\"1\">\n                <p>Example cell</p>\n            </td>\n            <td colspan=\"1\" rowspan=\"2\">\n                <p>Example merged cells (vertical)</p>\n            </td>\n        </tr>\n        <tr>\n            <td colspan=\"1\" rowspan=\"1\">\n                <p><strong>Example </strong><u>cell </u><em>with format </em><span style=\"color: rgb(208, 2, 27)\">in\n                    </span><mark data-color=\"#4a90e2\" style=\"background-color: #4a90e2; color: inherit\">it</mark></p>\n            </td>\n        </tr>\n        <tr>\n            <td colspan=\"2\" rowspan=\"1\">\n                <p>Example merged cells (horizontal)</p>\n            </td>\n        </tr>\n    </tbody>\n</table>\n<h1 id=\"heading-9hlqdjns\">h1 title</h1>\n<h2 id=\"heading-un65fqgv\">h2 title</h2>\n<h3 id=\"heading-kh4l9y64\">h3 title</h3>\n<p><span style=\"color: #417505\">Colored text</span></p>\n<p><mark data-color=\"#bd10e0\" style=\"background-color: #bd10e0; color: inherit\">Highlighted text</mark></p>\n<p>Example <span style=\"font-family: Times New Roman\">font</span></p>\n<p>Examples <strong>bold</strong>, <em>italic</em>, <u>underline</u>, <s>strikethrough</s></p>\n<p style=\"text-align: left\">Left align</p>\n<p style=\"text-align: center\">Middle align</p>\n<p style=\"text-align: right\">Right align</p>\n<p style=\"text-align: justify\">Justify align</p>\n<p>Example reference: <reference informationid=\"12\" position=\"3456\"/></p>\n<p>Example reference without position: <reference informationid=\"12\"/></p>\n```\n"
        }}
    return sota.t('format', format_prompt)
    
def get_json_schema(sota : SOTA,
                    act_on_title: bool = True,
                    act_on_expectations: bool = False,
                    act_on_comments: bool = False,
                    act_on_contents: bool = False):
    logging.debug('Building JSON schema')
    html_a_priori_comment = sota.t('', {'': {
        'en': 'Based on the provided information and instructions, provide a comment in html format as per specified by the HTML Format instructions. This comment\'s purpose is to reflect on the provided task and provide insights on the strategy adopted to tackle it. You may refer to references here, put bullet points, text formatting, etc. Basically the same as html_content.',
        'fr': 'En fonction des informations et instructions fournies, fournissez un commentaire au format html tel que spécifié par les instructions de format HTML. Le but de ce commentaire est de réfléchir à la tâche fournie et de fournir des informations sur la stratégie adoptée pour la traiter. Vous pouvez faire référence aux références ici, mettre des puces, formater le texte, etc. Fondamentalement la même chose que html_content.'
        }})
    title_description = sota.t('', {'': {
        'en': 'Section title, deprived of any html formatting. Do NOT change it.',
        'fr': 'Titre de la section, dépourvu de tout formatage html. Ne le changez PAS.'
        }}) if not act_on_title else sota.t('', {'': {
        'en': 'Section title, deprived of any html formatting. You may change it.',
        'fr': 'Titre de la section, dépourvu de tout formatage html. Vous pouvez le changer.'
        }})
    html_expectations_description = sota.t('', {'': {
        'en': 'Section expectations both in terms of content and formatting. Rewrite those expectations, in html as per specified by the HTML Format instructions. You may also refer to references here, put bullet points, text formatting, etc. Basically the same as html_content.',
        'fr': 'Attentes de la section à la fois en termes de contenu et de formatage. Réécrivez ces attentes, en html tel que spécifié par les instructions de format HTML. Vous pouvez faire référence aux références ici, mettre des puces, formater le texte, etc. Fondamentalement la même chose que html_content.'
        }})
    html_content_description = sota.t('', {'': {
        'en': 'Section contents, formatted as per specified by the HTML format instructions above. Do NOT include either the section title, the expectations nor the comments in there.',
        'fr': 'Contenu de la section, formaté comme spécifié par les instructions de format HTML ci-dessus. N\'incluez ni le titre de la section, ni les attentes, ni les commentaires.'
        }})
    html_a_posteriori_comment = sota.t('', {'': {
        'en': 'If you want to add a last a-posteriori comment, a feedback, hints at how to enhance this section or whatever, do it here, in html too, same as html_contents. You may also refer to references here, put bullet points, text formatting, etc. Basically the same as html_content.',
        'fr': 'Si vous souhaitez ajouter un dernier commentaire a-posteriori, un retour, des indices sur la manière d\'améliorer cette section ou autre, faites-le ici, en html également, de la même manière que html_contents. Vous pouvez également faire référence aux références ici, mettre des puces, formater le texte, etc. Fondamentalement la même chose que html_content.'
        }})
    
    fields = {
                "html_a_priori_comment": {
                    "type": "string",
                    "description": html_a_priori_comment
                },
                "title": {
                    "type": "string",
                    "description": title_description
                },
                "html_expectations": {
                    "type": "string",
                    "description": html_expectations_description
                },
                "html_content": {
                    "type": "string",
                    "description": html_content_description
                },
                "html_a_posteriori_comment": {
                    "type": "string",
                    "description": html_a_posteriori_comment
                }
            }
    required = ["html_a_priori_comment", "title"]
    if act_on_expectations:
        required.append("html_expectations")
    if act_on_contents:
        required.append("html_content")
    if act_on_comments:
        required.append("html_a_posteriori_comment")
    json_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "section",
            "strict": True,
            "schema": 
                {
                "type": "object",
                "properties": {k:v for k,v in fields.items() if k in required},
                "required": required,
                "additionalProperties": False
                }
        }
    }
    return json.dumps(json_schema)

def get_sections_schema(sota : SOTA):
    schema = {
    "type": "json_schema",
    "json_schema": {
      "name": "chapter",
      "strict": True,
      "schema": {
        "type": "object",
        "properties": {
          "sections": {
            "type": "array",
            "description": sota.t('', {'': {
                    'en': 'Sections for this chapter',
                    'fr': 'Sections pour ce chapitre'
                }}),
            "items": {
              "$ref": "#/$defs/section"
            }
          }
        },
        "required": [
          "sections"
        ],
        "additionalProperties": False,
        "$defs": {
          "section": {
            "type": "object",
            "properties": {
              "title": {
                    "type": "string",
                    "description": sota.t('', {'': {
                        'en': 'Section title, deprived of any html formatting.',
                        'fr': 'Titre de la section, dépourvu de tout formatage html.'
                    }})
                },
              "expectations": {
                    "type": "string",
                    "description": sota.t('', {'': {
                        'en': 'Section expectations both in terms of substance and form. This will be used to determine, later, to assess and evaluate the generated section\'s contents\' quality. HTML format as per specified by the HTML Format instructions. This should be VERY detailed.',
                        'fr': 'Attentes de la section à la fois en termes de contenu et de forme. Cela sera utilisé pour déterminer, plus tard, pour évaluer et évaluer la qualité du contenu de la section générée. Format HTML tel que spécifié par les instructions de format HTML. Cela devrait être TRÈS détaillé.'
                    }})
                },
              "contents": {
                    "type": "string",
                    "description": sota.t('', {'': {
                        'en': 'Section contents, formatted as per specified by the HTML format instructions above. Do NOT include either the section title, the expectations nor the comments in there.',
                        'fr': 'Contenu de la section, formaté comme spécifié par les instructions de format HTML ci-dessus. N\'incluez ni le titre de la section, ni les attentes, ni les commentaires.'
                    }})
                }
            },
            "required": [
              "title",
              "expectations",
              "contents"
            ],
            "additionalProperties": False
          }
        }
      }
    }
  }
    return json.dumps(schema)

def get_bibliography_schema(sota: SOTA):
    schema = {
        "type": "json_schema",
        "json_schema": {
        "name": "Answer",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
            "comments": {
                "type": "string",
                "description": sota.t('', {'': {
                    'en': "Any comments you may want to add before generating the bibliography",
                    'fr': "Tous les commentaires que vous souhaitez ajouter avant de générer la bibliographie"
                }})
            },
            "bibliography_title": {
                "type": "string",
                "description": sota.t('', {'': {
                    'en': "Title of the bibliography, no html formatting",
                    'fr': "Titre de la bibliographie, sans formatage html"
                }})
            },
            "html_bibliography": {
                "type": "string",
                "description": sota.t('', {'': {
                    'en': "HTML-Formatted bibliography following the provided guidance, using <ul> and <li> tags. Each item should be a reference to a document, with the title, authors, publication date, and any other relevant information. You can also include comments or notes on each reference. Each reference in the list should start by <li><reference informationid=\"{information id here}\"/>, followed by the formatted reference, and end with </li>.",
                    'fr': "Bibliographie formatée suivant les directives fournies"
                }})
            }
            },
            "required": [
                "comments",
                "bibliography_title",
                "html_bibliography"
            ],
            "additionalProperties": False
        }
        }
    }
    return json.dumps(schema)

def get_instruction(sota : SOTA, 
                    include_references: bool = True, 
                    include_article: bool = True,
                    act_on_title: bool = True,
                    act_on_expectations: bool = False,
                    act_on_comments: bool = False,
                    act_on_contents: bool = False,
                    last_minute_instructions: str = '',
                    mode: Literal['text', 'sections'] = 'text'
                    ):
    logging.debug('Building instructions prompt')
    traductions = {
        'instructions': {
            'en':'Above are, in order%s%s, an example of how sections\' content should be formatted, with allowed html tags, and, finally, the focused section which you will have to work one and/or reflect on. Pay very close attention to the comments in the focused section as well as any last-minute instructions below, as those will indicate you what is expected from you. In your reasoning phase, start by detailing the comments associated with the focused section and further instructions detailed below, then, the sections\' expectations, and, what you should do to best align with those.',
            'fr':'Voici, dans l\'ordre%s%s, un exemple de la façon dont le contenu des sections doit être formaté, avec les balises html autorisées, et, enfin, la section ciblée sur laquelle vous devrez travailler et/ou réfléchir. Prêtez une attention très particulière aux commentaires de la section ciblée, car ils vous fourniront des informations supplémentaires sur ce qui est attendu de vous. Dans votre phase de réflexion, commencez par détailler les commentaires associés à la section ciblée, les attentes des sections et ce que vous devez faire pour vous aligner au mieux sur celles-ci.'
            },
        'text_format': {
            'en': 'In the end, you will be tasked with providing:%s%s%s%s',
            'fr': 'En fin de compte, vous devrez fournir:%s%s%s%s'
        },
        'sections_format':{
            'en': 'In the end, you will be tasked with providing subsections to the focused section/ chapter, with, for each section, its title, expectations, and contents.',
            'fr': 'En fin de compte, vous devrez fournir des sous-sections à la section/chapitre ciblé, avec, pour chaque section, son titre, ses attentes et son contenu.'
        },
        'references': {
            'en': ', the references to use,',
            'fr': ', les références à utiliser,'
        },
        'document': {
            'en': ', the full document at its current version,',
            'fr': ', le document complet à sa version actuelle,'
        },
        'last_minute_instructions': {
            'en': 'Finally (important!):\n %s',
            'fr': 'Enfin (important!):\n %s'
        },
        'new_title': {
            'en': '\n- A new title (no html)',
            'fr': '\n- Un nouveau titre (pas de html)',
        },
        'new_expectations': {
            'en': '\n- A revised version (still html) of the section\'s expectations',
            'fr': '\n- Une version révisée (toujours html) des attentes de la section',
        },
        'new_comments': {
            'en': '\n- A revised version (still html) of the section\'s content',
            'fr': '\n- Une version révisée (toujours html) du contenu de la section',
        },
        'new_comment': {
            'en': '\n- A comment (still html) on the section, providing feedback, hints, etc.',
            'fr': '\n- Un commentaire (toujours html) sur la section, fournissant des retours, des indices, etc.',
        }
    }
    instructions_prompt = ( sota.t('instructions', traductions) % \
            (sota.t('references', traductions) if include_references else '',
            sota.t('document', traductions) if include_article else '') ) \
        + ( sota.t('text_format', traductions) % \
                (sota.t('new_title', traductions) if act_on_title else '',
                sota.t('new_expectations', traductions) if act_on_expectations else '',
                sota.t('new_comment', traductions) if act_on_contents else '',
                sota.t('new_comments', traductions) if act_on_comments else '') \
            if mode == 'text' \
            else \
                sota.t('sections_format', traductions)) \
        + (sota.t('last_minute_instructions', traductions) % (last_minute_instructions if last_minute_instructions else ''))
    return instructions_prompt

def complex_rewrite(
    sota : SOTA, 
    information_id: int,
    include_references: bool = True,
    include_article: bool = True,
    act_on_title: bool = False,
    act_on_expectations: bool = False,
    act_on_comments: bool = False,
    act_on_contents: bool = False,
    last_minute_instructions: str = '',
    references_mode: Literal['allow', 'restrict', 'free'] = 'allow',
    mode: Literal['text', 'sections'] = 'text'
    ):
    logging.debug(f'Starting complex rewrite')
    traductions = {
        'references': {
            'en': '============================== References ==============================\n\n',
            'fr': '============================== Références ==============================\n\n'
        },
        'document': {
            'en': '\n\n============================== Full Document, current version ==============================\n\n',
            'fr': '\n\n============================== Document complet, version actuelle ==============================\n\n'
        },
        'format': {
            'en': '\n\n============================== HTML Format for Sections\' content ==============================\n\n',
            'fr': '\n\n============================== Format HTML pour le contenu des sections ==============================\n\n'
        },
        'focused': {
            'en': '\n\n============================== Focused Section ==============================\n\n',
            'fr': '\n\n============================== Section ciblée sur laquelle travailler ==============================\n\n'
        },
        'instructions': {
            'en': '\n\n============================== Instructions ==============================\n\n',
            'fr': '\n\n============================== Instructions ==============================\n\n'
        }
    }
    references, article, focus, format_prompt = '', '', '', ''
    # 1. Building the references is the hard part
    if include_references:
        references = build_references(sota, information_id, references_mode)
        references_header = sota.t('references', traductions)
        references = f"{references_header}{references}"
    # 2. Building the article is the medium hard
    if include_article:
        article = sota.build_text(focused_information_id=information_id)
        article_header = sota.t('document', traductions)
        article = f"{article_header}{article}"
    # 3. The prompt
    if act_on_comments or act_on_contents or act_on_expectations or mode == 'sections':
        format_prompt = get_html_format(sota)
        format_header = sota.t('format', traductions)
        format_prompt = f"{format_header}{format_prompt}"
    # 4. The focused section, basically the same as the article, but only the focused section
    if include_article:
        focus = ''.join([_ for _ in article.splitlines(True) if _.startswith('>>>')])
    else:
        focus = sota.build_text(information_id=information_id)
    focus_header = sota.t('focused', traductions)
    focus = f"{focus_header}{focus}"
    # 5. The instructions
    instructions = get_instruction(sota, include_article=include_article, include_references=include_references, act_on_comments=act_on_comments, act_on_contents=act_on_contents, act_on_expectations=act_on_expectations, last_minute_instructions=last_minute_instructions, mode=mode)
    instructions_header = sota.t('instructions', traductions)
    instructions = f"{instructions_header}{instructions}"
    # 6. The final prompt for the LLM
    final_prompt = f"{references}{article}{format_prompt}{focus}{instructions}"
    # 7. Send that to the LLM
    prompt = PROMPT()
    prompt.add(final_prompt, role='user')
    result = LLMS_v2(
        get_json_schema(sota, act_on_expectations = act_on_expectations, act_on_comments = act_on_comments, act_on_contents = act_on_contents) if mode == 'text' else get_sections_schema(sota),
        model="o3-mini-2025-01-31")(prompt)
    # 8. Return the result, wrapped in a dictionary
    result = {
        'information_id': information_id,
        'contents': result,
        'action': mode,
        'params': {
            'act_on_title': act_on_title,
            'act_on_expectations': act_on_expectations,
            'act_on_comments': act_on_comments,
            'act_on_contents': act_on_contents,
            'references_mode': references_mode
        }
    }
    return result

# Pipelines for text sections

def rewrite(sota : SOTA, 
            information_id: int,
            references_mode: Literal['allow', 'restrict', 'free'] = 'allow',
            additional_instructions: str = '',
            final_comment: bool = True
            ) -> dict:
    logging.debug(f'Starting rewrite')
    return complex_rewrite(sota, information_id, act_on_title=True, act_on_comments=True, act_on_contents=final_comment, last_minute_instructions=additional_instructions, references_mode=references_mode)

def brush(sota: SOTA, 
          information_id: int,
          brush_mode: Literal['academic', 'research', 'technical', 'informative', 'analytical', 'explanatory', 'summarize', 'evaluative', 'critical', 'neutral']
          ) -> dict:
    logging.debug(f'Starting brush')
    traductions = {
        'academic': {
            'en': (
                "Please rewrite this section in a more academic style. "
                "Ensure that all core content, references, and citations remain unchanged."
            ),
            'fr': (
                "Veuillez réécrire cette section dans un style plus académique. "
                "Assurez-vous que le contenu principal, les références et les citations restent inchangés."
            )
        },
        'research': {
            'en': (
                "Please rewrite this section with a focus on research methodology and data analysis. "
                "Retain all core content, references, and citations exactly as provided."
            ),
            'fr': (
                "Veuillez réécrire cette section en mettant l'accent sur la méthodologie de recherche et l'analyse des données. "
                "Conservez l'intégralité du contenu, y compris les références et citations, sans modification."
            )
        },
        'technical': {
            'en': (
                "Please rewrite this section in a technical style, ensuring that all technical details, "
                "specifications, and references remain intact."
            ),
            'fr': (
                "Veuillez réécrire cette section dans un style technique, en veillant à ce que tous les détails techniques, "
                "les spécifications et les références restent inchangés."
            )
        },
        'informative': {
            'en': (
                "Please rewrite this section in an informative style, highlighting key details and facts without altering "
                "the core message or any references."
            ),
            'fr': (
                "Veuillez réécrire cette section dans un style informatif, en mettant en lumière les détails et faits clés sans altérer "
                "le message principal ni modifier les références."
            )
        },
        'analytical': {
            'en': (
                "Please rewrite this section in an analytical style, breaking down the information and providing deeper insights "
                "while preserving the original content and all references."
            ),
            'fr': (
                "Veuillez réécrire cette section dans un style analytique, en décomposant les informations et en fournissant des analyses approfondies "
                "tout en préservant le contenu original et toutes les références."
            )
        },
        'explanatory': {
            'en': (
                "Please rewrite this section in an explanatory style, clarifying complex ideas and processes without changing "
                "the essential content or any references."
            ),
            'fr': (
                "Veuillez réécrire cette section dans un style explicatif, en clarifiant les idées complexes et les processus sans modifier "
                "le contenu essentiel ni altérer les références."
            )
        },
        'summarize': {
            'en': (
                "Please rewrite this section to create a concise summary, capturing the main points while retaining the essential details "
                "and preserving all references."
            ),
            'fr': (
                "Veuillez réécrire cette section pour créer un résumé concis, en capturant les points principaux tout en conservant les détails essentiels "
                "et en préservant toutes les références."
            )
        },
        'evaluative': {
            'en': (
                "Please rewrite this section in an evaluative style, offering a balanced critique of the content while preserving all key information "
                "and references."
            ),
            'fr': (
                "Veuillez réécrire cette section dans un style évaluatif, en offrant une critique équilibrée du contenu tout en conservant toutes les informations clés "
                "et les références."
            )
        },
        'critical': {
            'en': (
                "Please rewrite this section in a critical style, challenging assumptions and providing a thoughtful critique without altering "
                "the factual content or any references."
            ),
            'fr': (
                "Veuillez réécrire cette section dans un style critique, en remettant en question les hypothèses et en fournissant une critique réfléchie "
                "sans altérer le contenu factuel ni modifier les références."
            )
        },
        'neutral': {
            'en': (
                "Please rewrite this section in a neutral style, presenting the information in an objective and unbiased manner while preserving "
                "all references."
            ),
            'fr': (
                "Veuillez réécrire cette section dans un style neutre, en présentant les informations de manière objective et impartiale tout en préservant "
                "toutes les références."
            )
        }
    }
    last_minute_instructions = sota.t(brush_mode, traductions)
    return complex_rewrite(sota, information_id, include_references=False, act_on_contents=True, last_minute_instructions=last_minute_instructions)

def translate(
    sota : SOTA, 
    information_id: int,
    langage: Literal['en', 'fr']
    ) -> dict:
    logging.debug(f'Starting translation')
    langage_cache = sota.configuration.language
    sota.configuration.language = langage
    last_minute_instructions = sota.t('', {'': {
        'en': 'Please translate this section in English. Make sure to preserve styling and references. If it is already in English, then just copy it verbatim without the slightest change.',
        'fr': 'Veuillez traduire cette section en français. Assurez-vous de préserver le style et les références. Si le texte est déjà en français, copiez-le tel quel sans le moindre changement.'
    }})
    result = complex_rewrite(sota, information_id, include_article=False, include_references=False, act_on_title=True, act_on_contents=True, last_minute_instructions=last_minute_instructions)
    sota.configuration.language = langage_cache
    return result

def make_longer(
    sota : SOTA, 
    information_id: int,
    ) -> dict:
    logging.debug(f'Starting make_longer')
    last_minute_instructions = sota.t('', {'': {
        'en': 'Please make this section longer. You can add more details, examples, explanations, or any relevant information to expand the content. Ensure that the additional content aligns with the existing text and references.',
        'fr': 'Veuillez allonger cette section. Vous pouvez ajouter plus de détails, d\'exemples, d\'explications ou toute information pertinente pour étendre le contenu. Assurez-vous que le contenu supplémentaire est en accord avec le texte et les références existants.'
    }})
    return complex_rewrite(sota, information_id, act_on_contents=True, last_minute_instructions=last_minute_instructions, references_mode='restrict')
    
def make_shorter(
    sota : SOTA, 
    information_id: int,
    ) -> dict:
    logging.debug(f'Starting make_shorter')
    last_minute_instructions = sota.t('', {'': {
        'en': 'Please make this section shorter. You can remove redundant information, unnecessary details, or any content that does not directly contribute to the main message. Ensure that the shortened version maintains clarity and coherence.',
        'fr': 'Veuillez raccourcir cette section. Vous pouvez supprimer les informations redondantes, les détails inutiles ou tout contenu qui ne contribue pas directement au message principal. Assurez-vous que la version raccourcie conserve la clarté et la cohérence.'
    }})
    return complex_rewrite(sota, information_id, act_on_contents=True, last_minute_instructions=last_minute_instructions, references_mode='restrict')

def rewrite_expectations(
    sota : SOTA, 
    information_id: int,
    additional_instructions: str = '',
    ) -> dict:
    logging.debug(f'Starting rewrite_expectations')
    return complex_rewrite(sota, information_id, act_on_expectations=True, last_minute_instructions=additional_instructions, references_mode='free')

def provide_feedback(
    sota : SOTA, 
    information_id: int,
    additional_instructions: str = '',
    ) -> dict:
    logging.debug(f'Starting provide_feedback')
    return complex_rewrite(sota, information_id, act_on_comments=True, last_minute_instructions=additional_instructions, references_mode='allow')

text_pipelines = {
    'rewrite': rewrite,
    'brush': brush,
    'translate': translate,
    'make_longer': make_longer,
    'make_shorter': make_shorter,
    'rewrite_expectations': rewrite_expectations,
    'provide_feedback': provide_feedback
}

# Pipelines for sections

def rebuild_sections(
    sota: SOTA,
    information_id: int,
    additional_instructions: str = ''
    ) -> dict:
    logging.debug(f'Starting rebuild_sections')
    return complex_rewrite(sota, information_id, last_minute_instructions=additional_instructions, mode='sections')

def sections_references(
    sota: SOTA,
    information_id: int,
    references_mode: Literal['allow', 'restrict', 'free'] = 'allow'
    ) -> dict:
    if references_mode == 'allow':
        allow_external, force_keep_documents, force_keep_chunks = True, True, True
    elif references_mode == 'restrict':
        allow_external, force_keep_documents, force_keep_chunks = False, True, True
    elif references_mode == 'free':
        allow_external, force_keep_documents, force_keep_chunks = True, False, True
    res = sota.build_references(information_id=information_id, allow_external=allow_external, force_keep_documents=force_keep_documents, force_keep_chunks=force_keep_chunks)
    return {
        'information_id': information_id,
        'contents': [
            {'reference_id':_['referenced_information'], 'information_id': __, 'chunk_id': _['chunk_id']}
            for _ in res for __ in _['assigned_to']
            ],
        'action': 'add_references',
        'params': {
            'references_mode': references_mode
        }
    }

def write_bibliography(
    sota: SOTA,
    information_id: int,
    bibliography_format: Literal['apa', 'mla', 'chicago', 'harvard', 'ieee', 'vancouver'] = 'apa',
    additional_instructions: str = ''
    ) -> dict:
    references = extract_references(sota.build_text(information_id=information_id))
    reference_ids = list(set([_['informationid'] for _ in references]))
    reference_ids.sort()
    references = [sota.information[_] for _ in reference_ids]
    versions_list = sota.versions_list(-1)
    references = [_ for _ in references if VersionedInformation.get_class_name(_.get_last_version(versions_list)) == 'External']
    lucario = LUCARIO(url=sota.drop_url, project_id=sota.file_id, elements={}, uuid_2_position={})
    for _information_id,r in zip(reference_ids, references):
        _last = r.get_last_version(versions_list)
        assert _last.external_db == 'lucario', f'External reference {r.id} is not from Lucario, unimplemented'
        lucario.elements[_information_id] = Document.get_empty()
        lucario.elements[_information_id].file_uuid = _last.external_id
        lucario.uuid_2_position[_last.external_id] = _information_id
    lucario.update()
    def jsonloads(text):
        try:
            return json.loads(text)
        except:
            return text
    prompt = PROMPT()
    prompt.add(
        json.dumps({f'reference_id: {k} (cite as <li><reference referenceid="{k}"/>....</li>)':jsonloads(v.description) for k,v in lucario.elements.items()}, indent=4), 
        role='user')
    html_format = get_html_format(sota)
    prompt.add(
               sota.t('', {'': {
                   'en': 'The bibliography you will write has to be in the specified format:\n%s\n\n Please refer to the instructions below for additional guidance.',
                     'fr': 'La bibliographie que vous allez rédiger doit être dans le format spécifié:\n%s\n\n Veuillez vous référer aux instructions ci-dessous pour des conseils supplémentaires.'
                }}) % html_format
               , role='user')
    prompt.add(
               sota.t('', {'': {
                    'en': 'Please write the bibliography for the provided references in the specified format. The dictionary keys are the reference IDs you should use in the bibliography, and the values are the reference details. Format to use: %s. \n%s',
                    'fr': 'Veuillez rédiger la bibliographie pour les références fournies dans le format spécifié. Les clés du dictionnaire sont les identifiants des références que vous devez utiliser dans la bibliographie, et les valeurs sont les détails des références. Format à utiliser: %s. \n%s'
                }}
               ) % (bibliography_format, additional_instructions)
               , role='user')
    pipeline = LLMS_v2(get_bibliography_schema(sota), model="o3-mini-2025-01-31")
    result = pipeline(prompt)
    return {
        'information_id': information_id,
        'contents': result,
        'action': 'bibliography',
        'params': {
            'bibliography_format': bibliography_format
        }
    }

sections_pipelines = {
    'sections_rewrite_expectations': rewrite_expectations,
    'rebuild_sections': rebuild_sections,
    'sections_feedback': provide_feedback,
    'sections_references': sections_references,
    'write_bibliography': write_bibliography
}

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self):
        pass
    def __call__(self, 
            sota : SOTA,
            task : dict
            ) -> dict:
        logging.debug(f'Calling pipeline with task {task}')
        information = sota.information[task.get('information_id')]
        last_version_class_name = VersionedInformation.get_class_name(information.get_last_version(sota.versions_list(-1)))
        name = task.pop('name')
        if last_version_class_name == 'str':
            assert name in text_pipelines, f'Pipeline {name} not found for text sections'
            pipeline = text_pipelines[name]
        else:
            assert last_version_class_name == 'Sections', f'Pipeline {name} not found for sections'
            assert name in sections_pipelines, f'Pipeline {name} not found for sections'
            pipeline = sections_pipelines[name]
        return pipeline(**{**task['params'], 'sota': sota, 'information_id': task['information_id']}) 