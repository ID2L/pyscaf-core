"""
Python action: scaffolds a modern Python project with uv, ruff, pytest.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action, ChoiceOption, CLIOption


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class PythonAction(Action):
    """Scaffolds a Python project with opinionated quality tooling (uv, ruff, pytest)."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--python-framework",
            type="choice",
            help="Python backend framework",
            prompt="Python backend framework",
            default=0,
            choices=[
                ChoiceOption(key="fastapi", display="FastAPI", value="fastapi"),
                ChoiceOption(key="django", display="Django", value="django"),
                ChoiceOption(key="flask", display="Flask", value="flask"),
                ChoiceOption(key="none", display="None (bare Python)", value="none"),
            ],
            visible_when=lambda ctx: ctx.get("backend_tech") == "python",
        ),
    ]

    def activate(self, context: dict) -> bool:
        return context.get("backend_tech") == "python"

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        backend_dir = context.get("backend_dir", ".")
        project_name = context.get("project_name", "project")
        package_name = project_name.replace("-", "_").replace(" ", "_").lower()
        framework = context.get("python_framework", "none")

        ctx = {
            "project_name": project_name,
            "package_name": package_name,
            "framework": framework,
        }

        base_dir = Path(backend_dir) if backend_dir != "." else Path()

        result: dict[Path, str | None] = {
            base_dir / "pyproject.toml": _render_template(
                templates_dir, "pyproject.toml.j2", ctx
            ),
            base_dir / "src" / package_name / "__init__.py": (
                f'"""Package {package_name}."""\n'
            ),
        }

        if framework == "fastapi":
            result[base_dir / "src" / package_name / "main.py"] = _render_template(
                templates_dir, "fastapi/main.py.j2", ctx
            )
            result[base_dir / "src" / package_name / "routers"] = None
            result[base_dir / "src" / package_name / "models"] = None
        elif framework == "django":
            result[base_dir / "src" / package_name / "manage.py"] = _render_template(
                templates_dir, "django/manage.py.j2", ctx
            )
        elif framework == "flask":
            result[base_dir / "src" / package_name / "app.py"] = _render_template(
                templates_dir, "flask/app.py.j2", ctx
            )

        result[base_dir / "tests" / "__init__.py"] = ""

        return result
