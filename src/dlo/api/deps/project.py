"""
Current Project Depends
"""

from typing import Annotated

from fastapi import Depends, Request

from dlo.common.exception import errors
from dlo.core.compiler.runtime import Runtime
from dlo.core.config import Profile, Project
from dlo.core.models.manifest import Manifest


def get_current_project(request: Request) -> Project:
    return request.app.state.project


# Annotated Current Project
CProject = Annotated[Project, Depends(get_current_project)]


def get_current_profile(request: Request) -> Profile:
    return request.app.state.profile


# Annotated Current Profile
CProfile = Annotated[Profile, Depends(get_current_profile)]


def get_project_manifest(project: CProject):
    manifest = Manifest.__from_project__(project)
    if manifest is None:
        raise errors.NotFoundError(
            "Manifest not found. Run 'dlo compile' first to generate the manifest."
        )

    return manifest


# Annotated Current Manifest
CManifest = Annotated[Manifest, Depends(get_project_manifest)]


# FIXME: have added manifest need to think about compiling when new changes happens
def get_runner(project: CProject, profile: CProfile, manifest: CManifest):
    return Runtime(project=project, profile=profile, manifest=manifest)


# Annotated Current Manifest
CRuntime = Annotated[Runtime, Depends(get_runner)]


