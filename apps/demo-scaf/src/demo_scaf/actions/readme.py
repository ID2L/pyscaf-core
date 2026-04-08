"""ReadmeAction — demonstrates dependency ordering and file appending."""

from pathlib import Path

from pyscaf_core import Action, CLIOption


class ReadmeAction(Action):
    """Creates a README.md with project info. Depends on HelloAction."""

    depends = {"hello"}
    run_preferably_after = "hello"
    cli_options = [
        CLIOption(
            name="--description",
            type="str",
            help="Short project description",
            default="A demo project scaffolded by demo-scaf",
            prompt="Project description",
        ),
        CLIOption(
            name="--add-license",
            type="bool",
            help="Add a license section to README",
            default=True,
            prompt="Add license section?",
        ),
    ]

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        project_name = context.get("project_name", "my-project")
        description = context.get("description", "A demo project scaffolded by demo-scaf")

        content = f"# {project_name}\n\n{description}\n"

        if context.get("add_license", True):
            content += "\n## License\n\nMIT\n"

        return {
            Path("README.md"): content,
        }

    def init(self, context: dict) -> None:
        pass

    def install(self, context: dict) -> None:
        pass
