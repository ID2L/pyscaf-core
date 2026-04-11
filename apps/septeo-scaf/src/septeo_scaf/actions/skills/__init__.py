"""
Skills action: agent skills in .agents/skills/.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action


def _render_template(template_dir: Path, template_path: str, context: dict) -> str:
    """Render a Jinja2 template with the given context."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )
    template = env.get_template(template_path)
    return template.render(**context)


class SkillsAction(Action):
    """Skills action: generates base agent skills (tdd-methodology, spec-driven-dev)."""

    depends = {"agents"}
    run_preferably_after = "agents"
    cli_options: list = []

    def _get_templates_dir(self) -> Path:
        """Return the path to the templates directory."""
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """Create skills in .agents/skills/."""
        templates_dir = self._get_templates_dir()
        ctx = {"project_name": context.get("project_name", "project")}

        return {
            Path(
                ".agents/skills/tdd-methodology/SKILL.md"
            ): _render_template(
                templates_dir, "tdd-methodology/SKILL.md.j2", ctx
            ),
            Path(
                ".agents/skills/spec-driven-dev/SKILL.md"
            ): _render_template(
                templates_dir, "spec-driven-dev/SKILL.md.j2", ctx
            ),
        }
