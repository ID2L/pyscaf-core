"""Tests for demo-scaf app — proves plugin discovery and action execution."""

import tempfile
from pathlib import Path

from click.testing import CliRunner
from demo_scaf.actions import discover_actions
from demo_scaf.actions.hello import HelloAction
from demo_scaf.actions.readme import ReadmeAction
from demo_scaf.main import cli


class TestDiscovery:
    def test_discover_finds_all_actions(self):
        actions = discover_actions()
        action_names = {a.__name__ for a in actions}
        assert "HelloAction" in action_names
        assert "ReadmeAction" in action_names

    def test_discover_returns_action_subclasses(self):
        from pyscaf_core import Action

        actions = discover_actions()
        for action_cls in actions:
            assert issubclass(action_cls, Action)


class TestHelloAction:
    def test_skeleton_creates_hello_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            action = HelloAction(tmpdir)
            skeleton = action.skeleton({"project_name": "test", "greeting": "hello", "author": "tester"})
            assert Path("HELLO.md") in skeleton
            assert "Hello, World!" in skeleton[Path("HELLO.md")]
            assert "tester" in skeleton[Path("HELLO.md")]

    def test_skeleton_with_hi_greeting(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            action = HelloAction(tmpdir)
            skeleton = action.skeleton({"project_name": "test", "greeting": "hi", "author": "tester"})
            assert "Hi there!" in skeleton[Path("HELLO.md")]

    def test_activate_always_true(self):
        action = HelloAction("/tmp/test")
        assert action.activate({}) is True

    def test_has_cli_options(self):
        assert len(HelloAction.cli_options) == 2
        assert HelloAction.cli_options[0].name == "--greeting"
        assert HelloAction.cli_options[1].name == "--author"


class TestReadmeAction:
    def test_depends_on_hello(self):
        assert "hello" in ReadmeAction.depends
        assert ReadmeAction.run_preferably_after == "hello"

    def test_skeleton_creates_readme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            action = ReadmeAction(tmpdir)
            skeleton = action.skeleton({"project_name": "my-proj", "description": "A test", "add_license": True})
            assert Path("README.md") in skeleton
            content = skeleton[Path("README.md")]
            assert "# my-proj" in content
            assert "A test" in content
            assert "## License" in content

    def test_skeleton_without_license(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            action = ReadmeAction(tmpdir)
            skeleton = action.skeleton({"project_name": "my-proj", "description": "A test", "add_license": False})
            content = skeleton[Path("README.md")]
            assert "## License" not in content


class TestCLI:
    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "demo-scaf" in result.output

    def test_init_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["init", "--help"])
        assert result.exit_code == 0
        assert "project_name" in result.output.lower() or "PROJECT_NAME" in result.output

    def test_init_creates_project(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "init",
                    "test-project",
                    "--greeting",
                    "hello",
                    "--author",
                    "tester",
                    "--description",
                    "Test project",
                    "--add-license",
                    "--no-install",
                ],
            )
            assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"
            assert Path("test-project/HELLO.md").exists()
            assert Path("test-project/README.md").exists()

            hello_content = Path("test-project/HELLO.md").read_text()
            assert "Hello, World!" in hello_content
            assert "tester" in hello_content

            readme_content = Path("test-project/README.md").read_text()
            assert "# test-project" in readme_content
            assert "Test project" in readme_content

    def test_init_with_different_greeting(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(
                cli,
                [
                    "init",
                    "my-proj",
                    "--greeting",
                    "hi",
                    "--author",
                    "dev",
                    "--description",
                    "My project",
                    "--no-add-license",
                    "--no-install",
                ],
            )
            assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"
            hello_content = Path("my-proj/HELLO.md").read_text()
            assert "Hi there!" in hello_content
