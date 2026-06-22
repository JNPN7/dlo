import logging
import os
import re

from functools import cached_property
from pathlib import Path
from typing import List, Optional

from dlo.common.exception import errors

# Configure module logger
log = logging.getLogger(__name__)


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

    def __init__(self, root_dir: str, ignore_patterns: Optional[list[str]] = None):
        """
        Initialize the file reader with the root directory path.

        Args:
            root_dir: The base directory path to scan for files. All file
                operations will be relative to this directory.

        Raises:
            None: This method does not raise exception during initialization.
        """
        log.debug("Initializing FileReaderFromFileSystem with root_dir: %s", root_dir)
        self.root_dir = root_dir
        self.ignore_patterns = list(ignore_patterns or [])

    @cached_property
    def files(self) -> List[str]:
        """
        Return the list of files in the root directory.

        This property provides lazy-loaded access to the file list. On first
        access, it triggers a directory scan

        Returns:
            List[str]: A list of absolute file paths found in the root directory.
        """
        log.debug("Scanning directory for files: %s", self.root_dir)
        _files: List[str] = []

        ignore_patterns = [re.compile(p) for p in self.ignore_patterns]

        # Walk through the directory structure and collect file paths
        for root, dirs, fs in os.walk(self.root_dir):
            # Exlude root dirs
            if root == self.root_dir:
                dirs[:] = [d for d in dirs if not any(p.search(d) for p in ignore_patterns)]

            for file in fs:
                file_path = os.path.join(root, file)
                _files.append(file_path)

        log.info("Completed file scan. Found %d files in %s", len(_files), self.root_dir)
        return _files

    @property
    def yaml_files(self) -> List[str]:
        """
        Filter the list of files to include only YAML files.

        Returns:
            List[str]: A list of file paths that have .yaml or .yml extensions.

        Example:
            >>> reader = FileReaderFromFileSystem("/project")
            >>> yaml_files = reader.filter_yaml_files()
        """
        yaml_files = [f for f in self.files if f.endswith((".yaml", ".yml"))]
        log.debug("Filtered %d YAML files from %d total files", len(yaml_files), len(self.files))
        return yaml_files

    @property
    def sql_files(self) -> List[str]:
        """
        Filter the list of files to include only SQL files.

        Returns:
            List[str]: A list of file paths that have .sql extension.

        Example:
            >>> reader = FileReaderFromFileSystem("/project")
            >>> sql_files = reader.filter_sql_files()
        """
        sql_files = [f for f in self.files if f.endswith(".sql")]
        log.debug("Filtered %d SQL files from %d total files", len(sql_files), len(self.files))
        return sql_files

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
        log.debug("Reading YAML file: %s", file_path)
        import yaml

        try:
            with open(file_path, "r") as stream:
                data: dict = yaml.safe_load(stream)
            log.debug("Successfully parsed YAML file: %s", file_path)
            return data
        except yaml.YAMLError as exc:
            log.error("Failed to parse YAML file %s: %s", file_path, exc)
            raise errors.DloParseError(
                message=f"Failed to parse YAML file '{file_path}': {exc}",
                data={"file": str(file_path), "error": str(exc)},
            )

    @staticmethod
    def read_markdown(file_path: str | Path):
        log.debug("Reading MD file: %s", file_path)
        import frontmatter

        try:
            with open(file_path, "r") as f:
                content = frontmatter.load(f)
            log.debug("Successfully parsed MD file: %s", file_path)
            return content
        except Exception as exc:
            log.error("Failed to parse MD file %s: %s", file_path, exc)
            raise errors.DloParseError(
                message=f"Failed to parse MD file '{file_path}': {exc}",
                data={"file": str(file_path), "error": str(exc)},
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
        log.debug("Reading file: %s", file_path)
        try:
            with open(file_path, "r") as f:
                content = f.read()
            log.debug("Successfully read file: %s (%d characters)", file_path, len(content))
            return content
        except Exception as exc:
            log.error("Failed to read file %s: %s", file_path, exc)
            raise errors.DloParseError(
                message=f"Failed to read file '{file_path}': {exc}",
                data={"file": str(file_path), "error": str(exc)},
            )
