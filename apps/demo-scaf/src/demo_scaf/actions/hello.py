"""HelloAction — demonstrates skeleton creation and CLI options."""

from pathlib import Path

from pyscaf_core import Action, ChoiceOption, CLIOption


class HelloAction(Action):
    """Creates a greeting file in the project root."""

    depends: set[str] = set()
    cli_options = [
        CLIOption(
            name="--greeting",
            type="choice",
            help="Greeting style",
            default=0,
            prompt="Choose a greeting style",
            choices=[
                ChoiceOption(key="hello", display="Hello World (classic)", value="Hello, World!"),
                ChoiceOption(key="hi", display="Hi there (casual)", value="Hi there!"),
                ChoiceOption(key="hey", display="Hey (informal)", value="Hey!"),
            ],
        ),
        CLIOption(
            name="--author",
            type="str",
            help="Author name for the greeting",
            default="demo-user",
            prompt="Author name",
        ),
    ]

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        greeting_key = context.get("greeting", "hello")
        greeting_value = "Hello, World!"
        for choice in self.cli_options[0].choices:
            if choice.key == greeting_key:
                greeting_value = choice.value
                break

        author = context.get("author", "demo-user")
        project_name = context.get("project_name", "my-project")

        return {
            Path("HELLO.md"): f"# {greeting_value}\n\nProject: {project_name}\nAuthor: {author}\n",
            Path("src"): None,
        }

    def activate(self, context: dict) -> bool:
        return True
