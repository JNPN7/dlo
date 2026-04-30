from functools import cached_property
from pathlib import Path

from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

import faiss

from dlo.common.exceptions import errors
from dlo.core.config import VectorCollectionConfig
from dlo.vector_store.vector_store import VectorStore

# Connection_config -> {"path"}


class FaissVectorStore(VectorStore):
    def __init__(
        self,
        embeddings: Embeddings,
        connection_config: dict,
        collection_config: VectorCollectionConfig,
        *args,
        **kwargs,
    ):
        self.connection_config = connection_config
        self.embeddings = embeddings
        self.collection_config = collection_config

    @cached_property
    def persist_dir(self) -> Path:
        if "path" not in self.connection_config:
            raise errors.DloConfigError("Path needs to be passed for faiss")
        path = self.connection_config["path"]
        return Path(path) / self.collection_config.collection

    @cached_property
    def vector_store(self):
        if self.persist_dir.exists():
            return FAISS.load_local(
                self.persist_dir, self.embeddings, allow_dangerous_deserialization=True
            )

        # Getting the dim from embeddings only
        index = faiss.IndexFlatL2(len(self.embeddings.embed_query("hello world")))

        return FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
            distance_strategy=self.collection_config.distance,
        )

    def delete_collection(self) -> None:
        import shutil

        shutil.rmtree(self.persist_dir)

    def add_documents(self, documents: list[Document], ids: list[str]) -> None:
        self.vector_store.add_documents(documents=documents, ids=ids)

    async def aadd_documents(self, documents: list[Document], ids: list[str]) -> None:
        await self.vector_store.aadd_documents(documents=documents, ids=ids)

    def delete(self, ids: list[str]) -> None:
        self.vector_store.delete(ids)

    async def adelete(self, ids: list[str]) -> None:
        self.vector_store.adelete(ids)

    def save(self) -> None:
        self.vector_store.save_local(self.persist_dir)
