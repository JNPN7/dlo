"""
Dashboards API routes.

Endpoint to serve Dashboard resources.
Charts are fetched separately using the charts API.
"""

from typing import Any

from fastapi import APIRouter

from dlo.api.deps.project import CManifest

router = APIRouter(tags=["dashboard"])


@router.get("/dashboards")
async def get_dashboards(manifest: CManifest) -> dict[str, Any]:
    """
    Get all dashboards present.
    Charts should be fetched separately using the /charts/{chart_uid} endpoint.
    """
    dashboards_json = {}

    for dashboard_name, dashboard in manifest.dashboards.items():
        d = dashboard.to_dict()
        dashboards_json[dashboard_name] = d

    return dashboards_json
