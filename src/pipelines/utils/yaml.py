import re, yaml
from pipelines.utils.useless import Pipeline

def robust_safe_load(yaml_text):
    """
    Attempt to load YAML text in a 'robust' manner:
      1. Try normal yaml.safe_load.
      2. If that fails, do a naive fix for lines that appear to have unquoted colons
         in the value part, then re-try loading.

    Returns:
        Parsed Python object (dict, list, etc.) if successful, otherwise raises.
    """
    # Remove code block markers if present
    if '```yaml' in yaml_text:
        yaml_text = yaml_text[yaml_text.find('```yaml')+7:]
        yaml_text = yaml_text[:yaml_text.find('\n```')]
    # replace weird unicode characters that break yaml parser
    yaml_text = yaml_text.replace(' ', ' ').replace(' ', ' ')
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