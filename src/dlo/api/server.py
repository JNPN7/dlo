"""
DLO API Server.

FastAPI application that serves the manifest REST API and the React UI static files.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from dlo import __version__
from dlo.common.logger import setup_logger
from dlo.core.config import Project


class RegisterApp:
    def __init__(
        self,
        project: Project,
        log_level: str = "ERROR",
        log_file: Optional[str] = None,
        dev_mode: bool = False,
    ):
        """Register FastAPI App"""
        self._log_level = log_level
        self._log_file = log_file
        self._dev_mode = dev_mode
        self._project = project

        self._app = FastAPI(
            title="DLO API",
            description="Data Lineage Orchestrator API - Serves manifest data for the UI",
            version=__version__.version,
            docs_url="/api/docs",
            redoc_url="/api/redoc",
            openapi_url="/api/openapi.json",
            lifespan=self.lifespan,
            swagger_ui_parameters={
                "persistAuthorization": True,
            },
        )

        self.register_logger()
        self.register_middleware()
        self.register_router()
        self.register_additional_routes()
        self.register_ui()
        self.register_exception()

    @property
    def app(self) -> FastAPI:
        return self._app

    async def startup_event(self, app_instance: FastAPI):
        app_instance.state.project = self._project

    async def shutdown_event(self, app_instance: FastAPI): ...

    @asynccontextmanager
    async def lifespan(self, app_instance: FastAPI):
        await self.startup_event(app_instance)
        yield
        await self.shutdown_event(app_instance)

    def register_logger(self) -> None:
        """
        Register Logger
        """
        setup_logger(level=self._log_level, log_file=self._log_file)

    def register_middleware(self) -> None:
        """
        Register middleware (execution order from bottom to top)
        """
        # Add CORS middleware for development mode
        if self._dev_mode:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["http://localhost:6364", "http://127.0.0.1:6364"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        self.app.add_middleware(GZipMiddleware)

    def register_router(self):
        """
        Register app router
        """
        from dlo.api.routes import router

        self.app.include_router(router)

    def register_additional_routes(self):
        """
        Register routes for hygines like health
        """

        @self.app.get("/api/health")
        async def health_check():
            return {"status": "healthy", "service": "dlo-api"}

    def register_ui(self) -> None:
        """
        Register UI (serves Next.js static export in production mode)
        """
        if self._dev_mode:
            return

        # Next.js static export directory (out/)
        static_dir = Path(__file__).parent.parent / "ui" / "out"
        if not static_dir.exists():
            return

        # Mount static assets directory (_next/ contains JS, CSS chunks)
        next_static_dir = static_dir / "_next"
        if next_static_dir.exists():
            self.app.mount("/_next", StaticFiles(directory=str(next_static_dir)), name="_next")

        # Mount public assets directory
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            self.app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        # TODO: Next JS will not work as React and runtime cannot be attach to Fastapi
        # For prod mode make necessary changes
        @self.app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            # Skip API routes
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="API endpoint not found")

            # Try to find the corresponding HTML file for the route
            # Next.js static export creates HTML files for each route
            if full_path == "" or full_path == "/":
                html_path = static_dir / "index.html"
            else:
                # Remove trailing slash and try route-specific HTML
                clean_path = full_path.rstrip("/")
                html_path = static_dir / f"{clean_path}.html"

                # If not found, try directory with index.html (for trailing slash routes)
                if not html_path.exists():
                    html_path = static_dir / clean_path / "index.html"

                # Fall back to root index.html for client-side routing
                if not html_path.exists():
                    html_path = static_dir / "index.html"

            if not html_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail="UI not built. Run 'npm run build' in src/dlo/ui/ first.",
                )

            return FileResponse(str(html_path))

    def register_exception(self) -> None:
        """
        Register exception (Add here when required)
        """
