"""CLI framework for pyscaf-core based applications."""

import sys
from typing import Any

import click
from rich.console import Console

from pyscaf_core.actions import (
    Action,
    CLIOption,
    cli_option_to_key,
    discover_actions_from_entry_points,
)
from pyscaf_core.actions.manager import ActionManager
from pyscaf_core.preference_chain import best_execution_order
from pyscaf_core.preference_chain.model import Node


def set_option_default(opt: CLIOption) -> Any:
    """Compute the default value for a CLI option."""
    if opt.type == "choice":
        default_index = opt.default
        if default_index is not None and opt.choices:
            return opt.choices[default_index].key
        return None
    return opt.default() if callable(opt.default) else opt.default


def collect_cli_options(
    action_classes: list[type[Action]] | None = None,
    discover: Any = None,
) -> list[CLIOption]:
    """Collect CLI options from all actions in dependency order.

    Args:
        action_classes: Explicit list of action classes
        discover: Callable returning action classes
    """
    if action_classes is not None:
        classes = action_classes
    elif discover is not None:
        classes = discover()
    else:
        classes = discover_actions_from_entry_points()

    deps: list[Node] = []
    action_class_by_id: dict[str, type[Action]] = {}
    for action_cls in classes:
        action_id = action_cls.__name__.replace("Action", "").lower()
        depends = getattr(action_cls, "depends", set())
        after = getattr(action_cls, "run_preferably_after", None)

        if depends and after is None:
            after = next(iter(depends))

        node = Node(id=action_id, depends=depends, after=after)
        deps.append(node)
        action_class_by_id[action_id] = action_cls

    if not deps:
        return []

    order = best_execution_order(deps)
    cli_options: list[CLIOption] = []
    for action_id in order:
        action_cls = action_class_by_id[action_id]
        cli_options.extend(getattr(action_cls, "cli_options", []))
    return cli_options


def fill_default_context(
    context: dict,
    action_classes: list[type[Action]] | None = None,
    discover: Any = None,
) -> dict:
    """Fill the context with default values from all actions."""
    if action_classes is not None:
        classes = action_classes
    elif discover is not None:
        classes = discover()
    else:
        classes = discover_actions_from_entry_points()

    for action_cls in classes:
        if hasattr(action_cls, "cli_options"):
            for opt in action_cls.cli_options:
                name = cli_option_to_key(opt)
                if name not in context or context[name] is None:
                    if opt.visible_when and not opt.visible_when(context):
                        continue
                    context[name] = set_option_default(opt)

    return context


def add_dynamic_options(
    command: click.Command,
    action_classes: list[type[Action]] | None = None,
    discover: Any = None,
) -> click.Command:
    """Add dynamic Click options from all actions to a command."""
    cli_options = collect_cli_options(action_classes=action_classes, discover=discover)
    for opt in reversed(cli_options):
        param_decls = [opt.name]
        click_opts: dict[str, Any] = {}
        if opt.type == "int":
            click_opts["type"] = int
        elif opt.type == "choice" and opt.choices:
            choice_keys = opt.get_choice_keys()
            click_opts["type"] = click.Choice(choice_keys, case_sensitive=False)
            if opt.multiple:
                click_opts["multiple"] = True
        elif opt.type == "str":
            click_opts["type"] = str
        elif opt.type == "bool":
            click_opts["type"] = click.BOOL
            click_opts["default"] = None
            base_name = opt.name.lstrip("-")
            param_decls[0] = f"--{base_name}/--no-{base_name}"

        if opt.help:
            click_opts["help"] = opt.help
        if opt.required:
            click_opts["required"] = True
        command = click.option(*param_decls, **click_opts)(command)
    return command


def build_cli(
    app_name: str,
    version: str,
    action_classes: list[type[Action]] | None = None,
    discover: Any = None,
) -> click.Group:
    """Build a complete Click CLI group for a pyscaf-core based application.

    Args:
        app_name: Name displayed in CLI help
        version: Version string for --version
        action_classes: Explicit list of action classes (mutually exclusive with discover)
        discover: Callable returning action classes (mutually exclusive with action_classes)

    Returns:
        A click.Group with an 'init' command wired to ActionManager
    """
    console = Console()

    def print_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
        if not value or ctx.resilient_parsing:
            return
        console.print(f"{app_name} version {version}")
        ctx.exit()

    @click.group()
    @click.version_option(
        version,
        "--version",
        "-V",
        callback=print_version,
        help="Show the version and exit.",
    )
    def cli() -> None:
        pass

    cli.help = f"{app_name} — project generator with plugin-based action system."

    @click.command()
    @click.argument("project_name")
    @click.option(
        "--interactive",
        is_flag=True,
        help="Enable interactive mode (asks questions to the user).",
    )
    @click.option("--no-install", is_flag=True, help="Skip installation step.")
    def init(project_name: str, interactive: bool, no_install: bool, **kwargs: Any) -> None:
        """Initialize a new customized project structure."""
        context = dict(kwargs)
        context["project_name"] = project_name
        context["interactive"] = interactive
        context["no_install"] = no_install

        if not interactive:
            context = fill_default_context(context, action_classes=action_classes, discover=discover)

        manager = ActionManager(project_name, context, action_classes=action_classes, discover=discover)
        context = manager.run_postfill_hooks(context)

        if interactive:
            context = manager.ask_interactive_questions(context)
        manager.context = context
        manager.create_project()

    init = add_dynamic_options(init, action_classes=action_classes, discover=discover)
    cli.add_command(init, "init")

    return cli


def make_main(cli_group: click.Group) -> Any:
    """Create a main() entry point from a CLI group."""

    def main() -> None:
        try:
            cli_group()
        except Exception as e:
            console = Console()
            console.print(f"[bold red]Error:[/bold red] {e!s}")
            sys.exit(1)

    return main
