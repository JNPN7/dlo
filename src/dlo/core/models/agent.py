from dataclasses import dataclass, field
from enum import auto
from typing import Optional

from dlo.common.schema import EnumBase, SchemaMixin


class AgentMode(EnumBase):
    primary = auto()
    subagent = auto()


class Permission:
    ...


@dataclass
class Agent(SchemaMixin):
    name: str = field()
    description: str = field()
    mode: AgentMode = field()
    model: str = field()
    prompt: str = field()
    temperature: Optional[float] = field(default=None)
    permission: dict[str, str] = field(default_factory=dict)
    subagents: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


@dataclass
class AgentManifest():
    agents: dict[str, Agent] = field(default_factory=dict)
