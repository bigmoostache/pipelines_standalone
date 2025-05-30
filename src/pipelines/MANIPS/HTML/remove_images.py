from bs4 import BeautifulSoup

def remove_images_regex(html_string):
    """
    Remove all <img> tags from HTML string using regex.
    Simple but may not handle all edge cases.
    """
    # Remove <img> tags (both self-closing and with closing tags)
    img_pattern = r'<img[^>]*/?>'
    cleaned_html = re.sub(img_pattern, '', html_string, flags=re.IGNORECASE)
    return cleaned_html

def remove_images_bs4(html_string):
    """
    Remove all <img> tags from HTML string using BeautifulSoup.
    More robust and handles malformed HTML better.
    """
    soup = BeautifulSoup(html_string, 'html.parser')
    
    # Find all img tags and remove them
    for img_tag in soup.find_all('img'):
        img_tag.decompose()  # Completely removes the tag
    
    return str(soup)

def remove_images(html_string):
    """
    Main function to remove images from HTML string.
    Uses BeautifulSoup by default for better reliability.
    Falls back to regex if BeautifulSoup is not available.
    """
    try:
        return remove_images_bs4(html_string)
    except ImportError:
        print("BeautifulSoup not available, falling back to regex method")
        return remove_images_regex(html_string)
    
from custom_types.HTML.type import HTML

class Pipeline:
    def __init__(self):
        pass
    def __call__(self, html : HTML) -> HTML:
        return HTML(
            html = remove_images(html.html)
        )
        