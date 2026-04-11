"""
Environment config action: generates env.example with dynamic variables.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class EnvConfigAction(Action):
    """Generates env.example with variables matching selected services."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options: list = []

    def activate(self, context: dict) -> bool:
        return context.get("project_type") != "library"

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        ctx = {
            "project_name": context.get("project_name", "project"),
            "docker": context.get("docker", False),
            "database": context.get("database", "none"),
            "serverless": context.get("serverless", False),
            "has_python": context.get("has_python", False),
            "has_php": context.get("has_php", False),
            "has_javascript": context.get("has_javascript", False),
        }

        return {
            Path("env.example"): _render_template(templates_dir, "env.example.j2", ctx),
        }
