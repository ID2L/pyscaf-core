"""
Git action: .gitignore and git init.
"""

import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action, ChoiceOption, CLIOption


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    """Render a Jinja2 template with the given context."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )
    template = env.get_template(template_name)
    return template.render(**context)


class GitAction(Action):
    """Git action: creates .gitignore and runs git init."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--git-hosting",
            type="choice",
            help="Git hosting provider",
            prompt="Git hosting",
            default=0,
            choices=[
                ChoiceOption(key="bitbucket", display="Bitbucket", value="bitbucket"),
                ChoiceOption(key="github", display="GitHub", value="github"),
            ],
        ),
    ]

    def _get_templates_dir(self) -> Path:
        """Return the path to the templates directory."""
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """Create .gitignore."""
        templates_dir = self._get_templates_dir()
        ctx = {"project_name": context.get("project_name", "project")}
        return {
            Path(".gitignore"): _render_template(templates_dir, ".gitignore.j2", ctx),
        }

    def install(self, context: dict) -> None:
        """Run git init in the project directory."""
        subprocess.run(
            ["git", "init"],
            cwd=self.project_path,
            check=True,
            capture_output=True,
        )
