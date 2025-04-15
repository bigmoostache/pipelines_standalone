from custom_types.PDF.type import PDF
from mistralai import Mistral
import mistralai
import io, os
from time import sleep
class Pipeline:
    """
    Pipeline class for converting PDF files to text using the Mistral OCR API.

    Attributes:
        __env__ (list): A list of required environment variables. This pipeline requires
            the `MISTRAL_API_KEY` environment variable to authenticate with the Mistral API.

    Methods:
        __init__():
            Initializes the Pipeline instance.

        __call__(pdf: PDF) -> str:
            Processes a PDF file using the Mistral OCR API and returns the extracted text
            in Markdown format.

            Args:
                pdf (PDF): An object representing the PDF file to be processed. It should
                    have the attributes `file_name` (str) and `file_as_bytes` (bytes).

            Returns:
                str: The extracted text from the PDF in Markdown format.

            Raises:
                KeyError: If the `MISTRAL_API_KEY` environment variable is not set.
                MistralAPIError: If there is an error during the interaction with the Mistral API.
    """
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
            except mistralai.models.sdkerror.SDKError as e:
                if retries < 5:
                    retries += 1
                    sleep(5)
                    continue
                else:
                    raise e
                
        def build_md(ocr_response):
            md = ""
            for page in ocr_response.pages:
                md += f"// Page {page.index}\n\n"
                md += f"{page.markdown}\n\n"
            return md
        return build_md(ocr_response)