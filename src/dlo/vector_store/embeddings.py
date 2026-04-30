"""
Embeddings classes with factory
"""

from langchain_core.embeddings import Embeddings

from dlo.common.exceptions import errors


# TODO: Testing all the embeddings provider and Add new
class EmbeddingsFactory:
    @classmethod
    def create(cls, **kwargs) -> Embeddings:
        """Create a Embeddings Factory"""
        provider = kwargs.pop("provider")
        try:
            func = getattr(cls, "from_" + provider)
        except KeyError:
            raise errors.MethodNotFoundError(f"unknown embeddings provider type {provider!r}")
        return func(**kwargs)

    @classmethod
    def from_openai(cls, config: dict):
        """Create a embeddings from openai"""
        from langchain_openai import AzureOpenAIEmbeddings

        embeddings = AzureOpenAIEmbeddings(**config)
        return embeddings

    @classmethod
    def from_azure(cls, config: dict):
        """Create a embeddings from azure"""
        from langchain_openai import AzureOpenAIEmbeddings

        embeddings = AzureOpenAIEmbeddings(**config)
        return embeddings

    @classmethod
    def from_gemini(cls, config: dict):
        """Create a embeddings from gemini"""
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        embeddings = GoogleGenerativeAIEmbeddings(**config)
        return embeddings

    @classmethod
    def from_vertex(cls, config: dict):
        """Create a embeddings from vertex"""
        from langchain_google_vertexai import VertexAIEmbeddings

        embeddings = VertexAIEmbeddings(**config)
        return embeddings

    @classmethod
    def from_bedrock(cls, config: dict):
        """Create a embeddings from AWS Bedrock"""
        from langchain_aws import BedrockEmbeddings

        embeddings = BedrockEmbeddings(**config)
        return embeddings

    @classmethod
    def from_huggingface(cls, config: dict):
        """Create a embeddings from Huggingface"""
        from langchain_huggingface import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(**config)
        return embeddings

    @classmethod
    def from_ollama(cls, config: dict):
        """Create a embeddings from Ollama"""
        from langchain_ollama import OllamaEmbeddings

        embeddings = OllamaEmbeddings(**config)
        return embeddings

    @classmethod
    def from_cohere(cls, config: dict):
        """Create a embeddings from Cohere"""
        from langchain_cohere import CohereEmbeddings

        embeddings = CohereEmbeddings(**config)
        return embeddings

    @classmethod
    def from_mistral(cls, config: dict):
        """Create a embeddings from Mistral"""
        from langchain_mistralai import MistralAIEmbeddings

        embeddings = MistralAIEmbeddings(**config)
        return embeddings

    @classmethod
    def from_fastembed(cls, config: dict):
        """Create a embeddings from Fastembed (Local)"""
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

        embeddings = FastEmbedEmbeddings(**config)
        return embeddings
