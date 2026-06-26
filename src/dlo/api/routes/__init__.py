"""
API Routes module.
"""

from fastapi import APIRouter

from dlo.api.routes.charts import router as chart_router
from dlo.api.routes.dashboards import router as dashboard_router
from dlo.api.routes.manifest import router as manifest_router

router = APIRouter(prefix="/api")

router.include_router(manifest_router)
router.include_router(chart_router)
router.include_router(dashboard_router)
