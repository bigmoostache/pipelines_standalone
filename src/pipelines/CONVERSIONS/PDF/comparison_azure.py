from custom_types.PDF.type import PDF
from custom_types.JSONL.type import JSONL
from pypdf import PdfReader
from typing import Literal
import io
import os
import re
import json
import requests
import time
from pipelines.MANIPS.TEXTS.segment_uniform import Pipeline as ChunkingPipeline
import openai, numpy as np

def get_text(pdf: PDF):
    form_data = {
        'file': ('document.pdf', pdf.file_as_bytes, 'application/pdf'),
        'langs': (None, "English"),
        "force_ocr": (None, False),
        "paginate": (None, True),
        'output_format': (None, 'markdown'),
        "disable_image_extraction": (None, True)
    }
    headers = {"X-Api-Key": os.environ.get("surya_api_key")}
    response = requests.post("https://www.datalab.to/api/v1/marker", files=form_data, headers=headers)
    data = response.json()
    max_polls = 300
    check_url = data["request_check_url"]
    
    for i in range(max_polls):
        time.sleep(2)
        response = requests.get(check_url, headers=headers)
        data = response.json()
    
        if data["status"] == "complete":
            break
    return data['markdown']

def replace_pattern(text):
    return re.sub(r'\n\n\{(\d+)\}------------------------------------------------', r'__PAGE_\1__', text)

def paginate(chunks: JSONL):
    current_page = '0'
    local_index = 0
    for line in chunks.lines:
        numbers = re.findall(r"__PAGE_(\d+)__", line['text'])
        line['text'] = re.sub(r"__PAGE_\d+__", "", line['text'])
        line['page_start'] = current_page
        line['local_index'] = local_index
        local_index += 1
        next_current_page=str(max([int(current_page)]+[int(_) for _ in numbers]))
        if next_current_page != current_page:
            local_index = 0
        current_page = next_current_page
        line['page_end'] = current_page
        
def get_embeddings_in_chunks(client, texts, model, chunk_size=1024):
    embeddings = []
    for i in range(0, len(texts), chunk_size):
        chunk = texts[i:i + chunk_size]
        try:
            response = client.embeddings.create(input=chunk, model=model).data
        except:
            response = client.embeddings.create(input=['no data here'] * len(chunk), model=model).data
        embeddings.extend(response)
    return np.array([x.embedding for x in embeddings])

class Pipeline:
    __env__ = ["surya_api_key", 'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT']
    def __init__(self, model: str = 'text-embedding-ada-002'):
        self.model = model
    def __call__(self, old_pdf : PDF, new_pdf : PDF) -> JSONL:
        old_pdf = get_text(old_pdf)
        new_pdf = get_text(new_pdf)
        # Replacing the pattern
        old_pdf = replace_pattern(old_pdf)
        new_pdf = replace_pattern(new_pdf)
        # Chunking the text
        old_pdf = ChunkingPipeline(n_chars = 1000)(old_pdf)
        new_pdf = ChunkingPipeline(n_chars = 1000)(new_pdf)
        # Paginating the chunks
        paginate(old_pdf)
        paginate(new_pdf)
        # Embedding the chunks
        client = openai.AzureOpenAI(
                api_key=os.environ['AZURE_OPENAI_API_KEY'],  
                api_version="2024-08-01-preview",
                azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
                )
        model = self.model
        texts_old_pdf = [_['text'] for _ in old_pdf.lines]
        texts_new_pdf = [_['text'] for _ in new_pdf.lines]
        embeddings_old = get_embeddings_in_chunks(client, texts_old_pdf, model)
        embeddings_new = get_embeddings_in_chunks(client, texts_new_pdf, model)
        M = embeddings_old.dot(embeddings_new.T)
        # Crafting the jobs
        works = []
        for i in range(len(new_pdf.lines)):
            old_chunks = np.argsort(M[:, i])[-5:][::-1]
            works.append(
                {
                    **new_pdf.lines[i],
                    'old': [old_pdf.lines[j] for j in old_chunks]
                }
            )
        return JSONL(works)
