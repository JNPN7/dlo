import functools

from typing import cast

import click

from dlo.core.config import Project


def project(func):
    @click.option("--project-root", "-p", type=str, help="Path to the DLO project configuration file.", default=".")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = args[0]

        ctx = cast("click.Context", ctx)
        ctx.obj = ctx.obj or {}

        project_root = kwargs.get("project_root")

        ctx.obj["project"] = Project(project_name="my_project", project_root=project_root)

        func(ctx, *args, **kwargs)
    return wrapper