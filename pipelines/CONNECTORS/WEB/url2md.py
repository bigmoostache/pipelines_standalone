import os, openai, requests
from bs4 import BeautifulSoup

def extract_text_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
        soup = BeautifulSoup(response.content, 'html.parser')

        # Common tags that might contain text content.
        tags_of_interest = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'blockquote', 'table', 'tr', 'td', 'th', 'ul', 'ol']

        text_content = []

        for tag in soup.find_all(tags_of_interest):
            if tag.name.startswith('h'):  # Heading tags could be treated as titles
                text_content.append(f'\n{tag.get_text()}\n')  # Add a newline before and after headings for readability
            else:
                text_content.append(tag.get_text())

        return ' '.join(text_content).strip()

    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        return ""
    except requests.RequestException as e:
        print(f"Request Exception: {e}")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

class Pipeline:
    __env__ = ["openai_api_key"]
    def __init__(self, 
                 role_message : str = "Please extract the actual article in markdown. Remove the rest.", 
                 model : str = 'gpt-3.5-turbo-0125', 
                 temperature : int = 1, 
                 max_tokens : int = 3500, 
                 top_p : int =1, 
                 frequency_penalty : float =0, 
                 presence_penalty : float=0):
        self.model = model
        self.role_message = role_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def __call__(self, url : str) -> str:
        api_key = os.environ.get("openai_api_key")
        client = openai.OpenAI(api_key=api_key)
        extracted_text = extract_text_content(url)
        if len(extracted_text) == 0:
            return "This article could not be extracted. If you are asked to work with it, just say 'EMPTY ARTICLE SORRY'."
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                    {
                        "role": "user",
                        "content": extracted_text
                    },
                    {
                        "role": "system",
                        "content": self.role_message
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
        )
        res = response.choices[0].message.content
        return res

