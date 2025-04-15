import os
from typing import List, Literal
import numpy as np
from pipelines.LLMS.v3.client import Pipeline as ClientPipeline, Providers

class Pipeline:
    def __init__(self,
        provider: Providers = "openai",
        model: str = "text-embedding-3-large",
        chunk_size: int = 1000,
        ):
        self.provider = provider
        self.model = model
        self.chunk_size = chunk_size
    def __call__(self, texts: List[str]) -> np.ndarray:
        if self.provider == "openai":
            return self.openai(texts)
        elif self.provider == "azure":
            return self.azure(texts)
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")
    def openai(self, texts) -> np.ndarray:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        embeddings = []
        for i in range(0, len(texts), self.chunk_size):
            chunk = texts[i:i + self.chunk_size]
            response = client.embeddings.create(input=chunk, model=self.model).data
            embeddings.extend(response)
        return np.array([x.embedding for x in embeddings])
    def azure(self, texts) -> np.ndarray:
        client = ClientPipeline(provider=self.provider, model=self.model)()
        embeddings = []
        for i in range(0, len(texts), self.chunk_size):
            chunk = texts[i:i + self.chunk_size]
            response = client.embeddings.create(input=chunk, model=self.model).data
            embeddings.extend(response)
        return np.array([x.embedding for x in embeddings])