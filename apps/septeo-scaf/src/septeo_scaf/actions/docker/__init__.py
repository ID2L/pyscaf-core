"""
Docker action: generates compose.yml, Dockerfiles, and .dockerignore.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class DockerAction(Action):
    """Generates Docker Compose, Dockerfiles, and .dockerignore."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options: list = []

    def activate(self, context: dict) -> bool:
        return (
            context.get("docker") is True
            and context.get("project_type") != "library"
        )

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        apps = context.get("apps", [])
        if isinstance(apps, str):
            apps = [apps]
        backend_tech = context.get("backend_tech", "none")
        frontend_tech = context.get("frontend_tech", "none")
        project_name = context.get("project_name", "project")
        database = context.get("database", "none")
        project_type = context.get("project_type", "monorepo")

        services = []
        if "backend" in apps and backend_tech != "none":
            services.append({
                "name": "backend",
                "tech": backend_tech,
                "dir": "apps/backend" if project_type == "monorepo" else ".",
                "port": 8000,
            })
        if "frontend" in apps:
            services.append({
                "name": "frontend",
                "tech": "node",
                "dir": "apps/frontend" if project_type == "monorepo" else ".",
                "port": 3000,
            })
        if "docs" in apps or context.get("docs"):
            services.append({
                "name": "docs",
                "tech": "node",
                "dir": "apps/docs" if project_type == "monorepo" else "docs",
                "port": 4321,
            })

        ctx = {
            "project_name": project_name,
            "services": services,
            "database": database,
            "backend_tech": backend_tech,
            "frontend_tech": frontend_tech,
            "has_python": context.get("has_python", False),
            "has_php": context.get("has_php", False),
            "has_javascript": context.get("has_javascript", False),
            "serverless": context.get("serverless", False),
        }

        result: dict[Path, str | None] = {
            Path("compose.yml"): _render_template(templates_dir, "compose.yml.j2", ctx),
            Path(".dockerignore"): _render_template(templates_dir, "dockerignore.j2", ctx),
        }

        for svc in services:
            tech = svc["tech"]
            dockerfile_template = f"dockerfiles/Dockerfile.{tech}.j2"
            result[Path(f".docker/{svc['name']}/Dockerfile")] = _render_template(
                templates_dir, dockerfile_template, {**ctx, "service": svc}
            )

        return result
