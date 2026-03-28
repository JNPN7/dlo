from typing import Optional, Protocol, Tuple

from datakit.core.schema import DatasetsModel


class ExecutionEngine(Protocol):
    """Protocol for execution engines (DatabricksEngine, etc.)"""

    def execute(self, query: str, warehouse_id: Optional[str] = None) -> list:
        """Execute a SQL query and return results."""
        ...

    @staticmethod
    def get_dataset_name_for_query(
        dataset: DatasetsModel, source_code: str
    ) -> Tuple[str, str]:
        """Get the dataset name for use in SQL queries."""
        ...

    def compile_schedule_job(
        self,
        job_name: str,
        queries: list,
        dataset_map: dict[str, DatasetsModel],
        cron_expression: Optional[str] = None,
        cron_expression_job_id_map: Optional[dict] = None
    ) -> Optional[int]: ...

    def pause_job(self, job_id: int):
        ...
