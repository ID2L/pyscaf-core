"""
Docs Starlight action: generates an Astro Starlight documentation site.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class DocsStarlightAction(Action):
    """Generates an Astro Starlight documentation site."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options: list = []

    def activate(self, context: dict) -> bool:
        apps = context.get("apps", [])
        if isinstance(apps, str):
            apps = [apps]
        return "docs" in apps or context.get("docs") is True

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        docs_dir = context.get("docs_dir", "apps/docs")
        project_name = context.get("project_name", "project")

        ctx = {"project_name": project_name}
        base = Path(docs_dir)

        return {
            base / "astro.config.mjs": _render_template(templates_dir, "astro.config.mjs.j2", ctx),
            base / "package.json": _render_template(templates_dir, "package.json.j2", ctx),
            base / "tsconfig.json": _render_template(templates_dir, "tsconfig.json.j2", ctx),
            base / "src" / "content" / "docs" / "index.mdx": _render_template(
                templates_dir, "content/index.mdx.j2", ctx
            ),
            base / "src" / "content" / "docs" / "guides": None,
            base / "public": None,
        }
