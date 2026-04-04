import json
import os

import pytest

from dlo.vector_store.embeddings import Embeddings

test_embeddings_configs = os.environ.get("TEST_EMBEDDINGS_CONFIG")

PERSIST_DIR = "./.data/fiass_index"


class TestFiass:
    @pytest.mark.parametrize("configs", [test_embeddings_configs])
    def test_fiass(self, configs):
        config = json.loads(configs)[0]
        embeddings = Embeddings.create(**config)

        # Initialize
        import faiss

        from langchain_community.docstore.in_memory import InMemoryDocstore
        from langchain_community.vectorstores import FAISS

        index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

        # Add document
        from uuid import uuid4

        from langchain_core.documents import Document

        document_1 = Document(
            page_content="I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",
            metadata={"source": "tweet"},
        )

        document_2 = Document(
            page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
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

        # To update we need to delete document then add the document

        # With Filter
        results = vector_store.similarity_search(
            "LangChain provides abstractions to make working with LLMs easy",
            k=2,
            filter={"source": "tweet"},
        )
        for res in results:
            print(f"* {res.page_content} [{res.metadata}]")

        # Filter $eq $neq
        results = vector_store.similarity_search(
            "LangChain provides abstractions to make working with LLMs easy",
            k=2,
            filter={"source": {"$eq": "tweet"}},
        )
        for res in results:
            print(f"* {res.page_content} [{res.metadata}]")

        # Search With score
        results = vector_store.similarity_search_with_score(
            "Will it be hot tomorrow?", k=1, filter={"source": "news"}
        )
        for res, score in results:
            print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]")

        # As Retriever
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 1})
        data = retriever.invoke("Stealing from the bank is a crime", filter={"source": "news"})
        print(data)

        # SAVE LOAD
        vector_store.save_local(PERSIST_DIR)
        new_vector_store = FAISS.load_local(
            PERSIST_DIR, embeddings, allow_dangerous_deserialization=True
        )
        docs = new_vector_store.similarity_search("qux")
        print(docs)
