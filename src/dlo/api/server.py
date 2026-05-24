"""
DLO API Server.

FastAPI application that serves the manifest REST API and the React UI static files.
"""

import copy
import os

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from dlo import __version__
from dlo.api.contexts import current_manifest, current_project
from dlo.common.logger import setup_logger
from dlo.core.config import Profile, Project
from dlo.core.models.agent import AgentManifest
from dlo.core.models.manifest import Manifest


class RegisterApp:
    def __init__(
        self,
        project: Project,
        profile: Profile,
        agent_manifest: Optional[AgentManifest] = None,
        log_level: str = "ERROR",
        log_file: Optional[str] = None,
        dev_mode: bool = False,
    ):
        """Register FastAPI App"""
        self._log_level = log_level
        self._log_file = log_file
        self._dev_mode = dev_mode
        self._project = project
        self._profile = profile
        self._agent_manifest = agent_manifest

        # Used for agents
        self.checkpointer = None
        self.checkpointer_context = None

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
        """App startup events"""
        app_instance.state.project = self._project

        if self._agent_manifest is not None:
            path = Path("checkpoint/checkpoint.sqlite")
            path.parent.mkdir(exist_ok=True)

            self.checkpointer_context = AsyncSqliteSaver.from_conn_string(
                path
            )
            self.checkpointer = await self.checkpointer_context.__aenter__()

            # Reqired here as we need to register agents after intializing the checkpointer
            await self.register_agent()
        else:
            @self.app.get("/api/agents")
            async def list_agents():
                return []

    async def shutdown_event(self, app_instance: FastAPI):
        """App shutdown events"""
        if self.checkpointer_context is not None:
            await self.checkpointer_context.__aexit__(None, None, None)

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

        # Add middleware to set project context for each request
        @self.app.middleware("http")
        async def set_project_context(request: Request, call_next):
            current_project.set(copy.deepcopy(self._project))
            current_manifest.set(Manifest.__from_project__(self._project))

            response = await call_next(request)

            return response

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

    def agent_callback(self) -> list:
        callbacks = []
        langfuse_callback = None

        langfuse_secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
        langfuse_public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
        langfuse_base_url = os.environ.get("LANGFUSE_BASE_URL")
        langfuse_environment = os.environ.get("LANGFUSE_ENVIRONMENT", "")
        if langfuse_secret_key is not None:
            from langfuse import Langfuse
            from langfuse.langchain import CallbackHandler
            Langfuse(
                secret_key=langfuse_secret_key,
                public_key=langfuse_public_key,
                environment=langfuse_environment,
                base_url=langfuse_base_url,
            )
            langfuse_callback = CallbackHandler()

        if langfuse_callback is not None:
            callbacks.append(langfuse_callback)

        return callbacks

    async def register_agent(self) -> None:
        """
        Register agents
        """
        from ag_ui_langgraph import add_langgraph_fastapi_endpoint
        from copilotkit import LangGraphAGUIAgent

        from dlo.agents.agent import AgentCompiler

        agent_compiler = AgentCompiler(
            project=self._project,
            profile=self._profile,
            agent_manifest=self._agent_manifest,
            checkpointer=self.checkpointer,
        )
        await agent_compiler.compile()

        callbacks = self.agent_callback()

        for agent_name in agent_compiler.primary_agents:
            compiled_agent = agent_compiler.compiled_agents[agent_name]
            agent = agent_compiler.agent_manifest.agents[agent_name]

            add_langgraph_fastapi_endpoint(
                app=self.app,
                agent=LangGraphAGUIAgent(
                    name=agent.name,
                    description=agent.description,
                    graph=compiled_agent,
                    config={"callbacks": callbacks},
                ),
                path=f"/api/agents/{agent.name}",
            )

        @self.app.get("/api/agents")
        async def list_agents():
            return agent_compiler.primary_agents

        @self.app.get("/api/agents-manifest")
        async def agent_manifest():
            return self._agent_manifest

        # agent = AgentCompiler().agent(checkpointer=self.checkpointer)
        #
        # callbacks = self.agent_callback()
        #
        # add_langgraph_fastapi_endpoint(
        #     app=self.app,
        #     agent=LangGraphAGUIAgent(
        #         name="analytics_agent",
        #         description="Analytics agent that have access to phone data",
        #         graph=agent,
        #         config={"callbacks": callbacks},
        #     ),
        #     path="/api/agents/test",
        # )
