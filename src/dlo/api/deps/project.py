"""
Current Project Depends
"""
from typing import Annotated

from fastapi import Depends, Request

from dlo.core.config import Project


def get_current_project(request: Request) -> Project:
    return request.app.state.project


# Annotated Current Project
CProject = Annotated[Project, Depends(get_current_project)]
