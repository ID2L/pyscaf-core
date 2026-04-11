"""
PHP action: scaffolds a PHP project with PHPStan, Rector, PHP CS Fixer.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action, ChoiceOption, CLIOption


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class PhpAction(Action):
    """Scaffolds a PHP project with opinionated quality tooling."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--php-framework",
            type="choice",
            help="PHP framework",
            prompt="PHP framework",
            default=0,
            choices=[
                ChoiceOption(key="symfony", display="Symfony", value="symfony"),
                ChoiceOption(key="laravel", display="Laravel", value="laravel"),
                ChoiceOption(key="none", display="None (bare PHP)", value="none"),
            ],
        ),
        CLIOption(
            name="--symfony-addons",
            type="choice",
            help="Symfony addons",
            prompt="Symfony addons",
            default=0,
            multiple=True,
            choices=[
                ChoiceOption(key="api-platform", display="API Platform", value="api-platform"),
            ],
            visible_when=lambda ctx: ctx.get("php_framework") == "symfony",
        ),
    ]

    def activate(self, context: dict) -> bool:
        return context.get("backend_tech") == "php"

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        backend_dir = context.get("backend_dir", ".")
        project_name = context.get("project_name", "project")
        framework = context.get("php_framework", "none")
        addons = context.get("symfony_addons", [])
        if isinstance(addons, str):
            addons = [addons]

        ctx = {
            "project_name": project_name,
            "framework": framework,
            "addons": addons,
        }

        base_dir = Path(backend_dir) if backend_dir != "." else Path()

        result: dict[Path, str | None] = {
            base_dir / "composer.json": _render_template(templates_dir, "composer.json.j2", ctx),
            base_dir / "phpstan.neon": _render_template(templates_dir, "phpstan.neon.j2", ctx),
            base_dir / "rector.php": _render_template(templates_dir, "rector.php.j2", ctx),
            base_dir / ".php-cs-fixer.dist.php": _render_template(
                templates_dir, ".php-cs-fixer.dist.php.j2", ctx
            ),
            base_dir / "src": None,
            base_dir / "tests": None,
        }

        if framework == "symfony":
            result[base_dir / "src" / "Kernel.php"] = _render_template(
                templates_dir, "symfony/Kernel.php.j2", ctx
            )
            result[base_dir / "config"] = None
            result[base_dir / "public" / "index.php"] = _render_template(
                templates_dir, "symfony/index.php.j2", ctx
            )

        return result
