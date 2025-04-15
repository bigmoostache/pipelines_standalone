import os
from typing import Literal

Providers = Literal["openai", "cohere", "anthropic", "google", "azure", "huggingface"]

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "text-embedding-3-large",
        ):
        self.provider = provider
        self.model = model
    def __call__(self) -> str:
        # for now, str as output, but this will change
        if self.provider == "openai":
            return self.openai()
        elif self.provider == "azure":
            return self.azure()
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
    def openai(self):
        api_key = os.environ.get("openai_api_key")
        if api_key is None:
            raise ValueError("OpenAI API key not found in environment variables")	
        import openai
        client = openai.OpenAI(api_key=api_key)
        return client
    def azure(self, texts) -> str:
        api_key=os.environ['AZURE_OPENAI_API_KEY']
        azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT']
        api_version="2024-08-01-preview"
        if api_key is None or azure_endpoint is None:
            raise ValueError("Azure OpenAI API key or endpoint not found in environment variables")
        import openai
        client = openai.AzureOpenAI(
                api_key=api_key,  
                api_version=api_version,
                azure_endpoint=azure_endpoint
                )
        return client