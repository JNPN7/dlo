"""
Manifest API routes.

Single endpoint to serve the full manifest JSON.
All data operations (filtering, searching, stats) are handled in the UI.
"""

from typing import Any

from fastapi import APIRouter

from dlo.api.deps.project import CManifest

router = APIRouter(tags=["manifest"])


@router.get("/manifest")
async def get_manifest(manifest: CManifest) -> dict[str, Any]:
    """
    Get the full manifest JSON.

    This is the only API endpoint - all data operations
    (filtering, searching, stats, graph building) are handled in the UI.
    """
    return manifest.to_dict()
