from custom_types.SOTA.type import SOTA, VersionedInformation, extract_references
from custom_types.JSONL.type import JSONL
from custom_types.PROMPT.type import PROMPT
from custom_types.LUCARIO.type import LUCARIO, Document
from pipelines.CONVERSIONS.JSONL.to_txt import Pipeline as JSONL2Txt
from pipelines.LLMS_v2.json_dict_output import Pipeline as LLMS_v2
import json
from typing import Literal, List
from openai import OpenAI
import logging
from datetime import datetime

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
                'en': '<!-- chunk from informationid="{referenced_information}" with position="{chunk_id}" -->\n{text}\n<!-- end of chunk positioned position="{chunk_id}" -->',
                'fr': '<reference informationid="{referenced_information}" position="{chunk_id}">\n{text}\n</reference>'
            }}),
        sort_by='position',
        joiner=sota.t('', {'': {
                'en': '\n\n\n====================== NEW DOCUMENT ============================\n\n\n',
                'fr': '\n\n\n====================== NOUVEAU DOCUMENT ============================\n\n\n'
            }}),
        grouped=True,
        group_by='referenced_information',
        group_format=sota.t('', {'': {
                'en': '# Reference {referenced_information}\n>> To cite this article, the "information_id" in the referencement is: information_id = {referenced_information}\n>> Context for this document: {reference}',
                'fr': '# Référence {referenced_information}\n>> Pour citer cet article, l\'"information_id" dans le referencement est: information_id = {referenced_information}\n>> Contexte pour ce document: {reference}'
            }}),
        group_joiner='?\n\n...\n\n'
    )
    text = to_txt_pipe(res)
    return text

def get_html_format(sota : SOTA):
    logging.debug('Building HTML format prompt')
    format_prompt = {"format": {
        "en": "# HTML Formatting and Special Tags Guidelines\n\n## Allowed Classic HTML Tags\n\nOnly the following tags are permitted - all others are forbidden:\n\n### Text Formatting\n- Headings: `<h4>Heading</h4>`\n- Paragraphs: `<p>Paragraph text</p>`\n- Bold: `<strong>Bold text</strong>`\n- Italic: `<em>Italic text</em>`\n- Strikethrough: `<s>Strikethrough text</s>`\n- Superscript: `<sup>Superscript</sup>`\n- Subscript: `<sub>Subscript</sub>`\n\n### Lists\n- Ordered lists: \n  ```html\n  <ol>\n      <li>First item</li>\n      <li>Second item</li>\n  </ol>\n  ```\n- Unordered lists:\n  ```html\n  <ul>\n      <li>Bullet point</li>\n      <li>Another bullet point</li>\n  </ul>\n  ```\n\n### Styling and Layout\n- Styling: `<span style=\"font-family: Arial\">Arial font</span>` or `<span style=\"color: #d0021b\">Red text</span>`\n- Highlight: `<mark data-color=\"#d0021b\" style=\"background-color: #d0021b; color: inherit\">Red background</mark>`\n- Alignment: `<p style=\"text-align: center\">Centered text</p>`\n- Tables: \n  ```html\n  <table style=\"min-width: 409px\">\n      <colgroup>\n          <col style=\"width: 313px\">\n          <col style=\"width: 71px\">\n          <col style=\"min-width: 25px\">\n      </colgroup>\n      <tbody>\n          <tr>\n              <th colspan=\"1\" rowspan=\"1\" colwidth=\"313\">\n                  <p>Example table</p>\n              </th>\n              <th colspan=\"1\" rowspan=\"1\" colwidth=\"71\">\n                  <p>Narrow<br>Column</p>\n              </th>\n              <th colspan=\"1\" rowspan=\"1\">\n                  <p>Example image in table</p>\n                  <img src=\"https://example.com/image.jpg\" style=\"width: 100%; height: auto;\">\n              </th>\n          </tr>\n          <tr>\n              <td colspan=\"2\" rowspan=\"1\" colwidth=\"313,71\">\n                  <p>Two cells merged horizontally</p>\n              </td>\n              <td colspan=\"1\" rowspan=\"2\">\n                  <p>Two cells merged vertically</p>\n              </td>\n          </tr>\n      </tbody>\n  </table>\n  ```\n- Blockquote: `<blockquote><p>Quoted text</p></blockquote>`\n- Code blocks: \n  ```html\n  <pre><code class=\"language-javascript\">Code content</code></pre>\n  ```\n- Images: `<img src=\"https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg\" style=\"width: 100%; height: auto; cursor: pointer;\" draggable=\"true\">` Try not to delete image if there are some.\n\n## Special Tags - CRITICAL RULES\n\n### References\n```html\n<reference refid=\"1234\"></reference>\n```\n- **NEVER REMOVE** these tags except if specifically asked or strongly relevant.\n- Linked to external verification database\n- Essential for fact-checking and information tracking\n\n### Comments\n```html\n<comment comment-id=\"1234\">content</comment>\n```\n- **PRESERVE THE TAGS** while content inside may be modified\n- Each has a unique 4-digit ID linked to database\n- When adding new comments, use unused 4-digit IDs\n- Will be removed in final export\n- In the html itself (html_content), ONLY the <comment comment-id=\"xx\">...</comment> should appear: the contents of the comment should SYSTEMATICALLY be speficied separately, in the field provided for that purpose (comments).\n- If wou created a new comment, MAKE SURE IT APPEARS SOMEWHERE!!!\n\n### Inline Comments\n```html\n<mention time=\"...\" author=\"...\">content</mention> Mention\' contents are meant to be 5-6 words MAXIMUM. \n```\n- Used for lightweight annotations\n- Will be removed in final export\n\n### Locked Content\n```html\n<lock>content</lock>\n```\n- **ABSOLUTELY DO NOT MODIFY** anything inside these tags\n- **PRESERVE THE TAGS** exactly as they appear\n- Indicates content that must remain unchanged\n- Will be removed in final export\n\nRemember:\n1. Only use tags explicitly listed above\n2. Preserve all special tags unless explicitly stated otherwise\n3. Pay special attention to locked content and references\n4. Modify content only where permitted",
        "fr": "Voici la traduction en fran\u00e7ais des directives de formatage HTML et des balises sp\u00e9ciales :\n\n**# Directives de formatage HTML et balises sp\u00e9ciales**\n**## Balises HTML classiques autoris\u00e9es**\nSeules les balises suivantes sont autoris\u00e9es - toutes les autres sont interdites :\n**### Formatage de texte**\n- Titres : `<h4>Titre</h4>`\n- Paragraphes : `<p>Texte du paragraphe</p>`\n- Gras : `<strong>Texte en gras</strong>`\n- Italique : `<em>Texte en italique</em>`\n- Barr\u00e9 : `<s>Texte barr\u00e9</s>`\n- Exposant : `<sup>Exposant</sup>`\n- Indice : `<sub>Indice</sub>`\n**### Listes**\n- Listes ordonn\u00e9es :\n  ```html\n  <ol>\n      <li>Premier \u00e9l\u00e9ment</li>\n      <li>Deuxi\u00e8me \u00e9l\u00e9ment</li>\n  </ol>\n  ```\n- Listes non ordonn\u00e9es :\n  ```html\n  <ul>\n      <li>Point \u00e0 puces</li>\n      <li>Autre point \u00e0 puces</li>\n  </ul>\n  ```\n**### Style et mise en page**\n- Style : `<span style=\"font-family: Arial\">Police Arial</span>` ou `<span style=\"color: #d0021b\">Texte rouge</span>`\n- Surlignement : `<mark data-color=\"#d0021b\" style=\"background-color: #d0021b; color: inherit\">Fond rouge</mark>`\n- Alignement : `<p style=\"text-align: center\">Texte centr\u00e9</p>`\n- Tableaux :\n  ```html\n  <table style=\"min-width: 409px\">\n      <colgroup>\n          <col style=\"width: 313px\">\n          <col style=\"width: 71px\">\n          <col style=\"min-width: 25px\">\n      </colgroup>\n      <tbody>\n          <tr>\n              <th colspan=\"1\" rowspan=\"1\" colwidth=\"313\">\n                  <p>Exemple de tableau</p>\n              </th>\n              <th colspan=\"1\" rowspan=\"1\" colwidth=\"71\">\n                  <p>Colonne<br>\u00e9troite</p>\n              </th>\n              <th colspan=\"1\" rowspan=\"1\">\n                  <p>Exemple d'image dans un tableau</p>\n                  <img src=\"https://example.com/image.jpg\" style=\"width: 100%; height: auto;\">\n              </th>\n          </tr>\n          <tr>\n              <td colspan=\"2\" rowspan=\"1\" colwidth=\"313,71\">\n                  <p>Deux cellules fusionn\u00e9es horizontalement</p>\n              </td>\n              <td colspan=\"1\" rowspan=\"2\">\n                  <p>Deux cellules fusionn\u00e9es verticalement</p>\n              </td>\n          </tr>\n      </tbody>\n  </table>\n  ```\n- Citation : `<blockquote><p>Texte cit\u00e9</p></blockquote>`\n- Blocs de code :\n  ```html\n  <pre><code class=\"language-javascript\">Contenu du code</code></pre>\n  ```\n- Images : `<img src=\"https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg\" style=\"width: 100%; height: auto; cursor: pointer;\" draggable=\"true\">` Essayez de ne pas supprimer l'image s'il y en a.\n**## Balises sp\u00e9ciales - R\u00c8GLES CRITIQUES**\n**### R\u00e9f\u00e9rences**\n```html\n<reference refid=\"1234\"></reference>\n```\n- **NE JAMAIS SUPPRIMER** ces balises sauf si sp\u00e9cifiquement demand\u00e9 ou fortement pertinent.\n- Li\u00e9es \u00e0 une base de donn\u00e9es de v\u00e9rification externe\n- Essentielles pour la v\u00e9rification des faits et le suivi des informations\n**### Commentaires**\n```html\n<comment comment-id=\"1234\">contenu</comment>\n```\n- **PR\u00c9SERVER LES BALISES** tandis que le contenu \u00e0 l'int\u00e9rieur peut \u00eatre modifi\u00e9\n- Chacun poss\u00e8de un identifiant unique \u00e0 4 chiffres li\u00e9 \u00e0 la base de donn\u00e9es\n- Lors de l'ajout de nouveaux commentaires, utilisez des identifiants \u00e0 4 chiffres non utilis\u00e9s\n- Seront supprim\u00e9s dans l'exportation finale\n- Dans le contenu principal (html_content), SEULE la balise <comment comment-id=\"xx\">...</comment> doit appara\u00eetre. Le contenu m\u00eame du commentaire doit quand \u00e0 lui \u00eatre fourni/ \u00e9dit\u00e9 dans le champs json fourni \u00e0 cet effet (comments).\n- Si tu as cr\u00e9\u00e9 un nouveau commentaire, ASSURE TOI DE L'INTEGRER QUELQUEPART!!!\n\n**### Commentaires en ligne**\n```html\n<mention time=\"...\" author=\"...\">contenu</mention> Le contenu des mentions de doit jamais dépasser 5 ou 6 mots!!!\n```\n- Utilis\u00e9s pour les annotations l\u00e9g\u00e8res\n- Seront supprim\u00e9s dans l'exportation finale\n**### Contenu verrouill\u00e9**\n```html\n<lock>contenu</lock>\n```\n- **NE MODIFIEZ ABSOLUMENT PAS** ce qui se trouve \u00e0 l'int\u00e9rieur de ces balises\n- **PR\u00c9SERVEZ LES BALISES** exactement comme elles apparaissent\n- Indique un contenu qui doit rester inchang\u00e9\n- Seront supprim\u00e9es dans l'exportation finale\nN'oubliez pas :\n1. Utilisez uniquement les balises explicitement list\u00e9es ci-dessus\n2. Pr\u00e9servez toutes les balises sp\u00e9ciales sauf indication contraire explicite\n3. Portez une attention particuli\u00e8re au contenu verrouill\u00e9 et aux r\u00e9f\u00e9rences\n4. Modifiez le contenu uniquement l\u00e0 o\u00f9 c'est autoris\u00e9"
    }}
    return sota.t('format', format_prompt)
    
def get_json_schema(sota : SOTA,
                    free_ref_ids: List[int],
                    existing_ref_ids: List[int],
                    act_on_title: bool = True,
                    act_on_expectations: bool = False,
                    act_on_comments: bool = False,
                    act_on_contents: bool = False):
    logging.debug('Building JSON schema')
    free_refs = ', '.join([f'{_}' for _ in free_ref_ids])
    existing_refs = ', '.join([f'{_}' for _ in existing_ref_ids])
    
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
        'en': f'Section contents, formatted as per specified by the HTML format instructions above. Do NOT re-include either the section title, the expectations nor the comments in there. I repeat. Do NOT repeat the title here, the machine will parse it from the "title" field. If you put it here too, it will appear twice. Allowed refids are: {existing_refs}, and the ids from {free_refs} which you decided to use in the \'referencements\' field. OTHER refid ids are NOT allowed.',
        'fr': f'Contenu de la section, formaté comme spécifié par les instructions de format HTML ci-dessus. N\'incluez ni le titre de la section, ni les attentes, ni les commentaires. Je répète. Ne répétez pas le titre ici, la machine le parsèmera du champ "titre". Si vous le mettez ici aussi, il apparaîtra deux fois. Les identifiants de référence autorisés sont : {existing_refs}, et les identifiants de {free_refs} que vous avez décidé d\'utiliser dans le champ \'références\'. D\'AUTRES identifiants refid ne sont PAS autorisés.'
        }})
    html_a_posteriori_comment = sota.t('', {'': {
        'en': 'If you want to add a last a-posteriori comment, a feedback, hints at how to enhance this section or whatever, do it here, in html too, same as html_contents. You may also refer to references here, put bullet points, text formatting, etc. Basically the same as html_content.',
        'fr': 'Si vous souhaitez ajouter un dernier commentaire a-posteriori, un retour, des indices sur la manière d\'améliorer cette section ou autre, faites-le ici, en html également, de la même manière que html_contents. Vous pouvez également faire référence aux références ici, mettre des puces, formater le texte, etc. Fondamentalement la même chose que html_content.'
        }})
    comments_description = sota.t('', {'': {
        'en': 'Comments you want to create or edit. Each comment SHOULD be linked to an in-text <comment> tag. When editing a previously existing comment, re-write previous contents of the contents, otherwise it will be lost, and then append to it. If you ought to modify the contents based - even slightly - on a comment, please answer to it, appending an answer to the SAME comment. You may of course (and it will have a very positive impact on your grade) create a new comment to provide feedback, hints, etc. to the human.',
        'fr': 'Commentaires que vous souhaitez créer ou modifier. Chaque commentaire DOIT être lié à une balise <comment> dans le texte. Lorsque vous modifiez un commentaire précédemment existant, réécrivez le contenu précédent, sinon il sera perdu, puis ajoutez-y. Si vous devez modifier le contenu en fonction d\'un commentaire - même légèrement - veuillez y répondre, en ajoutant une réponse au MÊME commentaire. Vous pouvez bien sûr (et cela aura un impact très positif sur votre note) créer un nouveau commentaire pour fournir des retours, des indices, etc. à l\'humain.'
        }})
    comment_id_description = sota.t('', {'': {
        'en': '4-digit yet-existing or newly-created comment ID',
        'fr': 'Identifiant de commentaire à 4 chiffres existant ou nouvellement créé'
        }})
    comment_html_description = sota.t('', {'': {
        'en': 'HTML-formatted comment. If you edit an existing version, make sure to JUST append to the previous contents, starting with <mention time="%s" author="IA">AI</mention> and then your comment Mentions\' contents are meant to be 5-6 words MAXIMUM. Failure to put this mention will lead to refusal of your answer and to your elimination.'  % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'fr': 'Commentaire formaté en HTML. Si vous modifiez une version existante, assurez-vous de JUSTE ajouter au contenu précédent, en commençant par <mention time="%s" author="IA">IA</mention> puis votre commentaire. Le contenu des mentions ne doit JAMAIS dépasser 5 ou 6 mots.. Le fait de ne pas mettre cette mention entraînera le refus de votre réponse et votre élimination.' % datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }})
    fields = {
                "thoughts_and_reflection": {
                    "type": "object",
                    "description": sota.t('', {'': {
                        'en': 'Analyze the provided content and task using the ADDIE methodology (Analysis, Design, Development, Implementation, Evaluation) - a scientifically proven framework widely used in instructional design and content development. Each phase should be thoroughly explored with at least one detailed paragraph per phase. The comprehensive approach ensures systematic improvement of content through evidence-based methods.',
                        'fr': 'Analysez le contenu et la tâche fournis en utilisant la méthodologie ADDIE (Analyse, Conception, Développement, Implémentation, Évaluation) - un cadre scientifiquement prouvé largement utilisé dans la conception pédagogique et le développement de contenu. Chaque phase doit être explorée en profondeur avec au moins un paragraphe détaillé par phase. Cette approche globale assure une amélioration systématique du contenu grâce à des méthodes fondées sur des preuves.'
                    }}),
                    "properties": {
                        "analysis_phase": {
                            "type": "string",
                            "description": sota.t('', {'': {
                                'en': "Phase 1 - Analysis: Comprehensive assessment of the current document state, examining both explicit and implicit elements. Analyze the section's purpose, target audience, and requirements. Evaluate how the current content aligns with stated expectations. Identify gaps, redundancies, inconsistencies, and contextual issues within the broader document. Assess clarity, completeness, and logical flow. Consider any constraints or special requirements indicated by comments or locked sections. This foundational analysis should be evidence-based and objective, with at least 5 detailed observations.",
                                'fr': "Phase 1 - Analyse: Évaluation complète de l'état actuel du document, examinant les éléments explicites et implicites. Analysez l'objectif de la section, le public cible et les exigences. Évaluez comment le contenu actuel s'aligne sur les attentes énoncées. Identifiez les lacunes, redondances, incohérences et problèmes contextuels dans l'ensemble du document. Évaluez la clarté, l'exhaustivité et le flux logique. Tenez compte de toutes contraintes ou exigences spéciales indiquées par les commentaires ou sections verrouillées. Cette analyse fondamentale doit être objective et factuelle, avec au moins 5 observations détaillées."
                            }}),
                        },
                        "design_phase": {
                            "type": "string",
                            "description": sota.t('', {'': {
                                'en': "Phase 2 - Design: Strategic planning based on the analysis findings. Outline the conceptual framework for improvements, including overall structure, logical flow, and content hierarchy. Define specific improvement objectives addressing each issue identified in the analysis phase. Determine what content should be preserved, modified, added, or removed. Create a coherent vision for how the revised content will better fulfill expectations and integrate with the broader document. Consider multiple design approaches and justify your selected strategy. This phase requires at least 5 detailed design decisions with supporting rationales.",
                                'fr': "Phase 2 - Conception: Planification stratégique basée sur les résultats de l'analyse. Esquissez le cadre conceptuel des améliorations, y compris la structure globale, le flux logique et la hiérarchie du contenu. Définissez des objectifs d'amélioration spécifiques pour chaque problème identifié dans la phase d'analyse. Déterminez quel contenu doit être préservé, modifié, ajouté ou supprimé. Créez une vision cohérente de la façon dont le contenu révisé répondra mieux aux attentes et s'intégrera au document plus large. Envisagez plusieurs approches de conception et justifiez votre stratégie sélectionnée. Cette phase nécessite au moins 5 décisions de conception détaillées avec des justifications."
                            }}),
                        },
                        "development_phase": {
                            "type": "string",
                            "description": sota.t('', {'': {
                                'en': "Phase 3 - Development: Detailed planning of specific content changes based on the design framework. Plan precise modifications to text, structure, and formatting. Identify specific references to add or modify, using appropriate 4-digit IDs. Formulate responses to existing comments and plan new comments where beneficial. Ensure all planned elements conform to required HTML formatting standards. Detail how locked content will be preserved while integrating surrounding improvements. Create a systematic approach to implementing each specific change. This phase requires at least 5 detailed development specifications.",
                                'fr': "Phase 3 - Développement: Planification détaillée des modifications spécifiques du contenu basées sur le cadre de conception. Planifiez des modifications précises du texte, de la structure et du formatage. Identifiez les références spécifiques à ajouter ou à modifier, en utilisant des identifiants à 4 chiffres appropriés. Formulez des réponses aux commentaires existants et planifiez de nouveaux commentaires si nécessaire. Assurez-vous que tous les éléments planifiés sont conformes aux normes de formatage HTML requises. Détaillez comment le contenu verrouillé sera préservé tout en intégrant les améliorations environnantes. Créez une approche systématique pour mettre en œuvre chaque changement spécifique. Cette phase nécessite au moins 5 spécifications de développement détaillées."
                            }}),
                        },
                        "implementation_strategy": {
                            "type": "string",
                            "description": sota.t('', {'': {
                                'en': "Phase 4 - Implementation Strategy: Concrete execution plan for applying all designed changes. Create a sequenced approach to implementation, considering dependencies between changes. Address potential challenges and mitigation strategies. Detail how to maintain document integrity throughout the implementation process. Ensure all special formatting requirements and tags will be preserved or properly implemented. Explain how you'll validate each change against the original requirements. Create contingency plans for complex modifications. This critical phase requires at least 5 detailed implementation steps with clear sequencing.",
                                'fr': "Phase 4 - Stratégie d'implémentation: Plan d'exécution concret pour appliquer tous les changements conçus. Créez une approche séquencée pour l'implémentation, en tenant compte des dépendances entre les changements. Abordez les défis potentiels et proposez des stratégies d'atténuation. Détaillez comment maintenir l'intégrité du document tout au long du processus d'implémentation. Assurez-vous que toutes les exigences de formatage spécial et les balises seront préservées ou correctement implémentées. Expliquez comment vous validerez chaque changement par rapport aux exigences originales. Créez des plans de contingence pour les modifications complexes. Cette phase critique nécessite au moins 5 étapes d'implémentation détaillées avec un séquençage clair."
                            }}),
                        },
                        "evaluation_framework": {
                            "type": "string",
                            "description": sota.t('', {'': {
                                'en': "Phase 5 - Evaluation Framework: Comprehensive assessment metrics to ensure the effectiveness of planned changes. Define specific criteria for evaluating each aspect of the improved content. Establish quality benchmarks for clarity, completeness, accuracy, and alignment with expectations. Create a systematic approach to verify that all identified issues have been properly addressed. Develop methods to assess how well the revised content integrates with the broader document. Include both formative evaluation (during the process) and summative evaluation (of final results). This metacognitive phase ensures quality and requires at least 5 detailed evaluation criteria.",
                                'fr': "Phase 5 - Cadre d'évaluation: Métriques d'évaluation complètes pour garantir l'efficacité des changements planifiés. Définissez des critères spécifiques pour évaluer chaque aspect du contenu amélioré. Établissez des repères de qualité pour la clarté, l'exhaustivité, l'exactitude et l'alignement avec les attentes. Créez une approche systématique pour vérifier que tous les problèmes identifiés ont bien été traités. Développez des méthodes pour évaluer la bonne intégration du contenu révisé avec l'ensemble du document. Incluez à la fois une évaluation formative (pendant le processus) et sommative (des résultats finaux). Cette phase métacognitive assure la qualité et nécessite au moins 5 critères d'évaluation détaillés."
                            }}),
                        },
                        "implementation_details": {
                            "type": "string",
                            "description": sota.t('', {'': {
                                'en': "Technical implementation specifications focusing on HTML formatting, special tags, and structural requirements. Detail exactly how to handle: 1) HTML formatting requirements for content, ensuring only permitted tags are used; 2) Special tag preservation including references (<reference>), comments (<comment> which you should systematically include in your new or edited comments), inline mentions (<mention>, 5-6 words max), and locked content (<lock>); 3) Content organization ensuring titles appear only in the title field and not duplicated in HTML content; 4) Comment management, specifying how existing comments should be preserved while new ones include proper time/author attributions; 5) Reference management with proper 4-digit IDs and correct informationid attributes; 6) Techniques for preserving document integrity during editing. This section must include at least 5 implementation guidelines addressing the specified HTML formatting standards.",
                                'fr': "Spécifications techniques d'implémentation axées sur le formatage HTML, les balises spéciales et les exigences structurelles. Détaillez précisément comment gérer : 1) Les exigences de formatage HTML pour le contenu, en veillant à n'utiliser que les balises autorisées; 2) La préservation des balises spéciales, y compris les références (<reference>), les commentaires (<comment> à inclure systématiquement dans les commentaires créés ou modifiés), les mentions en ligne (<mention>, 5-6 mots max) et le contenu verrouillé (<lock>); 3) L'organisation du contenu garantissant que les titres n'apparaissent que dans le champ prévu et ne sont pas dupliqués dans le contenu HTML; 4) La gestion des commentaires, en précisant comment les commentaires existants doivent être conservés tandis que les nouveaux incluent les attributions appropriées de temps et d'auteur; 5) La gestion des références avec des identifiants à 4 chiffres corrects et des attributs informationid appropriés; 6) Des techniques spécifiques pour préserver l'intégrité du document lors de l'édition. Cette section doit comporter au moins 5 directives d'implémentation répondant aux normes de formatage HTML précisées."
                            }}),
                        }
                    },
                    "required": ["analysis_phase", "design_phase", "development_phase", "implementation_strategy", "evaluation_framework", "implementation_details"],
                    "additionalProperties": False
                },
                "title": {
                    "type": "string",
                    "description": title_description
                },
                "html_expectations": {
                    "type": "string",
                    "description": html_expectations_description
                },
                "referencements": {
                    "type": "array",
                    "description": sota.t('', {'': {
                        'en': f"References. All <reference refid=\"xxx\"> in the content must link to an existing external reference. If you want to add references within the content, you must create them here first. Choose from the free ref IDs provided: {free_refs}. To update or complement an existing reference, consult the existing list: {existing_refs}.",
                        'fr': f"Références. Tous les <reference refid=\"xxx\"> dans le contenu doivent faire référence à une référence externe existante. Si vous souhaitez ajouter des références dans le contenu, vous devez d'abord les créer ici. Choisissez parmi les identifiants libres suivants : {free_refs}. Pour mettre à jour ou compléter une référence existante, consultez la liste suivante : {existing_refs}."
                    }}),
                    "items": {
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "enum": ["CREATE", "EDIT"],
                                "description": "Mode of operation for this reference: 'CREATE' for new references or 'EDIT' for existing references. If CREATE, use a free refid. If EDIT, use an existing refid.",
                            },
                            "refid": {
                                "type": "string",
                                "description": sota.t('', {'': {
                                    'en': f'If mode is CREATE, use the provided free refids, in order. If mode is EDIT, use the existing refid. Free refids are: {free_refs}. Existing refids are: {existing_refs}.',
                                    'fr': f'Si le mode est CREATE, utilisez les refids libres fournis, dans l\'ordre. Si le mode est EDIT, utilisez le refid existant. Les refids libres sont : {free_refs}. Les refids existants sont : {existing_refs}.'
                                }}),
                            },
                            "informationid": {
                                "type": "string",
                                "description": sota.t('', {'': {
                                    'en': 'Identifier of the referenced information, as detailed by "informationid" in the provided data. This is the id of the referenced information, not the 4-digit refid.',
                                    'fr': 'Identifiant de l\'information référencée, tel que défini par "informationid" dans les données fournies. Ce n\'est pas le refid à 4 chiffres, mais l\'id de l\'information référencée.'
                                }}),
                            },
                            "position": {
                                "type": "string",
                                "description": sota.t('', {'': {
                                    'en': 'For external references, provide a comma-separated list of chunk positions you are citing. Example: 12, 15, 18. Leave empty for internal references.',
                                    'fr': 'Pour les références externes, fournissez une liste de positions de chunks séparées par des virgules. Exemple : 12, 15, 18. Laissez vide pour des références internes.'
                                }}),
                            },
                            "html_contents": {
                                "type": "string",
                                "description": sota.t('', {'': {
                                    'en': 'Cite (using <blockquote>) and analyse. This will be used to verify any information or statement made. It is essential for audits, scientific reviews, and fact-checking. Aim at 50-50 split between citation and analysis.',
                                    'fr': 'Citez (en utilisant <blockquote>) et analysez. Cela sera utilisé pour vérifier toute information ou déclaration faite. C\'est essentiel pour les audits, les revues scientifiques et la vérification des faits. Visez un partage 50-50 entre citation et analyse.'
                                }}),
                            }
                        },
                        "required": ["mode", "refid", "informationid", "position", "html_contents"],
                        "additionalProperties": False
                    }
                },
                "comments": {
                    "type": "array",
                    "description": comments_description,
                    "items": {
                        "type": "object",
                        "properties": {
                            "comment_id": {
                                "type": "string",
                                "description": comment_id_description
                            },
                            "comment_html": {
                                "type": "string",
                                "description": comment_html_description
                            }
                        },
                        "required": ["comment_id", "comment_html"],
                        "additionalProperties": False
                    }
                },
                "html_content": {
                    "type": "string",
                    "description": html_content_description
                }
            }
    required = ["thoughts_and_reflection", "title"]
    if act_on_expectations:
        required.append("html_expectations")
    if act_on_contents:
        required.append("html_content")
        required.append("comments")
        required.append("referencements")
    if act_on_comments:
        required.append("comments")
    json_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "section",
            "strict": True,
            "schema": 
                {
                "type": "object",
                "properties": {k:v for k,v in fields.items() if k in required},
                "required": list(set(required)),
                "additionalProperties": False
                }
        }
    }
    return json.dumps(json_schema, indent = 2)

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
                    'en': "HTML-Formatted bibliography, using an unordered list. Specify the reference <reference informationid=.../> for each reference (at the beginning of each line).",
                    'fr': "Bibliographie formatée en HTML, en utilisant une liste non ordonnée. Spécifiez la référence <reference informationid=.../> pour chaque référence (au début de chaque ligne)."
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
                    title: str,
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
            'en':'Above are, in order%s%s, an example of how sections\' content should be formatted, with allowed html tags, and, finally, the focused section which you will have to work on (%s). Pay very close attention to the comments in the focused section as well as any last-minute instructions below, as those will indicate you what is expected from you. In your reasoning phase, analyse as thoroughly as possible in order to MAXIMIZE the quality of your answer.',
            'fr':'Voici, dans l\'ordre%s%s, un exemple de la façon dont le contenu des sections doit être formaté, avec les balises html autorisées, et, enfin, la section ciblée sur laquelle vous devrez travailler (%s). Prêtez une attention très particulière aux commentaires de la section ciblée, car ils vous fourniront des informations supplémentaires sur ce qui est attendu de vous. Dans votre phase de raisonnement, analysez aussi minutieusement que possible afin de MAXIMISER la qualité de votre réponse.'
            },
        'text_format': {
            'en': 'In the end, you will be tasked with providing:%s%s%s%s',
            'fr': 'En fin de compte, vous devrez fournir:%s%s%s%s'
        },
        'sections_format':{
            'en': ' In the end, you will be tasked with providing subsections to the focused section/ chapter, with, for each section, its title, expectations, and contents.',
            'fr': ' En fin de compte, vous devrez fournir des sous-sections à la section/chapitre ciblé, avec, pour chaque section, son titre, ses attentes et son contenu.'
        },
        'references': {
            'en': ', the references to use',
            'fr': ', les références à utiliser'
        },
        'document': {
            'en': ', the full document at its current version',
            'fr': ', le document complet à sa version actuelle'
        },
        'last_minute_instructions': {
            'en': 'Finally (important!):\n %s',
            'fr': 'Enfin (important!):\n %s'
        },
        'new_title': {
            'en': '\n- A new title (no html). Unless really necessary, keep the same as before.',
            'fr': '\n- Un nouveau titre (pas de html). Sauf si vraiment nécessaire, gardez le même que précédemment.',
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
        },
        'current_time': {
            'en': 'To add inline mentions if needed, use <mention time="%s" author="AI">content</mention>. Mentions\' contents are meant to be 5-6 words MAXIMUM.',
            'fr': 'Pour ajouter des mentions en ligne si nécessaire, utilisez <mention time="%s" author="AI">contenu</mention>. Le contenu des mentions doit être de 5 à 6 mots MAXIMUM.'
        }
    }
    # Build instructions prompt combining:
    # 1. Main instructions (with references and document if included)
    # 2. Format instructions (either text or sections mode)
    # 3. Any last-minute instructions
    # 4. Current time information in a readable format
    
    instructions_prompt = ( sota.t('instructions', traductions) % \
            (sota.t('references', traductions) if include_references else '',
            sota.t('document', traductions) if include_article else '', 
            title)) \
        + ( sota.t('text_format', traductions) % \
                (sota.t('new_title', traductions) if act_on_title else '',
                sota.t('new_expectations', traductions) if act_on_expectations else '',
                sota.t('new_comment', traductions) if act_on_contents else '',
                sota.t('new_comments', traductions) if act_on_comments else '') \
            if mode == 'text' \
            else \
                sota.t('sections_format', traductions)) \
        + '\n' + (sota.t('last_minute_instructions', traductions) % (last_minute_instructions if last_minute_instructions else '')) \
        
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
            'en': '# ============================== References ==============================\n\n',
            'fr': '# ============================== Références ==============================\n\n'
        },
        'document': {
            'en': '\n\n# ============================== Full Document ==============================\n\n',
            'fr': '\n\n# ============================== Document complet, version actuelle ==============================\n\n'
        },
        'format': {
            'en': '\n\n# ============================== HTML Format for Sections\' content ==============================\n\n',
            'fr': '\n\n# ============================== Format HTML pour le contenu des sections ==============================\n\n'
        },
        'focused': {
            'en': '\n\n# ============================== Focused Section ==============================\n\n',
            'fr': '\n\n# ============================== Section ciblée sur laquelle travailler ==============================\n\n'
        },
        'instructions': {
            'en': '\n\n# ============================== Instructions ==============================\n\n',
            'fr': '\n\n# ============================== Instructions ==============================\n\n'
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
    title = sota.get_last(sota.information[information_id].title.versions, sota.versions_list(-1))
    instructions = get_instruction(sota, title, include_article=include_article, include_references=include_references, act_on_comments=act_on_comments, act_on_contents=act_on_contents, act_on_expectations=act_on_expectations, last_minute_instructions=last_minute_instructions, mode=mode)
    instructions_header = sota.t('instructions', traductions)
    instructions = f"{instructions_header}{instructions}"
    # 6. The final prompt for the LLM
    final_prompt = f"{references}{article}{format_prompt}{focus}{instructions}"
    # 7. Send that to the LLM
    prompt = PROMPT()
    prompt.add(final_prompt, role='user')
    free_ref_ids = []
    from random import randint
    while len(free_ref_ids) < 10:
        new_id = randint(1000, 9999)
        if new_id not in free_ref_ids and new_id not in sota.information[information_id].referencements:
            free_ref_ids.append(new_id)
    existing_ref_ids = list(sota.information[information_id].referencements.keys())
    schema = get_json_schema(sota, free_ref_ids, existing_ref_ids, act_on_expectations = act_on_expectations, act_on_comments = act_on_comments, act_on_contents = act_on_contents) if mode == 'text' else get_sections_schema(sota)
    result = LLMS_v2(
        schema,
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
    return complex_rewrite(
        sota, 
        information_id, 
        act_on_title=True, 
        act_on_comments=True, act_on_contents=final_comment, last_minute_instructions=additional_instructions, references_mode=references_mode)

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
    langage_cache = sota.language
    sota.language = langage
    last_minute_instructions = sota.t('', {'': {
        'en': 'Please translate this section in English. Make sure to preserve styling and references. If it is already in English, then just copy it verbatim without the slightest change.',
        'fr': 'Veuillez traduire cette section en français. Assurez-vous de préserver le style et les références. Si le texte est déjà en français, copiez-le tel quel sans le moindre changement.'
    }})
    result = complex_rewrite(sota, information_id, include_article=False, include_references=False, act_on_title=True, act_on_contents=True, last_minute_instructions=last_minute_instructions)
    sota.language = langage_cache
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
    raise NotImplementedError("This function is deprecated.")
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
    lucario.update()
    def jsonloads(text):
        try:
            return json.loads(text)
        except:
            return text
    prompt = PROMPT()
    prompt.add(
        json.dumps({f'reference_id: {k} (cite as <reference informationid="{k}" />)':jsonloads(v.description) for k,v in lucario.elements.items()}, indent=4), 
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