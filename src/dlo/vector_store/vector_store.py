from abc import ABC, abstractmethod, abstractproperty

from langchain_core.documents import Document


class VectorStore(ABC):

    @abstractproperty
    def vector_store(self):
        """Vector store"""

    @abstractmethod
    def delete_collection(self) -> None:
        """Delete collection"""

    @abstractmethod
    def add_documents(self, documents: list[Document], ids: list[str]) -> None:
        """Add documents"""

    @abstractmethod
    async def aadd_documents(self, documents: list[Document], ids: list[str]) -> None:
        """Add documents"""

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        """Delete documents"""

    @abstractmethod
    async def adelete(self, ids: list[str]) -> None:
        """Delete documents"""

    @abstractmethod
    def save(self) -> None:
        """Save vector store content"""
