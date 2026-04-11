"""
Pipeline action: generates CI/CD pipeline configuration.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class PipelineAction(Action):
    """Generates CI/CD pipeline configuration for Bitbucket or GitHub."""

    depends = {"core", "git"}
    run_preferably_after = "git"
    cli_options: list = []

    def activate(self, context: dict) -> bool:
        return context.get("ci_cd", "none") not in ("none", None)

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        ci_cd = context.get("ci_cd", "bitbucket")
        project_name = context.get("project_name", "project")
        backend_tech = context.get("backend_tech", "none")

        ctx = {
            "project_name": project_name,
            "backend_tech": backend_tech,
            "has_python": context.get("has_python", False),
            "has_php": context.get("has_php", False),
            "has_javascript": context.get("has_javascript", False),
        }

        if ci_cd == "bitbucket":
            return {
                Path("bitbucket-pipelines.yml"): _render_template(
                    templates_dir, "bitbucket-pipelines.yml.j2", ctx
                ),
            }
        elif ci_cd == "github":
            return {
                Path(".github/workflows/ci.yml"): _render_template(
                    templates_dir, "github-ci.yml.j2", ctx
                ),
            }
        return {}
