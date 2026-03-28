import json
import os

import pytest

from dlo.vector_store.embeddings import Embeddings

test_embeddings_configs = os.environ.get("TEST_EMBEDDINGS_CONFIG")


class TestEmbeddings:
    @pytest.mark.parametrize("configs", [test_embeddings_configs])
    def test_embeddings(self, configs):
        configs = json.loads(configs)
        for config in configs:
            embeddings = Embeddings.create(**config)
            assert embeddings is not None
