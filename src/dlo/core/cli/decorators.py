import functools

from pathlib import Path
from typing import Literal, NewType, cast

import click

from dlo.common.logger import setup_logger
from dlo.core.config import Profile, Project
from dlo.core.constants import LOG_FILE

LogLevels = NewType("LogLevels", Literal["info", "error", "debug"])


def project(func):
    @click.option("--project-root", "-p", type=str, help="Path to the DLO project.", default=".")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = args[0]

        ctx = cast("click.Context", ctx)
        ctx.obj = ctx.obj or {}

        project_root = kwargs.get("project_root")

        ctx.obj["project"] = Project.__from_project_root__(project_root)

        func(ctx, *args, **kwargs)

    return wrapper


def lifespan(func):
    @click.option("--log-level", "-l", type=LogLevels, help="Log level", default="error")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        ctx = args[0]

        ctx = cast("click.Context", ctx)
        ctx.obj = ctx.obj or {}

        log_level = kwargs.get("log_level")
        ctx.obj["log_level"] = log_level

        project: Project = ctx.obj["project"]

        log_file = Path(project.project_root) / LOG_FILE
        setup_logger(level=log_level, log_file=log_file)

        func(ctx, *args, **kwargs)

    return wrapper


def profile(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = args[0]

        ctx = cast("click.Context", ctx)

        project: Project = ctx.obj["project"]
        ctx.obj["profile"] = Profile.__from_project__(project)

        func(ctx, *args, **kwargs)

    return wrapper


def cached_manifest(func):
    @click.option(
        "--cached-manifest",
        "-c",
        is_flag=True,
        help="Use cached complied manifest i.e. use complied manifest.json.",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = args[0]

        ctx = cast("click.Context", ctx)

        cached_manifest = kwargs.get("cached_manifest")
        ctx.obj["cached_manifest"] = cached_manifest

        func(ctx, *args, **kwargs)

    return wrapper
