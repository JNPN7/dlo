"""
Agent
"""

from functools import cached_property
from typing import Callable

from copilotkit import CopilotKitMiddleware
from deepagents import CompiledSubAgent, create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents import create_agent

from dlo.agents.llm import ChatModelFactory
from dlo.agents.tool import ToolRegistry
from dlo.common.exception import errors
from dlo.core.compiler.graph import Graph
from dlo.core.config import Profile, Project
from dlo.core.constants import COMPILED_GRAPH_FIG_PATH_AGENTS
from dlo.core.models.agent import Agent, AgentManifest, AgentMode


def get_weather(location: str):
    """Get weather for a location"""
    return f"The weather in {location} is sunny."


class AgentCompiler:
    def __init__(
        self,
        project: Project,
        profile: Profile,
        agent_manifest: AgentManifest,
        checkpointer,
    ):
        self.agent_manifest = agent_manifest
        self.profile = profile
        self.project = project
        self.compiled_agents = {}
        self.checkpointer = checkpointer

    @cached_property
    def graph(self) -> Graph:
        graph = Graph()

        agents_name = list(self.agent_manifest.agents.keys())
        agents = self.agent_manifest.agents.values()

        for agent in agents:
            graph.add_node(agent.name)

        # Check for missing subagents
        missing = [
            (agent.name, subagent)
            for agent in agents
            for subagent in agent.subagents
            if subagent not in agents_name
        ]
        if missing:
            details = ', '.join(f"`{sub}` (in `{agent}`)" for agent, sub in missing)
            raise errors.DloParseError(f"Subagents not found: {details}")

        graph.add_edges_from(
            (subagent, agent.name)
            for agent in agents
            for subagent in agent.subagents
        )
        return graph

    @cached_property
    def primary_agents(self) -> list[str]:
        return [
            agent.name for agent in self.agent_manifest.agents.values()
            if agent.mode == AgentMode.primary
        ]

    def draw_layer(self) -> None:
        graph = self.graph
        figure_name = self.project.project_root_path / COMPILED_GRAPH_FIG_PATH_AGENTS

        graph.draw_layer(nodes=self.agent_manifest.agents, figure_name=figure_name)

    def get_model(self, agent: Agent):
        model_provider, model = agent.model.split("/")

        provider = self.profile.providers.get(model_provider)
        if provider is None:
            raise errors.DloParseError(f"Provider `{model_provider}` not found in the profile")

        config = {
            **provider.config,
            "provider": provider.provider,
            "model": model,
            "temperature": agent.temperature,
        }
        return ChatModelFactory.create(**config)

    def get_tools(self, agent: Agent):
        tools = agent.tools
        return [ToolRegistry.get(tool) for tool in tools]

    async def create_agent(self, agent: Agent):
        async def create_primary(agent: Agent):
            # path = Path(f"checkpoint/{agent.name}/checkpoint.sqlite")
            # path.parent.mkdir(exist_ok=True)
            # checkpointer_context = AsyncSqliteSaver.from_conn_string(
            #     path
            # )
            # checkpointer = await checkpointer_context.__aenter__()

            model = self.get_model(agent)

            return create_deep_agent(
                model=model,
                middleware=[CopilotKitMiddleware()],  # for frontend tools and context
                system_prompt=agent.prompt,
                tools=self.get_tools(agent),
                checkpointer=self.checkpointer,
                subagents=[self.compiled_agents[sub] for sub in agent.subagents],
                permissions=agent.permissions,
                backend=FilesystemBackend(
                    root_dir=self.project.project_root_path, virtual_mode=True
                ),
                skills=agent.skills,
            )

        async def create_subagent(agent: Agent):
            if agent.subagents or agent.permissions:
                custom_graph = await create_primary(agent)
            else:
                model = self.get_model(agent)
                custom_graph = create_agent(
                    model=model,
                    system_prompt=agent.prompt,
                    tools=self.get_tools(agent),
                )

            # Use it as a custom subagent
            return CompiledSubAgent(
                name=agent.name,
                description=agent.description,
                runnable=custom_graph
            )

        agent_map: dict[AgentMode, Callable] = {
            AgentMode.primary: create_primary,
            AgentMode.subagent: create_subagent,
        }

        return await agent_map[agent.mode](agent)

    async def compile_agent(self, agent_name: str) -> None:
        agent = self.agent_manifest.agents[agent_name]

        compiled_agent = await self.create_agent(agent)

        self.compiled_agents[agent_name] = compiled_agent

    async def compile(self) -> None:
        self.draw_layer()

        for agent_name in self.graph.topoligical_sort:
            await self.compile_agent(agent_name)

    @classmethod
    def agent(self, checkpointer):
        import json
        import os

        AGENT_CONFIG_TEMP = json.loads(os.environ.get("AGENT_CONFIG_TEMP", "{}"))
        config = {
            **AGENT_CONFIG_TEMP,
        }

        model = ChatModelFactory.create(**config)
        return create_deep_agent(
            model=model,
            tools=[get_weather],
            middleware=[CopilotKitMiddleware()],  # for frontend tools and context
            system_prompt="You are a helpful research assistant.",
            checkpointer=checkpointer,
        )
