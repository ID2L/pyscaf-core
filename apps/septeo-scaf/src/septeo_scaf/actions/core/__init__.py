"""
Core action: project structure layout with scope questions.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action, ChoiceOption, CLIOption


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )
    template = env.get_template(template_name)
    return template.render(**context)


def _apps_postfill_hook(context: dict) -> dict:
    """Compute convenience keys from apps + backend_tech selections."""
    apps = context.get("apps", [])
    if isinstance(apps, str):
        apps = [apps]
    context["apps"] = apps

    backend_tech = context.get("backend_tech", "none")
    project_type = context.get("project_type", "monorepo")

    context["has_python"] = backend_tech == "python"
    context["has_php"] = backend_tech == "php"
    context["has_javascript"] = (
        backend_tech == "typescript" or "frontend" in apps
    )

    if project_type == "monorepo":
        context["backend_dir"] = "apps/backend"
        context["frontend_dir"] = "apps/frontend"
        context["docs_dir"] = "apps/docs"
    else:
        context["backend_dir"] = "."
        context["frontend_dir"] = "."
        context["docs_dir"] = "docs"

    return context


class CoreAction(Action):
    """Root action: creates base project structure with scope questions."""

    depends: set[str] = set()
    cli_options = [
        CLIOption(
            name="--project-description",
            type="str",
            help="Project description",
            prompt="Describe your project briefly",
            default="",
        ),
        CLIOption(
            name="--project-type",
            type="choice",
            help="Project type",
            prompt="Project type",
            default=0,
            choices=[
                ChoiceOption(key="monorepo", display="Monorepo (apps + packages)", value="monorepo"),
                ChoiceOption(key="single", display="Single application", value="single"),
                ChoiceOption(key="library", display="Library", value="library"),
            ],
        ),
        CLIOption(
            name="--ide",
            type="choice",
            help="IDE",
            prompt="IDE",
            default=0,
            choices=[
                ChoiceOption(key="cursor", display="Cursor", value="cursor"),
                ChoiceOption(key="vscode", display="VS Code", value="vscode"),
                ChoiceOption(key="none", display="None", value="none"),
            ],
        ),
        CLIOption(
            name="--apps",
            type="choice",
            help="App slots (monorepo)",
            prompt="Which apps to include?",
            default=0,
            multiple=True,
            choices=[
                ChoiceOption(key="backend", display="Backend", value="backend"),
                ChoiceOption(key="frontend", display="Frontend", value="frontend"),
                ChoiceOption(key="docs", display="Documentation", value="docs"),
                ChoiceOption(key="mobile", display="Mobile", value="mobile"),
            ],
            visible_when=lambda ctx: ctx.get("project_type") == "monorepo",
            postfill_hook=_apps_postfill_hook,
        ),
        CLIOption(
            name="--backend-tech",
            type="choice",
            help="Backend technology",
            prompt="Backend technology",
            default=0,
            choices=[
                ChoiceOption(key="python", display="Python", value="python"),
                ChoiceOption(key="php", display="PHP", value="php"),
                ChoiceOption(key="typescript", display="TypeScript", value="typescript"),
                ChoiceOption(key="none", display="None", value="none"),
            ],
            visible_when=lambda ctx: (
                "backend" in ctx.get("apps", [])
                or ctx.get("project_type") in ("single", "library")
            ),
            postfill_hook=_apps_postfill_hook,
        ),
        CLIOption(
            name="--frontend-tech",
            type="choice",
            help="Frontend technology",
            prompt="Frontend technology",
            default=0,
            choices=[
                ChoiceOption(key="react", display="React", value="react"),
                ChoiceOption(key="vue", display="Vue", value="vue"),
                ChoiceOption(key="svelte", display="Svelte", value="svelte"),
            ],
            visible_when=lambda ctx: "frontend" in ctx.get("apps", []),
        ),
        CLIOption(
            name="--database",
            type="choice",
            help="Database",
            prompt="Database",
            default=0,
            choices=[
                ChoiceOption(key="postgres-18", display="PostgreSQL 18", value="postgres-18"),
                ChoiceOption(key="postgres-17", display="PostgreSQL 17", value="postgres-17"),
                ChoiceOption(key="mysql-8", display="MySQL 8", value="mysql-8"),
                ChoiceOption(key="none", display="None", value="none"),
            ],
            visible_when=lambda ctx: ctx.get("project_type") != "library",
        ),
        CLIOption(
            name="--docker",
            type="bool",
            help="Enable Docker",
            prompt="Docker for local development?",
            default=True,
            visible_when=lambda ctx: ctx.get("project_type") != "library",
        ),
        CLIOption(
            name="--docs",
            type="bool",
            help="Documentation site (Astro Starlight)",
            prompt="Documentation site?",
            default=True,
        ),
        CLIOption(
            name="--i18n",
            type="bool",
            help="Internationalization",
            prompt="Internationalization (i18n)?",
            default=True,
            visible_when=lambda ctx: ctx.get("project_type") != "library",
        ),
        CLIOption(
            name="--ci-cd",
            type="choice",
            help="CI/CD platform",
            prompt="CI/CD platform",
            default=0,
            choices=[
                ChoiceOption(key="bitbucket", display="Bitbucket Pipelines", value="bitbucket"),
                ChoiceOption(key="github", display="GitHub Actions", value="github"),
                ChoiceOption(key="none", display="None", value="none"),
            ],
        ),
        CLIOption(
            name="--serverless",
            type="bool",
            help="LocalStack for serverless",
            prompt="Serverless (LocalStack)?",
            default=False,
            visible_when=lambda ctx: (
                ctx.get("docker") is True
                and ctx.get("project_type") != "library"
            ),
        ),
    ]

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        project_type = context.get("project_type", "monorepo")
        apps = context.get("apps", [])
        if isinstance(apps, str):
            apps = [apps]

        ctx = {
            "project_name": context.get("project_name", "project"),
            "project_description": context.get("project_description", ""),
            "project_type": project_type,
        }

        skeleton: dict[Path, str | None] = {
            Path("AGENTS.md"): _render_template(templates_dir, "AGENTS.md.j2", ctx),
            Path("README.md"): _render_template(templates_dir, "README.md.j2", ctx),
            Path("Makefile"): _render_template(templates_dir, "Makefile.j2", ctx),
            Path("_todo.md"): _render_template(templates_dir, "_todo.md.j2", ctx),
            Path("specs"): None,
        }

        if project_type == "monorepo":
            skeleton[Path("apps")] = None
            skeleton[Path("packages")] = None
            for app in apps:
                skeleton[Path(f"apps/{app}")] = None
            if context.get("docs") and "docs" not in apps:
                skeleton[Path("apps/docs")] = None
        elif project_type == "single":
            skeleton[Path("src")] = None
        else:
            skeleton[Path("src")] = None
            skeleton[Path("docs")] = None

        return skeleton
