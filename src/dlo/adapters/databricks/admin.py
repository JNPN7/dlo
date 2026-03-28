from typing import Literal

from databricks.sdk import AccountClient, WorkspaceClient
from databricks.sdk.service.catalog import PermissionsChange, Privilege
from databricks.sdk.service.iam import (
    GrantRule,
    Patch,
    PatchOp,
    PatchSchema,
    RuleSetUpdateRequest,
    WorkspacePermission,
)


class DatabricksAdmin:
    """
    Handles administrative tasks for Databricks such as Service Account management,
    Schema creation, and Permission updates.
    """

    def __init__(self, client: WorkspaceClient):
        self.client = client
    
    def serverless_warehouse_create(self, name: str, *args, **kwargs):
        """Creates a serverless warehouse"""
        data = self.client.warehouses.create(name=name, *args, **kwargs)
        return data
    
    def serverless_warehouse_delete(self, id: str):
        """Delete existing serverless warehouse"""
        data = self.client.warehouses.delete(id=id)
        return data

    def service_account_create(self, name: str = ""):
        """Creates a new service principal."""
        data = self.client.service_principals_v2.create(active=True, display_name=name)
        return data
    
    def service_account_delete(self, id: str, account_config: dict):
        """Delete existing service principal."""
        account = AccountClient(**account_config)
        data = account.service_principals_v2.delete(id=id)
        return data

    def service_account_role_update(
        self,
        service_principal_id: int,
        service_principal_application_id: str,
        workspace_id: int,
        account_config: dict,
        role: Literal["USER", "ADMIN"] = "USER",
    ):
        """
        Updates the role of a service account in the workspace and account console.
        Requires Account Admin credentials in `account_config`.
        """
        account = AccountClient(**account_config)
        account.workspace_assignment.update(
            workspace_id, service_principal_id, permissions=[WorkspacePermission(role)]
        )

        # Updating access control of an account
        name = f"accounts/{account_config['account_id']}/servicePrincipals/{service_principal_application_id}/ruleSets/default"
        rule_set = account.access_control.get_rule_set(name=name, etag="")
        
        account.access_control.update_rule_set(
            name=name,
            rule_set=RuleSetUpdateRequest(
                name=name,
                etag=rule_set.etag,
                grant_rules=[
                    GrantRule(
                        role="roles/servicePrincipal.manager",
                        principals=[
                            f"servicePrincipals/{service_principal_application_id}"
                        ],
                    ),
                    GrantRule(
                        role="roles/servicePrincipal.user",
                        principals=[
                            f"servicePrincipals/{service_principal_application_id}"
                        ],
                    ),
                ],
            ),
        )

        # Updating the role of service account as account admin
        # TODO: Verify if this high privilege is always needed
        account.service_principals_v2.patch(
            id=str(service_principal_id),
            schemas=[PatchSchema.URN_IETF_PARAMS_SCIM_API_MESSAGES_2_0_PATCH_OP],
            operations=[
                Patch(op=PatchOp.ADD, path="roles", value=[{"value": "account_admin"}])
            ],
        )

    def permission_external_location_update(
        self, location_name: str, service_principal_id: str
    ):
        """Grant ALL_PRIVILEGES on an external location to a service principal."""
        self.client.grants.update(
            "external-location",
            location_name,
            changes=[
                PermissionsChange(
                    add=[Privilege.ALL_PRIVILEGES], principal=service_principal_id
                )
            ],
        )

    def service_account_secret_generate(
        self, service_principal_id: str, account_config: dict
    ):
        """Generates a secret for the service principal."""
        account = AccountClient(**account_config)
        data = account.service_principal_secrets.create(
            service_principal_id=service_principal_id
        )
        return data

    def schema_create(self, name: str, catalog_name: str):
        """Creates a new schema in the specified catalog."""
        self.client.schemas.create(name=name, catalog_name=catalog_name)

    def schema_grants(self, name: str, service_principal_id: str):
        """Grants ALL_PRIVILEGES on a schema to a service principal."""
        self.client.grants.update(
            "schema",
            name,
            changes=[
                PermissionsChange(
                    add=[Privilege.ALL_PRIVILEGES], principal=service_principal_id
                )
            ],
        )
