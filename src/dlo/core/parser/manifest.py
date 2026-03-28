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
import os

from pathlib import Path
from typing import List, Optional

import yaml

from dlo.common.exceptions import errors
from dlo.core.config import Project
from dlo.core.models.manifest import Manifest
from dlo.core.models.resources import Resource

# Configure module logger
logger = logging.getLogger(__name__)


class FileReaderFromFileSystem:
    """
    Reads files from the file system and provides methods to filter and read files.

    This class provides utilities for traversing directory structures, filtering
    files by extension, and reading file contents. It supports both YAML and SQL
    file formats commonly used in DLO projects.

    Attributes:
        root_dir (str): The root directory path to scan for files.
        _files (Optional[List[str]]): Cached list of file paths, lazily loaded.

    Example:
        >>> reader = FileReaderFromFileSystem("/path/to/project")
        >>> yaml_files = reader.filter_yaml_files()
        >>> for file in yaml_files:
        ...     data = reader.read_yaml(file)
    """

    def __init__(self, root_dir: str) -> None:
        """
        Initialize the file reader with the root directory path.

        Args:
            root_dir: The base directory path to scan for files. All file
                operations will be relative to this directory.

        Raises:
            None: This method does not raise exceptions during initialization.
        """
        logger.debug("Initializing FileReaderFromFileSystem with root_dir: %s", root_dir)
        self.root_dir = root_dir
        self._files: Optional[List[str]] = None

    def get_files(self) -> None:
        """
        Retrieve all files from the root directory recursively.

        This method walks through the directory structure starting from the
        root directory and collects all file paths into the _files attribute.
        Hidden directories and files are included in the scan.

        Note:
            This method populates the internal _files cache. Use the `files`
            property for lazy-loaded access to the file list.
        """
        logger.debug("Scanning directory for files: %s", self.root_dir)
        _files: List[str] = []

        # Walk through the directory structure and collect file paths
        for root, _, fs in os.walk(self.root_dir):
            for file in fs:
                file_path = os.path.join(root, file)
                _files.append(file_path)
                logger.debug("Found file: %s", file_path)

        self._files = _files
        logger.info("Completed file scan. Found %d files in %s", len(_files), self.root_dir)

    @property
    def files(self) -> List[str]:
        """
        Return the list of files in the root directory.

        This property provides lazy-loaded access to the file list. On first
        access, it triggers a directory scan via get_files().

        Returns:
            List[str]: A list of absolute file paths found in the root directory.
        """
        if self._files is None:
            logger.debug("Files not yet loaded, triggering get_files()")
            self.get_files()
        return self._files  # type: ignore[return-value]

    @staticmethod
    def read_yaml(file_path: str | Path) -> dict:
        """
        Read a YAML file and return its contents as a dictionary.

        Args:
            file_path: The path to the YAML file to read. Can be either a
                string path or a Path object.

        Returns:
            dict: The parsed YAML content as a dictionary.

        Raises:
            errors.DloParseError: If the YAML file cannot be parsed due to
                syntax errors or other YAML-related issues.

        Example:
            >>> data = FileReaderFromFileSystem.read_yaml("config.yaml")
            >>> print(data["key"])
        """
        logger.debug("Reading YAML file: %s", file_path)
        try:
            with open(file_path, "r") as stream:
                data: dict = yaml.safe_load(stream)
            logger.debug("Successfully parsed YAML file: %s", file_path)
            return data
        except yaml.YAMLError as exc:
            logger.error("Failed to parse YAML file %s: %s", file_path, exc)
            raise errors.DloParseError(
                message=f"Failed to parse YAML file '{file_path}': {exc}",
                data={"file": str(file_path), "error": str(exc)}
            )

    @staticmethod
    def read_file(file_path: str | Path) -> str:
        """
        Read a file and return its contents as a string.

        Args:
            file_path: The path to the file to read. Can be either a string
                path or a Path object.

        Returns:
            str: The entire contents of the file as a string.

        Raises:
            errors.DloParseError: If the file cannot be read due to IO errors,
                permission issues, or if the file does not exist.

        Example:
            >>> sql_content = FileReaderFromFileSystem.read_file("query.sql")
            >>> print(sql_content)
        """
        logger.debug("Reading file: %s", file_path)
        try:
            with open(file_path, "r") as f:
                content = f.read()
            logger.debug("Successfully read file: %s (%d characters)", file_path, len(content))
            return content
        except Exception as exc:
            logger.error("Failed to read file %s: %s", file_path, exc)
            raise errors.DloParseError(
                message=f"Failed to read file '{file_path}': {exc}",
                data={"file": str(file_path), "error": str(exc)}
            )

    def filter_yaml_files(self) -> List[str]:
        """
        Filter the list of files to include only YAML files.

        Returns:
            List[str]: A list of file paths that have .yaml or .yml extensions.

        Example:
            >>> reader = FileReaderFromFileSystem("/project")
            >>> yaml_files = reader.filter_yaml_files()
        """
        yaml_files = [f for f in self.files if f.endswith((".yaml", ".yml"))]
        logger.debug("Filtered %d YAML files from %d total files", len(yaml_files), len(self.files))
        return yaml_files

    def filter_sql_files(self) -> List[str]:
        """
        Filter the list of files to include only SQL files.

        Returns:
            List[str]: A list of file paths that have .sql extension.

        Example:
            >>> reader = FileReaderFromFileSystem("/project")
            >>> sql_files = reader.filter_sql_files()
        """
        sql_files = [f for f in self.files if f.endswith(".sql")]
        logger.debug("Filtered %d SQL files from %d total files", len(sql_files), len(self.files))
        return sql_files


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

    def __init__(self, project: Project) -> None:
        """
        Initialize the ManifestLoader with a project configuration.

        Args:
            project: The Project object containing configuration details
                including the project root directory path.
        """
        logger.debug("Initializing ManifestLoader for project: %s", project.project_root)
        self.project = project
        self.manifest = Manifest()

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
        logger.info("Parsing YAML file: %s", file_path)
        data = FileReaderFromFileSystem.read_yaml(file_path)

        # Iterate over each resource type defined in the YAML file
        for resource_type, resource_data in data.items():
            logger.debug("Processing resource type: %s", resource_type)
            resource_model = Resource.get_resource(resource_type)

            # Skip unknown resource types
            if resource_model is None:
                logger.warning(
                    "Unknown resource type '%s' in file %s, skipping",
                    resource_type,
                    file_path
                )
                continue

            # Validate and add each resource to the manifest
            for d in resource_data:
                d["file_path"] = file_path.absolute().as_posix()
                validated_data = resource_model.from_dict(d)

                resource = getattr(self.manifest, resource_type)
                resource[validated_data.name] = validated_data
                logger.debug(
                    "Added resource '%s' of type '%s' to manifest",
                    validated_data.name,
                    resource_type
                )

        logger.info("Successfully parsed YAML file: %s", file_path)

    def parse_sql_file(self, file_path: Path) -> None:
        """
        Parse a SQL file and add its contents to the manifest.

        Args:
            file_path: The path to the SQL file to parse.

        Note:
            The SQL content is stored in the manifest keyed by the file path
            as a string for consistent key types.
        """
        logger.info("Parsing SQL file: %s", file_path)
        sql = FileReaderFromFileSystem.read_file(file_path)
        # Store SQL content using string path as key for consistency
        self.manifest.sql[str(file_path)] = sql
        logger.debug("Added SQL file to manifest: %s (%d characters)", file_path, len(sql))

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
            ".sql": self.parse_sql_file
        }

        parse_func = mapper.get(file_path.suffix)
        if parse_func is None:
            logger.debug("Skipping unsupported file type: %s", file_path)
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
        logger.info("Starting manifest load for project: %s", self.project.project_root)

        # Initialize file reader for the project root
        reader = FileReaderFromFileSystem(self.project.project_root)

        logger.info(
            "Found %d files in project directory: %s",
            len(reader.files),
            self.project.project_root
        )

        # Iterate over all files and parse them based on their type
        parsed_count = 0
        skipped_count = 0

        for file in reader.files:
            file_path = Path(file)

            # Check if file has a supported extension before parsing
            if file_path.suffix in (".yaml", ".yml", ".sql"):
                logger.debug("Parsing file: %s", file)
                self.parse_files(file_path)
                parsed_count += 1
            else:
                skipped_count += 1

        logger.info(
            "Finished parsing files. Parsed: %d, Skipped: %d",
            parsed_count,
            skipped_count
        )
        logger.debug("Final manifest state: %s", self.manifest)

        return self.manifest
