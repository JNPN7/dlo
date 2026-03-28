"""
API Routes module.
"""

from fastapi import APIRouter

from dlo.api.routes.manifest import router as manifest_router

__all__ = ["manifest_router"]

router = APIRouter(prefix="/api")

router.include_router(manifest_router)
