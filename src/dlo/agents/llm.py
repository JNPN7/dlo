"""
Chat Model (LLM) classes with factory
"""

from langchain_core.language_models.chat_models import BaseChatModel

from dlo.common.exceptions import errors


# TODO: Testing all the chat model provider and Add new
class ChatModelFactory:
    @classmethod
    def create(cls, **kwargs) -> BaseChatModel:
        """Create a LLM Model"""
        provider = kwargs.pop("provider")
        try:
            func = getattr(cls, "from_" + provider)
        except KeyError:
            raise errors.MethodNotFoundError(
                f"unknown chat model (llm) provider type {provider!r}"
            )
        return func(**kwargs)

    @classmethod
    def from_openai(cls, **kwargs):
        """Create a chat model (llm) from openai"""
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(**kwargs)

    @classmethod
    def from_google(cls, **kwargs):
        """Create a chat model (llm) from google"""
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(**kwargs)

    @classmethod
    def from_google_genai(cls, **kwargs):
        """Create a chat model (llm) from google"""
        return cls.from_google(**kwargs)

    @classmethod
    def from_azure(cls, **kwargs):
        """Create a chat model (llm) from azure"""
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(**kwargs)

    @classmethod
    def from_bedrock(cls, **kwargs):
        """Create a chat model (llm) from amazon bedrock"""
        from langchain_aws import ChatBedrockConverse

        return ChatBedrockConverse(**kwargs)

    @classmethod
    def from_amazon_bedrock(cls, **kwargs):
        """Create a chat model (llm) from amazon bedrock"""
        return cls.from_bedrock(**kwargs)

    @classmethod
    def from_anthropic(cls, **kwargs):
        """Create a chat model (llm) from anthropic"""
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(**kwargs)
