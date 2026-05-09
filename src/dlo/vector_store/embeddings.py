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

        return AzureOpenAIEmbeddings(**config)

    @classmethod
    def from_azure(cls, config: dict):
        """Create a embeddings from azure"""
        from langchain_openai import AzureOpenAIEmbeddings

        return AzureOpenAIEmbeddings(**config)

    @classmethod
    def from_gemini(cls, config: dict):
        """Create a embeddings from gemini"""
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(**config)

    @classmethod
    def from_vertex(cls, config: dict):
        """Create a embeddings from vertex"""
        from langchain_google_vertexai import VertexAIEmbeddings

        return VertexAIEmbeddings(**config)

    @classmethod
    def from_bedrock(cls, config: dict):
        """Create a embeddings from AWS Bedrock"""
        from langchain_aws import BedrockEmbeddings

        return BedrockEmbeddings(**config)

    @classmethod
    def from_huggingface(cls, config: dict):
        """Create a embeddings from Huggingface"""
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(**config)

    @classmethod
    def from_ollama(cls, config: dict):
        """Create a embeddings from Ollama"""
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(**config)

    @classmethod
    def from_cohere(cls, config: dict):
        """Create a embeddings from Cohere"""
        from langchain_cohere import CohereEmbeddings

        return CohereEmbeddings(**config)

    @classmethod
    def from_mistral(cls, config: dict):
        """Create a embeddings from Mistral"""
        from langchain_mistralai import MistralAIEmbeddings

        return MistralAIEmbeddings(**config)

    @classmethod
    def from_fastembed(cls, config: dict):
        """Create a embeddings from Fastembed (Local)"""
        from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

        return FastEmbedEmbeddings(**config)
