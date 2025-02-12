from typing import List
import json 
from pydantic import BaseModel, Field
from typing import Optional, Union, Literal
import os
from langchain.chat_models import init_chat_model
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
import numpy as np

class LLM(BaseModel):
    class Config(BaseModel):
        def env(self):
            for field in self.__fields_set__:
                os.environ[field] = str(getattr(self, field))
                
    class OpenAIConfig(Config):
        OPENAI_API_KEY: str = Field(..., description = "OpenAI API Key")
        def get_model(self, llm: 'LLM'):
            self.env()
            return init_chat_model(llm.model_name, model_provider="openai")
        def get_embeddings_model(self, llm: 'LLM'):
            self.env()
            return OpenAIEmbeddings(model=llm.llm_name)
        
    class AzureOpenAIConfig(Config):
        AZURE_OPENAI_ENDPOINT: str = Field(..., description = "Azure OpenAI Endpoint")
        AZURE_OPENAI_API_VERSION: str = Field(..., description = "Azure OpenAI API Version")
        AZURE_OPENAI_API_KEY: str = Field(..., description = "Azure OpenAI API Key")
        def get_model(self, llm: 'LLM'):
            self.env()
            return AzureChatOpenAI(
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                azure_deployment=llm.model_name,
                openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            )
        def get_embeddings_model(self, llm: 'LLM'):
            self.env()
            return AzureOpenAIEmbeddings(
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                azure_deployment=llm.model_name,
                openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            )
    llm_category: Literal['text', 'embeddings'] = Field(..., description = "Model category")
    
    image_url: Optional[str] = Field(None, description = "Image URL")
    llm_name: str = Field(..., description = "Model name")
    
    tool_calling: bool = Field(True, description = "Tool calling supported")
    support_system_roles: bool = Field(True, description = "Support system role")
    structured_outputs: bool = Field(True, description = "Structured outputs supported")
    json_outputs: bool = Field(True, description = "JSON outputs supported")
    image_inputs: bool = Field(False, description = "Image inputs supported")
    audio_inputs: bool = Field(False, description = "Audio inputs supported")
    video_inputs: bool = Field(False, description = "Video inputs supported")
    
    config : Union[OpenAIConfig, AzureOpenAIConfig] = Field(..., description = "Model configuration")
            
    def __call__(self, message, structured: BaseModel = None):
        if self.llm_category == 'text':
            model = self.config.get_model(self)
            if structured is not None:
                assert self.structured_outputs, "Structured outputs not supported"
                model = llm.with_structured_output(structured)
            return llm.invoke(message)
        elif self.llm_category == 'embeddings':
            model = self.config.get_embeddings_model(self)
            if isinstance(message, str):
                message = [message]
            return np.array(model.embed_documents(message))
        else:
            raise ValueError("Model category not supported")
    
class Converter:
    @staticmethod
    def to_bytes(llm : LLM) -> bytes:
        return bytes(json.dumps(llm.dict()), 'utf-8')
        
    @staticmethod
    def from_bytes(b: bytes) -> LLM:
        return LLM.model_validate(json.loads(b.decode('utf-8')))
    
    @staticmethod
    def len(bib : LLM) -> int:
        return 1
    
from custom_types.wrapper import TYPE
wraped = TYPE(
    extension='llm',
    _class = LLM,
    converter = Converter,
    icon='/micons/lib.svg'
)