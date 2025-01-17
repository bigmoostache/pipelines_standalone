import re, yaml

replacements = {
  "U+00A0": " ",    # Non-breaking space
  "U+2000": " ",    # En quad
  "U+2001": " ",    # Em quad
  "U+2002": " ",    # En space
  "U+2003": " ",    # Em space
  "U+2004": " ",    # Three-per-em space
  "U+2005": " ",    # Four-per-em space
  "U+2006": " ",    # Six-per-em space
  "U+2007": " ",    # Figure space
  "U+2008": " ",    # Punctuation space
  "U+2009": " ",    # Thin space
  "U+200A": " ",    # Hair space
  "U+202F": " ",    # Narrow no-break space
  "U+205F": " ",    # Medium mathematical space
  "U+3000": " ",    # Ideographic space
  "U+0009": "\t",   # Horizontal tab
  "U+200B": "",     # Zero-width space (remove entirely)
  "U+200C": "",     # Zero-width non-joiner (remove entirely)
  "U+200D": "",     # Zero-width joiner (remove entirely)
  "U+FEFF": ""      # Zero-width no-break space (BOM, remove entirely)
}


def robust_safe_load(yaml_text):
    """
    Attempt to load YAML text in a 'robust' manner:
      1. Try normal yaml.safe_load.
      2. If that fails, do a naive fix for lines that appear to have unquoted colons
         in the value part, then re-try loading.

    Returns:
        Parsed Python object (dict, list, etc.) if successful, otherwise raises.
    """
    # replace weird unicode characters that break yaml parser
    for k,v in replacements.items():
        yaml_text = yaml_text.replace(k, v)
        k2 = k.replace("U+", "\\u")
        yaml_text = yaml_text.replace(k2, v)
        k3 = k2.lower()
        yaml_text = yaml_text.replace(k3, v)
    try:
        # First attempt: just parse directly
        return yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        fixed_lines = []
        for line in yaml_text.splitlines():

            match = re.match(r'^(\s*(?:- )?[^:]+:\s)(.*:.*)$', line)
            if match:
                prefix = match.group(1)  # e.g. "key: " or "- name: "
                rest   = match.group(2)  # e.g. "Domain 1 : More text"
                
                # Wrap the rest in quotes (escape existing quotes if any)
                rest_escaped = rest.replace('"', '\\"')
                new_line = f'{prefix}"{rest_escaped}"'
                fixed_lines.append(new_line)
            else:
                # No suspicious pattern found; leave line alone
                fixed_lines.append(line)

        # Now try parsing again with the 'fixed' text
        fixed_text = "\n".join(fixed_lines)
        return yaml.safe_load(fixed_text)