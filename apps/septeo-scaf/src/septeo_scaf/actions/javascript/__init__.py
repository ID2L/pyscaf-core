"""
JavaScript/TypeScript action: scaffolds JS/TS with bun, Vite, ESLint, Prettier, Vitest.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class JavascriptAction(Action):
    """Scaffolds a JS/TS project with opinionated quality tooling."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options: list = []

    def activate(self, context: dict) -> bool:
        apps = context.get("apps", [])
        if isinstance(apps, str):
            apps = [apps]
        return (
            context.get("backend_tech") == "typescript"
            or "frontend" in apps
        )

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        frontend_dir = context.get("frontend_dir", "apps/frontend")
        project_name = context.get("project_name", "project")
        frontend_tech = context.get("frontend_tech", "react")
        apps = context.get("apps", [])
        if isinstance(apps, str):
            apps = [apps]

        result: dict[Path, str | None] = {}

        if "frontend" in apps:
            base = Path(frontend_dir) if frontend_dir != "." else Path()
            ctx = {
                "project_name": project_name,
                "frontend_tech": frontend_tech,
            }

            result[base / "package.json"] = _render_template(templates_dir, "package.json.j2", ctx)
            result[base / "tsconfig.json"] = _render_template(templates_dir, "tsconfig.json.j2", ctx)
            result[base / "vite.config.ts"] = _render_template(templates_dir, "vite.config.ts.j2", ctx)
            result[base / ".prettierrc"] = _render_template(templates_dir, "prettierrc.j2", ctx)
            result[base / "eslint.config.js"] = _render_template(templates_dir, "eslint.config.js.j2", ctx)

            if frontend_tech == "react":
                result[base / "src" / "App.tsx"] = _render_template(templates_dir, "react/App.tsx.j2", ctx)
                result[base / "src" / "main.tsx"] = _render_template(templates_dir, "react/main.tsx.j2", ctx)
                result[base / "index.html"] = _render_template(templates_dir, "react/index.html.j2", ctx)
            elif frontend_tech == "vue":
                result[base / "src" / "App.vue"] = _render_template(templates_dir, "vue/App.vue.j2", ctx)
                result[base / "src" / "main.ts"] = _render_template(templates_dir, "vue/main.ts.j2", ctx)
                result[base / "index.html"] = _render_template(templates_dir, "vue/index.html.j2", ctx)
            elif frontend_tech == "svelte":
                result[base / "src" / "App.svelte"] = _render_template(templates_dir, "svelte/App.svelte.j2", ctx)
                result[base / "src" / "main.ts"] = _render_template(templates_dir, "svelte/main.ts.j2", ctx)
                result[base / "index.html"] = _render_template(templates_dir, "svelte/index.html.j2", ctx)

        return result
