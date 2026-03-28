
from abc import ABC, abstractmethod
from typing import Optional

from dlo.adapters.model import NodeId, NodeMap
from dlo.common.exceptions import errors
from dlo.core.models.resources import Model


class Adapter(ABC):
    def create_table(self, model: Model):
        if model.compiled is False:
            raise errors.DloRuntimeError(
                f"Model `{model.name}` was not complied but tried to create it"
            )

        return self._create_table(model)

    @abstractmethod
    def execute(self): ...

    @abstractmethod
    def fetch(self): ...

    @abstractmethod
    def _create_table(self, model: Model): ...

    @abstractmethod
    def create_job(
        self, node_map: NodeMap, nodes: list[NodeId], job_name: str, cron: Optional[str] = None
    ): ...
