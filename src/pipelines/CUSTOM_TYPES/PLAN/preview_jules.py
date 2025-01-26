from typing import Any, Dict, List

def _display_section_as_string(section_data: Dict[str, Any], indent: int = 0) -> str:
    """
    Recursively build a string representation of a section (and its subsections) with indentation.
    """
    indent_str = "    " * indent  # 4 spaces per indent level
    section_id = section_data.get("section_id", "Unknown")
    prefix = section_data.get("prefix", "")
    title = section_data.get("title", "")
    abstract = section_data.get("abstract", "")

    # Prepare lines for the current section
    lines = [
        f"{indent_str}{prefix} Section ID: {section_id}",
        f"{indent_str}{prefix} Title: {title}",
        f"{indent_str}{prefix} Abstract: {abstract}",
        ""
    ]

    # Handle leaf bullet points
    contents = section_data.get("contents", {})
    leaf_bullets = contents.get("leaf_bullet_points", [])
    for bullet in leaf_bullets:
        lines.append(f"{indent_str}  - {bullet}")
    if leaf_bullets:
        lines.append("")

    # Recursively process subsections
    subsections = contents.get("subsections", [])
    for sub in subsections:
        lines.append(_display_section_as_string(sub, indent + 1))

    return "\n".join(lines)


def _display_references_as_string(references: List[Dict[str, Any]]) -> str:
    """
    Build a string representation of references if they exist.
    """
    if not references:
        return ""

    lines = ["References:"]
    for ref_item in references:
        reference_id = ref_item.get("reference_id", "N/A")
        citation = ref_item.get("citation", "No citation provided")
        lines.append(f"  [{reference_id}] {citation}")
    lines.append("")  # Blank line after references

    return "\n".join(lines)


def process(dico: dict) -> str:
    """
    Takes a dictionary (representing one JSON entry of hierarchical data) 
    and returns a nicely formatted string representation of its contents.
    """
    # Collect lines in a list and then join them for the final output
    lines = []

    # Add the main section content
    lines.append(_display_section_as_string(dico))

    # Add references, if any
    references = dico.get("references", [])
    if references:
        lines.append(_display_references_as_string(references))

    return "\n".join(lines)


from custom_types.PLAN.type import Plan

class Pipeline:
    def __init__(self):
        pass    
    def __call__(self, 
            plan : Plan,
            ) -> str:
        return process(plan.dict())