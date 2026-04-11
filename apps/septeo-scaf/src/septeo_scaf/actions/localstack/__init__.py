"""
LocalStack action: adds serverless simulation to Docker Compose.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class LocalstackAction(Action):
    """Adds LocalStack to Docker Compose for serverless simulation."""

    depends = {"docker"}
    run_preferably_after = "docker"
    cli_options: list = []

    def activate(self, context: dict) -> bool:
        return context.get("serverless", False) is True

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        project_name = context.get("project_name", "project")
        ctx = {"project_name": project_name}

        return {
            Path(".docker/localstack/compose.localstack.yml"): _render_template(
                templates_dir, "compose.localstack.yml.j2", ctx
            ),
            Path(".docker/localstack/init/ready.d/init-aws.sh"): _render_template(
                templates_dir, "init-aws.sh.j2", ctx
            ),
        }

    def init(self, context: dict) -> None:
        init_script = self.project_path / ".docker/localstack/init/ready.d/init-aws.sh"
        if init_script.exists():
            init_script.chmod(0o755)
