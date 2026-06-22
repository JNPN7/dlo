import shutil

from functools import cached_property
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from dlo.common.exception import errors

TEMPLATE_PATH = "dlo.templates"


# NOTE: Use copier if bootstrap project becomes complex
class InitProject:
    def __init__(self, project_name: str, profile: str, template: str):
        self.template = template
        self.project_name = project_name
        self.profile = profile
        self.target_dir = Path.cwd()

    @cached_property
    def template_root(self):
        return files(TEMPLATE_PATH).joinpath(self.template)

    def initalize(self):
        # Check if target_dir is empty
        if any(self.target_dir.iterdir()):
            raise errors.DloRuntimeError("Directory is not empty. It must be empty")

        # Intialize env for loading jinja templates
        env = Environment(loader=FileSystemLoader(self.template_root))

        context = {
            "project_name": self.project_name,
            "profile": self.profile,
        }

        # Iterate over all the template files
        for item in self.template_root.rglob("*"):
            relative_path = item.relative_to(self.template_root)
            output_path = self.target_dir / relative_path

            if item.is_dir():
                output_path.mkdir(parents=True, exist_ok=True)
                continue

            if item.suffix == ".jinja":
                template = env.get_template(relative_path.as_posix())
                output = template.render(context)

                # Remove jinja suffix
                output_path.with_suffix("").write_text(output)
                continue

            shutil.copy2(item, output_path)
