"""
Rules action: AIDD rules in .agents/rules/ based on project context.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action, ChoiceOption, CLIOption


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    """Render a Jinja2 template with the given context."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )
    template = env.get_template(template_name)
    return template.render(**context)


class RulesAction(Action):
    """Rules action: generates AIDD rules based on languages and frameworks."""

    depends = {"agents"}
    run_preferably_after = "agents"
    cli_options = [
        CLIOption(
            name="--languages",
            type="choice",
            help="Programming languages",
            prompt="Select languages",
            default=0,
            multiple=True,
            choices=[
                ChoiceOption(key="python", display="Python", value="python"),
                ChoiceOption(key="typescript", display="TypeScript", value="typescript"),
            ],
        ),
    ]

    def _get_templates_dir(self) -> Path:
        """Return the path to the templates directory."""
        return Path(__file__).parent / "templates"

    def _get_languages(self, context: dict) -> list[str]:
        """Extract languages from context as a list."""
        raw = context.get("languages")
        if raw is None:
            return []
        if isinstance(raw, (list, tuple)):
            return list(raw)
        return [raw] if raw else []

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """Generate rules in .agents/rules/ based on context."""
        templates_dir = self._get_templates_dir()
        ctx = {"project_name": context.get("project_name", "project")}
        languages = self._get_languages(context)

        result: dict[Path, str | None] = {
            Path(".agents/rules/01-standards/1-clean-code.mdc"): _render_template(
                templates_dir, "1-clean-code.mdc.j2", ctx
            ),
            Path(".agents/rules/01-standards/1-naming.mdc"): _render_template(
                templates_dir, "1-naming.mdc.j2", ctx
            ),
            Path(
                ".agents/rules/04-tools-and-configurations/4-git.mdc"
            ): _render_template(templates_dir, "4-git.mdc.j2", ctx),
            Path(
                ".agents/rules/05-workflows-and-processes/5-spec-driven-dev.mdc"
            ): _render_template(templates_dir, "05-spec-driven-dev.mdc.j2", ctx),
            Path(
                ".agents/rules/07-quality-assurance/7-testing.mdc"
            ): _render_template(templates_dir, "07-testing.mdc.j2", ctx),
        }

        if "python" in languages:
            result[
                Path(".agents/rules/02-programming-languages/2-python@3.12.mdc")
            ] = _render_template(templates_dir, "2-python@3.12.mdc.j2", ctx)

        if "typescript" in languages:
            result[
                Path(".agents/rules/02-programming-languages/2-typescript.mdc")
            ] = _render_template(templates_dir, "2-typescript.mdc.j2", ctx)

        return result
