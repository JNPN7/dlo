import json
import os

from typing import Literal

import pytest

from dlo.vector_store.embeddings import Embeddings

test_embeddings_configs = os.environ.get("TEST_EMBEDDINGS_CONFIG")

PERSIST_DIR = "./.data/chroma_langchain_db"

DISTANCE_SUPPORT = Literal["cosine", "l2", "ip"]


class TestChroma:
    @pytest.mark.parametrize("configs", [test_embeddings_configs])
    def test_chroma(self, configs):
        config = json.loads(configs)[0]
        embeddings = Embeddings.create(**config)

        from langchain_chroma import Chroma

        vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR,
            collection_metadata={"hnsw:space": "cosine"},
        )

        # For hosted
        # vector_store = Chroma(
        #     collection_name="example_collection",
        #     embedding_function=embeddings,
        #     host="localhost",
        # )

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

        # Update Doc
        updated_document_1 = Document(
            page_content="I had chocolate chip pancakes and fried eggs for breakfast this morning.",  # noqa: E501
            metadata={"source": "tweet"},
            id=1,
        )

        updated_document_2 = Document(
            page_content="The weather forecast for tomorrow is sunny and warm, with a high of 82 degrees.",  # noqa: E501
            metadata={"source": "news"},
            id=2,
        )

        vector_store.update_document(document_id=uuids[0], document=updated_document_1)
        # You can also update multiple documents at once
        vector_store.update_documents(
            ids=uuids[:2], documents=[updated_document_1, updated_document_2]
        )

        # Delete Doc
        vector_store.delete(ids=uuids[-1])

        # With Filter
        results = vector_store.similarity_search(
            "LangChain provides abstractions to make working with LLMs easy",
            k=2,
            filter={"source": "tweet"},
        )
        for res in results:
            print(f"* {res.page_content} [{res.metadata}]")

        # Search with score
        results = vector_store.similarity_search_with_score(
            "Will it be hot tomorrow?", k=1, filter={"source": "news"}
        )
        for res, score in results:
            print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")

        # Search by vector
        results = vector_store.similarity_search_by_vector(
            embedding=embeddings.embed_query("I love green eggs and ham!"), k=1
        )
        for doc in results:
            print(f"* {doc.page_content} [{doc.metadata}]")

        # As Retriever
        retriever = vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 5, "fetch_k": 5}
        )
        data = retriever.invoke("Stealing from the bank is a crime", filter={"source": "news"})
        print(data)
