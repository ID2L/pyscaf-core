"""Tests for CLI factory and helpers."""

from pyscaf_core.actions import Action, ChoiceOption, CLIOption
from pyscaf_core.cli import build_cli, collect_cli_options, fill_default_context, set_option_default


class TestSetOptionDefault:
    def test_str_default(self):
        opt = CLIOption(name="--name", type="str", default="hello")
        assert set_option_default(opt) == "hello"

    def test_callable_default(self):
        opt = CLIOption(name="--name", type="str", default=lambda: "computed")
        assert set_option_default(opt) == "computed"

    def test_choice_default(self):
        opt = CLIOption(
            name="--tech",
            type="choice",
            default=0,
            choices=[
                ChoiceOption(key="py", display="Python", value="python"),
                ChoiceOption(key="js", display="JavaScript", value="javascript"),
            ],
        )
        assert set_option_default(opt) == "py"


class TestCollectCliOptions:
    def test_collects_in_dependency_order(self):
        class SetupAction(Action):
            depends: set[str] = set()
            cli_options = [CLIOption(name="--setup-opt")]

        class BuildAction(Action):
            depends = {"setup"}
            run_preferably_after = "setup"
            cli_options = [CLIOption(name="--build-opt")]

        opts = collect_cli_options(action_classes=[SetupAction, BuildAction])
        names = [o.name for o in opts]
        assert names.index("--setup-opt") < names.index("--build-opt")

    def test_empty_actions(self):
        opts = collect_cli_options(action_classes=[])
        assert opts == []


class TestFillDefaultContext:
    def test_fills_defaults(self):
        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(name="--name", type="str", default="world"),
                CLIOption(name="--count", type="int", default=42),
            ]

        context = fill_default_context({}, action_classes=[_TestAction])
        assert context["name"] == "world"
        assert context["count"] == 42

    def test_skips_when_visible_when_false(self):
        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(name="--always", type="str", default="yes"),
                CLIOption(name="--hidden", type="str", default="no", visible_when=lambda ctx: False),
            ]

        context = fill_default_context({}, action_classes=[_TestAction])
        assert context["always"] == "yes"
        assert "hidden" not in context

    def test_fills_when_visible_when_true(self):
        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(name="--visible", type="str", default="val", visible_when=lambda ctx: True),
            ]

        context = fill_default_context({}, action_classes=[_TestAction])
        assert context["visible"] == "val"


class TestBuildCli:
    def test_build_cli_creates_group(self):
        class _TestAction(Action):
            depends: set[str] = set()

        cli = build_cli("test-app", "1.0.0", action_classes=[_TestAction])
        assert cli.name == "cli"

        command_names = list(cli.commands.keys())
        assert "init" in command_names

    def test_build_cli_with_no_actions(self):
        cli = build_cli("test-app", "1.0.0", action_classes=[])
        assert "init" in cli.commands
