"""Tests for Action base class, CLIOption, and discovery."""

import tempfile
from pathlib import Path

import pytest
from pyscaf_core.actions import (
    Action,
    ChoiceOption,
    CLIOption,
    cli_option_to_key,
)


class TestCLIOption:
    def test_visible_when_callable(self):
        opt = CLIOption(
            name="--apps",
            type="choice",
            visible_when=lambda ctx: ctx.get("project_type") == "monorepo",
        )
        assert opt.visible_when is not None
        assert opt.visible_when({"project_type": "monorepo"}) is True
        assert opt.visible_when({"project_type": "library"}) is False

    def test_visible_when_defaults_to_none(self):
        opt = CLIOption(name="--name", type="str")
        assert opt.visible_when is None

    def test_visible_when_complex_condition(self):
        opt = CLIOption(
            name="--frontend-tech",
            type="choice",
            visible_when=lambda ctx: "frontend" in ctx.get("apps", []),
        )
        assert opt.visible_when({"apps": ["backend", "frontend"]}) is True
        assert opt.visible_when({"apps": ["backend"]}) is False
        assert opt.visible_when({}) is False

    def test_choice_option_keys(self):
        opt = CLIOption(
            name="--license",
            type="choice",
            choices=[
                ChoiceOption(key="mit", display="MIT License", value="MIT"),
                ChoiceOption(key="apache", display="Apache 2.0", value="Apache-2.0"),
            ],
        )
        assert opt.get_choice_keys() == ["mit", "apache"]
        assert opt.get_choice_displays() == ["MIT License", "Apache 2.0"]
        assert opt.get_choice_by_key("mit") == "MIT"
        assert opt.get_choice_by_display("Apache 2.0") == "Apache-2.0"

    def test_default_value_for_choice(self):
        opt = CLIOption(
            name="--tech",
            type="choice",
            default=1,
            choices=[
                ChoiceOption(key="py", display="Python", value="python"),
                ChoiceOption(key="js", display="JavaScript", value="javascript"),
            ],
        )
        assert opt.get_default_value() == "javascript"
        assert opt.get_default_display() == "JavaScript"


class TestAction:
    def test_init_subclass_validates_multi_depends(self):
        with pytest.raises(ValueError, match="multiple depends but no run_preferably_after"):

            class _BadAction(Action):
                depends = {"a", "b"}

    def test_init_subclass_accepts_single_depend(self):
        class _OkAction(Action):
            depends = {"a"}

    def test_init_subclass_accepts_multi_depends_with_after(self):
        class _OkAction(Action):
            depends = {"a", "b"}
            run_preferably_after = "a"

    def test_skeleton_returns_empty_by_default(self):
        action = Action("/tmp/test")
        assert action.skeleton({}) == {}

    def test_activate_returns_true_by_default(self):
        action = Action("/tmp/test")
        assert action.activate({}) is True

    def test_create_skeleton_creates_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:

            class _TestAction(Action):
                def skeleton(self, context):
                    return {
                        Path("hello.txt"): "Hello World",
                        Path("subdir"): None,
                    }

            action = _TestAction(tmpdir)
            created = action.create_skeleton({})
            assert (Path(tmpdir) / "hello.txt").read_text() == "Hello World"
            assert (Path(tmpdir) / "subdir").is_dir()
            assert len(created) == 2

    def test_create_skeleton_appends_to_existing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = Path(tmpdir) / "file.txt"
            existing.write_text("line1")

            class _TestAction(Action):
                def skeleton(self, context):
                    return {Path("file.txt"): "line2"}

            action = _TestAction(tmpdir)
            action.create_skeleton({})
            content = existing.read_text()
            assert "line1" in content
            assert "line2" in content


class TestCliOptionToKey:
    def test_simple(self):
        opt = CLIOption(name="--project-name")
        assert cli_option_to_key(opt) == "project_name"

    def test_double_dash(self):
        opt = CLIOption(name="--no-install")
        assert cli_option_to_key(opt) == "no_install"
