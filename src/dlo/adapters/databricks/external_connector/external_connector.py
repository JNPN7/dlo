import logging
from typing import Callable, Optional

from databricks.sdk.service.catalog import ConnectionType
from datakit.core.config import RuntimeConfig
from datakit.execution_engine.databricks.engine import (
    DatabricksConfig,
    DatabricksEngine,
)
from datakit.execution_engine.databricks.schema import ConnectionConfig

logger = logging.getLogger(__name__)


class ExternalConnector(DatabricksEngine):
    """Connector implementation for external databases (PostgreSQL, SQLServer, etc.)."""

    def __init__(
        self,
        config: DatabricksConfig,
        runtime_config: Optional[RuntimeConfig] = None,
        redis_client_callback: Optional[Callable] = None,
        token_validity_seconds: int = 3600,
    ):
        super().__init__(
            config, runtime_config, redis_client_callback, token_validity_seconds
        )

    def create_connection(
        self,
        connection_name: str,
        config: ConnectionConfig,
    ):
        """
        Create an external connection and a corresponding catalog.

        Args:
            connection_name: Name of the connection to create.
            catalog_name: Name of the catalog to create (usually same as connection name).
            connection_params: Parameters for the connection and catalog options.
        """
        logger.info(f"Creating connection '{connection_name}'")

        # Override catalog name if intended to be same as connection name,
        # though function arg implies flexibility. keeping original logic for now.
        catalog_name = connection_name

        try:
            logger.debug(f"Creating connection '{connection_name}'")
            self.client.connections.create(
                name=connection_name,
                connection_type=ConnectionType(config.connection_type),
                options=config.credentials,
                comment="External connection",
            )
        except Exception as e:
            logger.error(f"Failed to create connection '{connection_name}': {e}")
            raise

        try:
            logger.debug(f"Creating catalog '{catalog_name}'")
            self.client.catalogs.create(
                name=catalog_name,
                connection_name=connection_name,
                comment="External catalog",
                options=config.connection_config,
            )
        except Exception as e:
            logger.error(
                f"Failed to create catalog '{catalog_name}', rolling back connection: {e}"
            )
            try:
                self.client.connections.delete(name=connection_name)
            except Exception as delete_error:
                logger.error(
                    f"Failed to rollback connection '{connection_name}': {delete_error}"
                )
            raise e

        try:
            logger.info(f"Discovering schema tables for catalog '{catalog_name}'")
            self.discover_schema_tables(catalog_name)
        except Exception as e:
            logger.error(f"Discovery failed for '{catalog_name}', cleaning up: {e}")
            try:
                self.client.catalogs.delete(name=catalog_name)
                self.client.connections.delete(name=connection_name)
            except Exception as cleanup_error:
                logger.error(
                    f"Failed to cleanup after discovery failure: {cleanup_error}"
                )
            raise e

        logger.info(f"Successfully created connection and catalog '{connection_name}'")

    def update_connection(
        self,
        connection_name: str,
        config: ConnectionConfig,
    ):
        """
        Update an existing connection.

        Args:
            connection_name: Name of the connection to update.
            catalog_name: Name of the catalog (unused in this method but kept for interface consistency).
            connection_params: New parameters for the connection.
        """
        logger.info(f"Updating connection '{connection_name}'")
        try:
            self.client.connections.update(
                name=connection_name,
                options=config.credentials,
            )
            logger.info(f"Successfully updated connection '{connection_name}'")
        except Exception as e:
            logger.error(f"Failed to update connection '{connection_name}': {e}")
            raise

    def delete_connection(self, connection_name: str):
        """
        Delete a connection and its associated catalog.

        Args:
            connection_name: Name of the connection to delete.
            cataldelete_connectiondelete_connectionog_name: Name of the catalog to delete.
        """
        logger.info(
            f"Deleting connection '{connection_name}' and catalog '{connection_name}'"
        )
        try:
            logger.debug(f"Deleting catalog '{connection_name}'")
            self.client.catalogs.delete(name=connection_name)
        except Exception as e:
            logger.warning(
                f"Failed to delete catalog '{connection_name}' (it might not exist): {e}"
            )

        try:
            logger.debug(f"Deleting connection '{connection_name}'")
            self.client.connections.delete(name=connection_name)
        except Exception as e:
            logger.error(f"Failed to delete connection '{connection_name}': {e}")
            raise

        logger.info(f"Successfully deleted connection '{connection_name}'")

    def list_datasets(
        self,
        connection_name: str,
        prefix: str = "",
        warehouse_id: str | None = None,
    ):
        """
        List datasets (tables) within a catalog.
        TODO Use query exeuction and get data instead to get fresh tables
        """
        catalog_name = connection_name
        logger.info(f"Listing datasets for catalog '{catalog_name}'")

        data = [
            {
                "type": "catalog",
                "path": catalog_name,
                "name": catalog_name,
                "items": [],
            }
        ]

        try:
            for schema in self.client.schemas.list(catalog_name=catalog_name):
                catalog_items = data[-1]["items"]
                catalog_items.append(
                    {
                        "type": "schema",
                        "path": f"{catalog_name}/{schema.name}",
                        "full_path": f"{catalog_name}/{schema.name}",
                        "name": schema.name,
                        "items": [],
                    }
                )
                for table in self.client.tables.list(
                    catalog_name=catalog_name, schema_name=schema.name or ""
                ):
                    schema_items = catalog_items[-1]["items"]

                    schema_items.append(
                        {
                            "type": "table",
                            "path": f"{catalog_name}/{schema.name}/{table.name}",
                            "full_path": f"{catalog_name}/{schema.name}/{table.name}",
                            "name": table.name,
                            "items": [],
                        }
                    )
        except Exception as e:
            logger.error(f"Failed to list datasets for '{catalog_name}': {e}")
            raise

        return data
