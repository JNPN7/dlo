from dlo.vector_store.factory import VectorStoreFactory
from dlo.vector_store.stores.faiss.impl import FaissVectorStore


def register(factory: VectorStoreFactory, name: str = "faiss"):
    factory.register(name, FaissVectorStore)
