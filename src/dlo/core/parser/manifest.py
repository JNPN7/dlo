"""
Manifest Parser Module.

This module provides functionality for reading and parsing project files
(YAML and SQL) into a unified manifest structure. It handles file system
traversal, file filtering, and content parsing for the DLO project.

Classes:
    FileReaderFromFileSystem: Handles file system operations for reading project files.
    ManifestLoader: Orchestrates the parsing of project files into a manifest.
"""

import logging

from pathlib import Path

from dlo.common.exceptions import errors
from dlo.core.config import Project
from dlo.core.constants import PARSE_DIRECTORIES_IGNORE
from dlo.core.models.manifest import Manifest
from dlo.core.models.resources import Code, Model, Resource, ResourceTypes
from dlo.core.parser.file_reader import FileReaderFromFileSystem

# Configure module logger
log = logging.getLogger(__name__)


class ManifestLoader:
    """
    Load and parse project files into a unified manifest structure.

    This class orchestrates the parsing of YAML and SQL files from a DLO
    project directory into a Manifest object. It handles resource validation,
    type mapping, and manifest population.

    Attributes:
        project (Project): The project configuration containing project paths.
        manifest (Manifest): The manifest object to populate with parsed resources.

    Example:
        >>> project = Project(project_root="/path/to/project")
        >>> loader = ManifestLoader(project)
        >>> loader.load()
        >>> print(loader.manifest)
    """

    def __init__(self, project: Project):
        """
        Initialize the ManifestLoader with a project configuration.

        Args:
            project: The Project object containing configuration details
                including the project root directory path.
        """
        log.debug("Initializing ManifestLoader for project: %s", project.project_root)
        self.project = project
        self.manifest = Manifest()

    def _check_if_name_already_exists(
        self, file_path: Path, name: str, resource_type: ResourceTypes
    ):
        resources = getattr(self.manifest, resource_type)
        resource_of_name = resources.get(name)
        if resource_of_name is None:
            return

        raise errors.DloCompilationError(
            f"Found multiple models with name `{name}`.\n"
            "To fix this please change name for one these resource.\n"
            f"({file_path})\n"
            f"({resource_of_name.path})\n"
        )

    def parse_yaml_file(self, file_path: Path) -> None:
        """
        Parse a YAML file and populate the manifest with resources.

        This method reads a YAML file, identifies resource types defined within,
        validates each resource against its model, and adds them to the manifest.

        Args:
            file_path: The path to the YAML file to parse.

        Note:
            Unknown resource types are silently skipped. The file_path is added
            to each resource's metadata for traceability.

        Raises:
            errors.DloParseError: If the YAML file cannot be parsed.
            ValidationError: If a resource fails model validation.
        """
        log.info("Parsing YAML file: %s", file_path)
        try:
            data = FileReaderFromFileSystem.read_yaml(file_path) or {}
        except Exception as exc:
            raise errors.DloParseError(f"Failed to parse YAML file {file_path}") from exc

        file_path_str = file_path.absolute().as_posix()

        # Iterate over each resource type defined in the YAML file
        for resource_type, resource_data in data.items():
            log.debug("Processing resource type: %s", resource_type)
            resource_model = Resource.get_resource(resource_type)

            # Skip unknown resource types
            if resource_model is None:
                log.warning(
                    "Unknown resource type '%s' in file %s, skipping", resource_type, file_path
                )
                continue

            if not isinstance(resource_data, list):
                log.warning(
                    "Expected list for resource type '%s' in file %s, skipping",
                    resource_type,
                    file_path,
                )
                continue

            manifest_resource = getattr(self.manifest, resource_type)

            # Validate and add each resource to the manifest
            for raw_resource in resource_data:
                resource_dict = {**raw_resource, "file_path": file_path_str}
                try:
                    validated_data = resource_model.from_dict(resource_dict)
                except Exception as e:
                    raise errors.DloCompilationError(
                        f"Error while parsing file {file_path_str}: {e}"
                    ) from e

                # Handle Model-specific logic
                if resource_model is Model:
                    code = self.manifest.code.get(validated_data.name)
                    if code is None:
                        raise errors.DloCompilationError(
                            f"Sql file not found for model `{validated_data.name}`"
                        )
                    validated_data.raw_code = code.code
                    validated_data.code_path = code.path

                self._check_if_name_already_exists(
                    validated_data.file_path, validated_data.name, resource_type
                )

                manifest_resource[validated_data.unique_id] = validated_data

                log.debug(
                    "Added resource '%s' of type '%s' to manifest",
                    validated_data.name,
                    resource_type,
                )

        log.info("Successfully parsed YAML file: %s", file_path)

    def parse_sql_file(self, file_path: Path) -> None:
        """
        Parse a SQL file and add its contents to the manifest.

        Args:
            file_path: The path to the SQL file to parse.

        Note:
            The SQL content is stored in the manifest keyed by the file path
            as a string for consistent key types.
        """
        log.info("Parsing SQL file: %s", file_path)
        name = file_path.stem
        self._check_if_name_already_exists(file_path, name, ResourceTypes.code)

        sql = FileReaderFromFileSystem.read_file(file_path)
        absolute_file_path = file_path.absolute().as_posix()

        # Store SQL content using string path as key for consistency
        self.manifest.code[name] = Code(name=name, path=absolute_file_path, code=sql)

        log.debug("Added SQL file to manifest: %s (%d characters)", file_path, len(sql))

    def parse_files(self, file_path: Path) -> None:
        """
        Parse a file based on its extension.

        This method dispatches to the appropriate parser (YAML or SQL) based
        on the file's extension. Files with unsupported extensions are silently
        skipped.

        Args:
            file_path: The path to the file to parse.

        Note:
            Supported extensions: .yaml, .yml, .sql
            Other file types are ignored without logging.
        """
        # Map file extensions to their parser functions
        mapper = {
            ".yaml": self.parse_yaml_file,
            ".yml": self.parse_yaml_file,
            ".sql": self.parse_sql_file,
        }

        parse_func = mapper.get(file_path.suffix)
        if parse_func is None:
            log.debug("Skipping unsupported file type: %s", file_path)
            return

        parse_func(file_path)

    def load(self) -> Manifest:
        """
        Load and parse all project files into the manifest.

        This method initializes a file reader, scans the project directory,
        and parses all supported files (YAML and SQL) into the manifest.

        Returns:
            Manifest: The populated manifest object containing all parsed resources.

        Example:
            >>> loader = ManifestLoader(project)
            >>> manifest = loader.load()
            >>> print(f"Loaded {len(manifest.models)} models")
        """
        log.info("Starting manifest load for project: %s", self.project.project_root)

        # Initialize file reader for the project root
        reader = FileReaderFromFileSystem(self.project.project_root, PARSE_DIRECTORIES_IGNORE)

        log.info(
            "Found %d files in project directory: %s", len(reader.files), self.project.project_root
        )

        # Iterate over all files and parse them based on their type
        parsed_count = 0

        for file in reader.sql_files:
            file_path = Path(file)
            self.parse_files(file_path)
            parsed_count += 1

        for file in reader.files:
            file_path = Path(file)

            # Skipping as already read in first run
            if file_path.suffix in (".sql"):
                continue

            self.parse_files(file_path)

            parsed_count += 1

        log.info("Finished parsing files. Parsed: %d", parsed_count)
        log.debug("Final manifest state: %s", self.manifest)

        return self.manifest
