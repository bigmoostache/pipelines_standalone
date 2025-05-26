from custom_types.PDF.type import PDF
from mistralai import Mistral
import mistralai
import io, os
from time import sleep
from pipelines.CONVERSIONS.PDF.to_txt import Pipeline as PipelineNormal

class Pipeline:
    __env__ = ["MISTRAL_API_KEY"]
    def __init__(self):
        pass
    def __call__(self, pdf : PDF) -> str:
        api_key = os.environ["MISTRAL_API_KEY"]
        client = Mistral(api_key=api_key)
        uploaded_pdf = client.files.upload(
            file={
                "file_name": pdf.file_name,
                "content": pdf.file_as_bytes
            },
            purpose="ocr"
        )
        signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
        retries = 0
        while True:
            try:
                ocr_response = client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "document_url",
                        "document_url": signed_url.url,
                    },
                    include_image_base64=False
                )
                break
            except mistralai.models.sdkerror.SDKError as e:
                # Check for internal server error and fallback if needed
                if retries < 1:
                    retries += 1
                    sleep(5)
                    continue
                else:
                    if (
                        hasattr(e, "args")
                        and len(e.args) >= 3
                        and e.args[1] == 500
                        and 'internal_server_error' in e.args[2]
                    ):
                        # Fallback to PipelineNormal
                        pipeline_normal = PipelineNormal(method='surya')
                        return pipeline_normal(pdf)
                    else:
                        raise e
                
        def build_md(ocr_response):
            md = ""
            for page in ocr_response.pages:
                md += f"// Page {page.index}\n\n"
                md += f"{page.markdown}\n\n"
            return md
        return build_md(ocr_response)
import re 
def extract_pages(text):
    page_markers = re.finditer(r'// Page (\d+)', text)
    page_positions = [(int(match.group(1)), match.start()) for match in page_markers]
    page_positions.sort(key=lambda x: x[1])
    pages = {}
    for i, (page_num, start_pos) in enumerate(page_positions):
        if i < len(page_positions) - 1:
            next_pos = page_positions[i + 1][1]
            content = text[start_pos:next_pos].strip()
        else:
            content = text[start_pos:].strip()
        pages[page_num] = content
    return pages