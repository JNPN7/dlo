from abc import ABC, abstractmethod
from typing import Optional

from dlo.adapters.model import Node, NodeId, NodeMap, QueryResult
from dlo.common.exception import errors
from dlo.core.constants import DEFAULT_CURSOR_LIMIT


class Adapter(ABC):
    def create_table(self, model: Node):
        if model.compiled is False:
            raise errors.DloRuntimeError(
                f"Model `{model.name}` was not complied but tried to create it"
            )

        return self._create_table(model)

    @abstractmethod
    def execute(self, query: str, cursor_limit: Optional[int] = DEFAULT_CURSOR_LIMIT): ...

    @abstractmethod
    def query(self, query: str, cursor_limit: Optional[int] = DEFAULT_CURSOR_LIMIT) -> QueryResult:
        ...

    @abstractmethod
    def _create_table(self, model: Node): ...

    @abstractmethod
    def create_job(
        self,
        node_map: NodeMap,
        nodes: list[NodeId],
        job_name: str,
        cron: Optional[str] = None,
        job_info: Optional[dict] = None,
    ) -> dict: ...

    @abstractmethod
    def pause_job(self, job_info: dict, cron: str) -> Optional[dict]: ...
