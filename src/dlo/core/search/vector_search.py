import logging

from functools import cached_property

from langchain_core.documents import Document

from dlo.common.exceptions import errors
from dlo.core.config import Embeddings as EmbeddingsConfig
from dlo.core.config import Profile, Project, VectorSearchConfig
from dlo.core.config import VectorStore as VectorStoreConfig
from dlo.core.models.manifest import Manifest
from dlo.core.models.resources import Model, Source
from dlo.vector_store import Embeddings, EmbeddingsFactory, VectorStore, VectorStoreFactory

log = logging.getLogger("__name__")


BATCH_SIZE = 500


class VectorSearch:
    def __init__(
        self, manifest: Manifest, project: Project, profile: Profile, batch_size=BATCH_SIZE
    ):
        self.project = project
        self.profile = profile
        self.manifest = manifest
        self.batch_size = batch_size

        if len(project.vector_search.scope) < 0:
            raise errors.DloConfigError("No scope found, Cannot proceed. Please add search scope")

    @cached_property
    def vector_search_config(self) -> VectorSearchConfig:
        vector_search_config = self.project.vector_search
        if vector_search_config is None:
            raise errors.DloConfigError(
                "No configuration for vector search found."
                "If you want to have vector search capability. Please add vector_search config"
            )
        return vector_search_config

    @cached_property
    def vector_store_config(self) -> VectorStoreConfig:
        vector_store = self.vector_search_config.vector_store
        vector_store_config = self.profile.vector_store.get(vector_store)

        if vector_store_config is None:
            raise errors.DloConfigError(
                f"No configuration found for vector store `{vector_store}` in profile"
            )
        return vector_store_config

    @cached_property
    def embedding_config(self) -> EmbeddingsConfig:
        embedding = self.vector_search_config.embedding
        embedding_config = self.profile.embeddings.get(embedding)

        if embedding_config is None:
            raise errors.DloConfigError(
                f"No configuration found for embedding `{embedding}` in profile"
            )
        return embedding_config

    @cached_property
    def embeddings(self) -> Embeddings:
        return EmbeddingsFactory.create(**self.embedding_config.to_dict())

    @cached_property
    def vector_store(self) -> VectorStore:
        return VectorStoreFactory().create(
            type=self.vector_store_config.type,
            embeddings=self.embeddings,
            connection_config=self.vector_store_config.config,
            collection_config=self.vector_search_config.collection
        )

    def search(self, query):
        documents = self.vector_store.vector_store.similarity_search(
            query, k=self.vector_search_config.top_k
        )
        return documents

    def _normalize_to_list(self, value):
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    def _build_documents(self, resources: list[Source] | list[Model]):
        documents = []
        ids = []
        for resource in resources:
            for scope, scope_config in self.vector_search_config.scope.items():
                values = self._normalize_to_list(getattr(resource, scope))

                for val in values:
                    val_str = str(val)
                    document = Document(
                        page_content=val_str,
                        metadata={"scope": scope, "resource_type": resource.resource_type.value},
                    )
                    _id = f"{resource.unique_id}-{scope}-{val_str}"

                    documents.append(document)
                    ids.append(_id)

        return documents, ids

    def initialize_resource(self, resources: list[Source] | list[Model]):
        documents, ids = self._build_documents(resources=resources)

        for i in range(0, len(documents), self.batch_size):
            self.vector_store.add_documents(
                documents=documents[i:i + self.batch_size],
                ids=ids[i:i + self.batch_size],
            )

    def initialize(self):
        if len(self.vector_search_config.scope) <= 0:
            log.warning("Scope for vector search is empty. This results in empty collection")
            return

        self.initialize_resource(self.manifest.sources.values())
        self.initialize_resource(self.manifest.models.values())

        self.vector_store.save()
