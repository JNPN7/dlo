import contextvars

from dlo.core.config import Project
from dlo.core.models.manifest import Manifest

# 1. Declare the variable at module level
current_project: Project = contextvars.ContextVar("current_project", default=None)
current_manifest: Manifest = contextvars.ContextVar("current_manifest", default=None)
