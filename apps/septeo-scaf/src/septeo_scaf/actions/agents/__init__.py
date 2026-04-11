"""
Agents action: .agents/ structure as vendor-neutral source of truth.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action

AIDD_RULE_CATEGORIES = [
    "00-architecture",
    "01-standards",
    "02-programming-languages",
    "03-frameworks-and-libraries",
    "04-tools-and-configurations",
    "05-workflows-and-processes",
    "06-templates-and-models",
    "07-quality-assurance",
    "08-domain-specific-rules",
    "09-other",
]


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    """Render a Jinja2 template with the given context."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )
    template = env.get_template(template_name)
    return template.render(**context)


class AgentsAction(Action):
    """Agents action: creates .agents/ structure (rules, skills, commands, mcp)."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options: list = []

    def _get_templates_dir(self) -> Path:
        """Return the path to the templates directory."""
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """Create .agents/ structure with 10 AIDD rule categories."""
        templates_dir = self._get_templates_dir()
        ctx = {"project_name": context.get("project_name", "project")}

        result: dict[Path, str | None] = {
            Path(".agents/rules"): None,
            Path(".agents/skills"): None,
            Path(".agents/commands"): None,
            Path(".agents/mcp"): None,
        }

        for category in AIDD_RULE_CATEGORIES:
            result[Path(f".agents/rules/{category}")] = None

        result[Path(".agents/rules/general.mdc")] = _render_template(
            templates_dir, "general.mdc.j2", ctx
        )

        return result
