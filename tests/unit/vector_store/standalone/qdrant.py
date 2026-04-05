import json
import os

from typing import Literal

import pytest

from dlo.vector_store.embeddings import Embeddings

test_embeddings_configs = os.environ.get("TEST_EMBEDDINGS_CONFIG")

PERSIST_DIR = "./.data/qdrant_langchain"

DISTANCE_SUPPORT = Literal["Cosine", "Euclid", "Dot", "Manhattan"]


class TestQdrant:
    @pytest.mark.parametrize("configs", [test_embeddings_configs])
    def test_qdrant(self, configs):
        config = json.loads(configs)[0]
        embeddings = Embeddings.create(**config)

        from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
        from qdrant_client import QdrantClient, models
        from qdrant_client.http.models import SparseVectorParams, VectorParams

        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

        client = QdrantClient(path=PERSIST_DIR)

        client.delete_collection("my_documents")

        dim = len(embeddings.embed_query("hello"))
        client.create_collection(
            collection_name="my_documents",
            vectors_config={"dense": VectorParams(size=dim, distance="Cosine")},
            sparse_vectors_config={
                "sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
            },
        )

        vector_store = QdrantVectorStore(
            client=client,
            collection_name="my_documents",
            embedding=embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )

        # Add document
        from uuid import uuid4

        from langchain_core.documents import Document

        document_1 = Document(
            page_content="I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",  # noqa: E501
            metadata={"source": "tweet"},
        )

        document_2 = Document(
            page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",  # noqa: E501
            metadata={"source": "news"},
        )

        document_3 = Document(
            page_content="Building an exciting new project with LangChain - come check it out!",
            metadata={"source": "tweet"},
        )

        document_4 = Document(
            page_content="Robbers broke into the city bank and stole $1 million in cash.",
            metadata={"source": "news"},
        )

        document_5 = Document(
            page_content="Wow! That was an amazing movie. I can't wait to see it again.",
            metadata={"source": "tweet"},
        )

        documents = [
            document_1,
            document_2,
            document_3,
            document_4,
            document_5,
        ]
        uuids = [str(uuid4()) for _ in range(len(documents))]

        vector_store.add_documents(documents=documents, ids=uuids)

        # Delete Doc
        vector_store.delete(ids=[uuids[-1]])

        # With filter
        # filter works little different (Go through proper docs)
        query = ("LangChain provides abstractions to make working with LLMs easy",)
        found_docs = vector_store.similarity_search(query, k=2)
        print(found_docs)

        # Search With score
        results = vector_store.similarity_search_with_score("Will it be hot tomorrow?", k=1)
        for res, score in results:
            print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")

        # As Retriever
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 1})
        data = retriever.invoke("Stealing from the bank is a crime")
        print(data)
