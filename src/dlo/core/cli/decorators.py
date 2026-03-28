import functools

from typing import cast

import click

from dlo.core.config import Profile, Project


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


def profile(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = args[0]

        ctx = cast("click.Context", ctx)

        project: Project = ctx.obj["project"]
        ctx.obj["profile"] = Profile.__from_project__(project)

        func(ctx, *args, **kwargs)

    return wrapper
