import logging
from typing import Callable, Optional

# from databricks_connector.schema import ExternalLocationParams
from databricks.sdk.service.catalog import (
    AwsIamRole,
    AzureManagedIdentity,
    AzureServicePrincipal,
    CredentialPurpose,
    DatabricksGcpServiceAccount,
)

from datakit.core.config import RuntimeConfig
from datakit.execution_engine.databricks.engine import (
    DatabricksConfig,
    DatabricksEngine,
)
from datakit.execution_engine.databricks.schema import ConnectionConfig

logger = logging.getLogger(__name__)


class ExternalLocation(DatabricksEngine):
    """Connector implementation for External Locations (AWS S3, Azure ADLS, GCP GCS)."""

    CREDENTIAL_MAP = {
        "aws_iam_role": AwsIamRole,
        "azure_managed_identity": AzureManagedIdentity,
        "azure_service_principal": AzureServicePrincipal,
        "databricks_gcp_service_account": DatabricksGcpServiceAccount,
    }

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
        Create a storage credential and an external location.

        Args:
            connection_name: Name of the external location (and derived credential name).
            catalog_name: Unused for external locations, but kept for interface consistency.
            connection_params: Parameters including URL and credential details.
        """
        logger.info(f"Creating external location '{connection_name}'")

        credential_name = f"{connection_name}_credential"
        credential_type = self.CREDENTIAL_MAP[config.auth_type]
        connection_params = credential_type(**config.credentials)
        # breakpoint()

        _config = {"name": credential_name, config.auth_type: connection_params}

        try:
            logger.debug(f"Creating credential '{credential_name}'")
            # name argument is positional or keyword depending on SDK version, safe to use named
            self.client.credentials.create_credential(
                **_config, purpose=CredentialPurpose.STORAGE
            )
        except Exception as e:
            logger.error(f"Failed to create credential '{credential_name}': {e}")
            raise

        try:
            logger.debug(
                f"Creating external location '{connection_name}' with url '{config.connection_config}'"
            )
            loc = self.client.external_locations.create(
                name=connection_name,
                credential_name=credential_name,
                **config.connection_config,
            )
            logger.info(f"Successfully created external location: {loc.name}")
        except Exception as e:
            logger.error(
                f"Failed to create external location '{connection_name}', rolling back credential: {e}"
            )
            try:
                self.client.credentials.delete_credential(name_arg=credential_name)
            except Exception as delete_error:
                logger.error(
                    f"Failed to delete credential '{credential_name}': {delete_error}"
                )
            raise e

    def delete_connection(self, connection_name: str):
        """
        Delete an external location and its associated credential.
        """
        logger.info(f"Deleting external location '{connection_name}'")

        credential_name = f"{connection_name}_credential"

        try:
            logger.debug(f"Deleting external location object '{connection_name}'")
            self.client.external_locations.delete(name=connection_name)
        except Exception as e:
            logger.error(f"Failed to delete external location '{connection_name}': {e}")
            # Continue to try deleting credential even if location delete fails (or maybe it was already deleted)

        try:
            logger.debug(f"Deleting credential '{credential_name}'")
            self.client.credentials.delete_credential(name_arg=credential_name)
        except Exception as e:
            logger.error(f"Failed to delete credential '{credential_name}': {e}")
            raise

        logger.info(
            f"Successfully deleted external location resources for '{connection_name}'"
        )

    def update_connection(
        self,
        connection_name: str,
        config: ConnectionConfig,
    ):
        """
        Update an external location and its credential.
        """
        logger.info(f"Updating external location '{connection_name}'")

        credential_name = f"{connection_name}_credential"
        credential_type = self.CREDENTIAL_MAP[config.auth_type]

        connection_params = credential_type(**config.credentials)

        _config = {"name_arg": credential_name, config.auth_type: connection_params}

        try:
            logger.debug(f"Updating credential '{credential_name}'")

            # Use name_arg if available, or name. Based on delete using name_arg, try name_arg.
            # We assume the SDK uses 'name_arg' for update as well or 'name'.
            # Given previous failure with 'name', we use 'name_arg'.
            self.client.credentials.update_credential(**_config)
        except Exception as e:
            logger.error(f"Failed to update credential '{credential_name}': {e}")
            raise

        try:
            logger.debug(f"Updating external location url to '{connection_params.url}'")
            self.client.external_locations.update(
                name=connection_name,
                url=connection_params.url,
                credential_name=credential_name,
            )
            logger.info(f"Successfully updated external location '{connection_name}'")
        except Exception as e:
            logger.error(f"Failed to update external location '{connection_name}': {e}")
            raise

    def get_external_location(self, name: str):
        """
        Get details of a specific external location.

        Args:
            name: Name of the external location.

        Returns:
            ExternalLocationInfo object with location details.
        """
        logger.debug(f"Fetching details for external location '{name}'")
        return self.client.external_locations.get(name=name)

    def list_datasets(
        self,
        connection_name: str,
        prefix: str = "",
        warehouse_id: str | None = None,
    ):
        """
        List files in the external location.
        """
        logger.info(f"Listing datasets for '{connection_name}' with prefix '{prefix}'")

        # Get the external location to retrieve its URL
        location = self.get_external_location(connection_name)

        if location.url is None:
            logger.error(f"External location '{connection_name}' has no URL")
            raise ValueError("URL location is none which shouldn't be the case")

        # Construct the full path
        base_url = location.url.rstrip("/")
        if prefix:
            full_path = f"{base_url}/{prefix.lstrip('/')}"
        else:
            full_path = base_url

        # Get warehouse ID if not provided
        if not warehouse_id:
            try:
                warehouse_id = self._get_default_warehouse_id()
            except ValueError as e:
                logger.error(f"Cannot list datasets without a warehouse: {e}")
                raise

        # Use SQL LIST command to list files
        sql_query = f"LIST '{full_path}'"
        logger.debug(f"Executing query: {sql_query}")

        try:
            result = self.client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=sql_query,
            )
        except Exception as e:
            logger.error(f"Failed to list files at '{full_path}': {e}")
            raise

        data = []
        if result.result and result.result.data_array:
            # LIST returns: path, name, size, modificationTime
            for row in result.result.data_array:
                path = row[0] if len(row) > 0 else None
                name = row[1] if len(row) > 1 else None
                file_size = row[2] if len(row) > 2 else None
                last_modified = row[3] if len(row) > 3 else None

                # Calculate relative path
                rel_path = None
                if path and path.startswith(location.url):
                    rel_path = path[len(location.url) :]
                    # ensure no leading slash if desired, or keep it.
                    # The original code did path.replace(location.url, "") which is risky if url appears elsewhere.
                    # Using slicing is safer if startsWith is true.
                elif path:
                    rel_path = path  # fallback

                data.append(
                    {
                        "path": rel_path,
                        "full_path": path,
                        "name": name,
                        "type": "directory" if name and name.endswith("/") else "file",
                        "last_modified": last_modified,
                        "file_size": file_size,
                    }
                )
        return data
