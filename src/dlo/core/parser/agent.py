import logging

from functools import cached_property
from pathlib import Path

from dlo.common.exceptions import errors
from dlo.core.config import Project
from dlo.core.models.agent import Agent, AgentManifest
from dlo.core.parser.file_reader import FileReaderFromFileSystem

# Configure module logger
log = logging.getLogger(__name__)


class AgentManifestLoader:
    def __init__(self, project: Project):
        self.project = project
        self.agent_manifest = AgentManifest()

    @cached_property
    def root_dir(self) -> Path:
        candidates = [
            self.project.project_root_path / ".dlo",
            self.project.project_root_path / ".opencode",
            self.project.project_root_path / ".claude",
        ]

        for path in candidates:
            if path.exists():
                log.debug(f"Agent manifest loaded from directory: {path}")
                return path

        raise errors.DloConfigError(
            "Agents configuration not found.\n"
            "Create .dlo or .opencode or .claude directory and add agents"
        )

    @cached_property
    def agents_dir(self) -> Path:
        return self.root_dir / "agents"

    def load_agents(self) -> None:
        # Initialize file reader for the project root
        reader = FileReaderFromFileSystem(self.agents_dir)

        log.info(
            "Found %d files in project directory: %s", len(reader.files), self.project.project_root
        )
        # Iterate over all files and parse them based on their type
        parsed_count = 0

        for file in reader.files:
            file_path = Path(file)

            if file_path.suffix != ".md":
                continue

            try:
                data = reader.read_markdown(file_path)
                agent = Agent.from_dict({
                    "name": file_path.stem,
                    **data.metadata,
                    "prompt": data.content
                })
            except Exception as e:
                raise errors.DloCompilationError(
                    f"Error while parsing file {file_path.absolute().as_posix()}: {e}"
                ) from e

            self.agent_manifest.agents[agent.name] = agent

            parsed_count += 1

        log.info("Finished parsing agent files. Parsed: %d", parsed_count)

    def load(self) -> AgentManifest:
        log.info("Starting Agent load for project: %s", self.project.project_root)

        self.load_agents()

        log.debug("Final agents state: %s", self.agent_manifest)

        return self.agent_manifest
