"""
i18n action: configures per-ecosystem internationalization.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action, ChoiceOption, CLIOption


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class I18nAction(Action):
    """Configures i18n for each detected ecosystem."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--i18n-languages",
            type="choice",
            help="i18n languages",
            prompt="Additional languages (English always included)",
            default=0,
            multiple=True,
            choices=[
                ChoiceOption(key="fr", display="French", value="fr"),
                ChoiceOption(key="es", display="Spanish", value="es"),
                ChoiceOption(key="de", display="German", value="de"),
            ],
            visible_when=lambda ctx: ctx.get("i18n") is True,
        ),
    ]

    def activate(self, context: dict) -> bool:
        return (
            context.get("i18n") is True
            and context.get("project_type") != "library"
        )

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        project_name = context.get("project_name", "project")
        apps = context.get("apps", [])
        if isinstance(apps, str):
            apps = [apps]
        frontend_dir = context.get("frontend_dir", "apps/frontend")
        backend_dir = context.get("backend_dir", "apps/backend")
        has_javascript = context.get("has_javascript", False) or "frontend" in apps
        has_python = context.get("has_python", False)
        has_php = context.get("has_php", False)

        languages = ["en"]
        extra_langs = context.get("i18n_languages", ["fr"])
        if isinstance(extra_langs, str):
            extra_langs = [extra_langs]
        for lang in extra_langs:
            if lang not in languages:
                languages.append(lang)
        if "fr" not in languages:
            languages.append("fr")

        ctx = {
            "project_name": project_name,
            "languages": languages,
        }

        result: dict[Path, str | None] = {}

        if has_javascript and "frontend" in apps:
            base = Path(frontend_dir)
            result[base / "src" / "i18n.ts"] = _render_template(
                templates_dir, "i18n.ts.j2", ctx
            )
            for lang in languages:
                result[base / "public" / "locales" / lang / "common.json"] = (
                    _render_template(
                        templates_dir,
                        "common.json.j2",
                        {**ctx, "lang": lang},
                    )
                )

        if has_python:
            base = Path(backend_dir)
            result[base / "babel.cfg"] = _render_template(
                templates_dir, "babel.cfg.j2", ctx
            )
            for lang in languages:
                result[base / "locales" / lang / "LC_MESSAGES"] = None

        if has_php:
            base = Path(backend_dir)
            for lang in languages:
                result[base / "translations" / f"messages.{lang}.yaml"] = (
                    _render_template(
                        templates_dir,
                        "messages.yaml.j2",
                        {**ctx, "lang": lang},
                    )
                )

        return result
