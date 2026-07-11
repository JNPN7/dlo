import logging

from dataclasses import dataclass, field
from enum import auto
from pathlib import Path
from typing import Optional

from deepagents import FilesystemPermission

from dlo.common.exception import errors
from dlo.common.schema import EnumBase, SchemaMixin
from dlo.core.config import Project
from dlo.core.constants import DEFAULT_AGENT_RECURSION_LIMIT

# Configure module logger
log = logging.getLogger(__name__)


class AgentMode(EnumBase):
    primary = auto()
    subagent = auto()


class AgentType(EnumBase):
    deepagent = auto()
    standard = auto()


@dataclass
class Agent(SchemaMixin):
    name: str = field()
    description: str = field()
    mode: AgentMode = field()
    model: str = field()
    prompt: str = field()
    agent_type: Optional[AgentType] = field(default=None)
    temperature: Optional[float] = field(default=None)
    permissions: list[FilesystemPermission] = field(default_factory=list)
    subagents: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    recursion_limit: int = field(default=DEFAULT_AGENT_RECURSION_LIMIT)

    base_dir: Optional[str] = field(default=None)

    def __post_init__(self):
        if self.base_dir and self.skills:
            self.skills = [(Path(self.base_dir) / Path(s)).as_posix() + "/" for s in self.skills]
        if self.agent_type is None:
            if self.subagents or self.permissions:
                self.agent_type = AgentType.deepagent
            else:
                self.agent_type = AgentType.standard


@dataclass
class AgentManifest(SchemaMixin):
    root_dir: Path
    base_dir: str
    agents: dict[str, Agent] = field(default_factory=dict)

    @classmethod
    def __from_project__(cls, project: Project):
        candidates = [
            (project.project_root_path / ".dlo", "/.dlo"),
            (project.project_root_path / ".opencode", "/.opencode"),
            (project.project_root_path / ".claude", "/.claude"),
        ]

        for path, base_dir in candidates:
            if path.exists():
                log.debug(f"Agent manifest loaded from directory: {path}")
                return cls(root_dir=path, base_dir=base_dir)

        raise errors.DloConfigError(
            "Agents configuration not found.\n"
            "Create .dlo or .opencode or .claude directory and add agents"
        )
