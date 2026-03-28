import logging
from typing import Callable, Optional

from datakit.core.config import RuntimeConfig
from datakit.execution_engine.databricks.engine import (
    DatabricksConfig,
    DatabricksEngine,
)
from datakit.execution_engine.databricks.external_connector.external_connector import (
    ExternalConnector,
)
from datakit.execution_engine.databricks.external_location.external_location import (
    ExternalLocation,
)

logger = logging.getLogger(__name__)


class DatabricksEngineFactory:
    """Factory for creating Databricks connectors based on connection type."""

    @staticmethod
    def create(
        connection_type: str,
        config: DatabricksConfig,
        runtime_config: Optional[RuntimeConfig] = None,
        redis_client_callback: Optional[Callable] = None,
        token_validity_seconds: int = 3600,
    ) -> DatabricksEngine:
        """
        Create a connector instance based on the connection type.

        Args:
            connection_type: The type of connection (e.g., 'POSTGRESQL', 'AWS').
            config: Databricks configuration.
            runtime_config: Optional runtime configuration.

        Returns:
            An instance of a DatabricksConnector subclass.

        Raises:
            ValueError: If the connection type is not supported.
        """
        logger.debug(f"Creating connector for type: {connection_type}")

        if connection_type in ["AZURE_BLOB", "S3", "GCS", "AZURE_DATA_LAKE"]:
            logger.debug("Instantiating ExternalLocation")
            return ExternalLocation(
                config, runtime_config, redis_client_callback, token_validity_seconds
            )

        logger.debug("Instantiating ExternalConnector")
        return ExternalConnector(
            config, runtime_config, redis_client_callback, token_validity_seconds
        )
