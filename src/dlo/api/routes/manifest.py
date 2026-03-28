"""
Manifest API routes.

Single endpoint to serve the full manifest JSON.
All data operations (filtering, searching, stats) are handled in the UI.
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from dlo.api.deps.project import CProject
from dlo.core.models.manifest import Manifest

router = APIRouter(tags=["manifest"])


@router.get("/manifest")
async def get_manifest(project: CProject) -> dict[str, Any]:
    """
    Get the full manifest JSON.

    This is the only API endpoint - all data operations
    (filtering, searching, stats, graph building) are handled in the UI.
    """
    manifest = Manifest.__from_project__(project)

    if manifest is None:
        raise HTTPException(
            status_code=404,
            detail="Manifest not found. Run 'dlo compile' first to generate the manifest.",
        )

    return manifest.to_dict()
