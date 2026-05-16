"""Tests for ActionManager."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from pyscaf_core.actions import Action, ChoiceOption, CLIOption
from pyscaf_core.actions.manager import ActionManager, _is_unanswered


class TestIsUnanswered:
    def test_none_is_unanswered(self):
        assert _is_unanswered(None) is True

    def test_empty_tuple_is_unanswered(self):
        assert _is_unanswered(()) is True

    def test_empty_list_is_unanswered(self):
        assert _is_unanswered([]) is True

    def test_nonempty_tuple_is_answered(self):
        assert _is_unanswered(("a",)) is False

    def test_nonempty_list_is_answered(self):
        assert _is_unanswered(["a"]) is False

    def test_string_is_answered(self):
        assert _is_unanswered("hello") is False

    def test_false_is_answered(self):
        assert _is_unanswered(False) is False

    def test_zero_is_answered(self):
        assert _is_unanswered(0) is False


class TestActionManagerOrdering:
    def test_orders_actions_by_dependency(self):
        class SetupAction(Action):
            depends: set[str] = set()

        class BuildAction(Action):
            depends = {"setup"}
            run_preferably_after = "setup"

        manager = ActionManager("test", {}, action_classes=[BuildAction, SetupAction])
        names = [a.__class__.__name__ for a in manager.actions]
        assert names.index("SetupAction") < names.index("BuildAction")

    def test_handles_empty_actions(self):
        manager = ActionManager("test", {}, action_classes=[])
        assert manager.actions == []


class TestActionManagerPostfillHooks:
    def test_runs_postfill_hooks(self):
        def my_hook(ctx):
            ctx["derived"] = ctx.get("source", "") + "_derived"
            return ctx

        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(name="--source", type="str", postfill_hook=my_hook),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        context = manager.run_postfill_hooks({"source": "val"})
        assert context["derived"] == "val_derived"

    def test_skips_postfill_when_visible_when_false(self):
        hook_called = []

        def my_hook(ctx):
            hook_called.append(True)
            return ctx

        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(
                    name="--hidden",
                    type="str",
                    postfill_hook=my_hook,
                    visible_when=lambda ctx: False,
                ),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        manager.run_postfill_hooks({"hidden": "value"})
        assert not hook_called

    def test_runs_postfill_when_visible_when_true(self):
        def my_hook(ctx):
            ctx["hook_ran"] = True
            return ctx

        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(
                    name="--visible",
                    type="str",
                    postfill_hook=my_hook,
                    visible_when=lambda ctx: True,
                ),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        context = manager.run_postfill_hooks({"visible": "value"})
        assert context["hook_ran"] is True

    def test_skips_postfill_for_empty_tuple(self):
        hook_called = []

        def my_hook(ctx):
            hook_called.append(True)
            return ctx

        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(name="--source", type="str", postfill_hook=my_hook),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        manager.run_postfill_hooks({"source": ()})
        assert not hook_called

    def test_runs_postfill_for_nonempty_tuple(self):
        hook_called = []

        def my_hook(ctx):
            hook_called.append(True)
            return ctx

        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(name="--source", type="str", postfill_hook=my_hook),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        manager.run_postfill_hooks({"source": ("val",)})
        assert hook_called


class TestActionManagerInteractive:
    def test_skips_question_when_visible_when_false(self):
        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(name="--always-visible", type="str", prompt="Always?", default="yes"),
                CLIOption(
                    name="--hidden-option",
                    type="str",
                    prompt="Hidden",
                    default="no",
                    visible_when=lambda ctx: False,
                ),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        with patch("questionary.text") as mock_text:
            mock_text.return_value.ask.return_value = "answer"
            context = manager.ask_interactive_questions({})

        assert context.get("always_visible") == "answer"
        assert context.get("hidden_option") is None

    def test_shows_question_when_visible_when_true(self):
        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(
                    name="--conditional",
                    type="str",
                    prompt="Cond?",
                    default="d",
                    visible_when=lambda ctx: True,
                ),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        with patch("questionary.text") as mock_text:
            mock_text.return_value.ask.return_value = "my_answer"
            context = manager.ask_interactive_questions({})

        assert context["conditional"] == "my_answer"

    def test_ask_interactive_shows_prompt_for_empty_tuple(self):
        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(
                    name="--bricks",
                    type="choice",
                    multiple=True,
                    prompt="Bricks?",
                    choices=[
                        ChoiceOption(key="frontend", display="Frontend", value="frontend"),
                        ChoiceOption(key="backend", display="Backend", value="backend"),
                    ],
                ),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        with patch("questionary.checkbox") as mock_checkbox:
            mock_checkbox.return_value.ask.return_value = ["Frontend"]
            context = manager.ask_interactive_questions({"bricks": ()})

        mock_checkbox.assert_called_once()
        assert context["bricks"] == ["frontend"]

    def test_ask_interactive_skips_prompt_for_nonempty_tuple(self):
        class _TestAction(Action):
            depends: set[str] = set()
            cli_options = [
                CLIOption(
                    name="--bricks",
                    type="choice",
                    multiple=True,
                    prompt="Bricks?",
                    choices=[
                        ChoiceOption(key="frontend", display="Frontend", value="frontend"),
                        ChoiceOption(key="backend", display="Backend", value="backend"),
                    ],
                ),
            ]

        manager = ActionManager("test", {}, action_classes=[_TestAction])
        with patch("questionary.checkbox") as mock_checkbox:
            context = manager.ask_interactive_questions({"bricks": ("frontend",)})

        mock_checkbox.assert_not_called()
        assert context["bricks"] == ("frontend",)


class TestActionManagerCreateProject:
    def test_create_project_runs_lifecycle(self):
        calls = []

        class _TestAction(Action):
            depends: set[str] = set()

            def skeleton(self, context):
                return {Path("hello.txt"): "hello"}

            def init(self, context):
                calls.append("init")

            def install(self, context):
                calls.append("install")

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ActionManager("myproject", {}, action_classes=[_TestAction])
            manager.project_path = Path(tmpdir) / "myproject"
            manager.actions = [_TestAction(manager.project_path)]
            manager.create_project()

        assert "init" in calls
        assert "install" in calls

    def test_create_project_skips_install_when_no_install(self):
        calls = []

        class _TestAction(Action):
            depends: set[str] = set()

            def install(self, context):
                calls.append("install")

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ActionManager("myproject", {"no_install": True}, action_classes=[_TestAction])
            manager.project_path = Path(tmpdir) / "myproject"
            manager.actions = [_TestAction(manager.project_path)]
            manager.create_project()

        assert "install" not in calls

    def test_create_project_skips_inactive_actions(self):
        calls = []

        class _ActiveAction(Action):
            depends: set[str] = set()

            def init(self, context):
                calls.append("active")

        class _InactiveAction(Action):
            depends: set[str] = set()

            def activate(self, context):
                return False

            def init(self, context):
                calls.append("inactive")

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ActionManager("myproject", {}, action_classes=[_ActiveAction, _InactiveAction])
            manager.project_path = Path(tmpdir) / "myproject"
            manager.actions = [
                _ActiveAction(manager.project_path),
                _InactiveAction(manager.project_path),
            ]
            manager.create_project()

        assert "active" in calls
        assert "inactive" not in calls
