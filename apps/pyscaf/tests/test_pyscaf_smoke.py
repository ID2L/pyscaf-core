"""Smoke tests for pyscaf-app — validates plugin discovery and CLI wiring."""

from click.testing import CliRunner
from pyscaf_app.actions import discover_actions
from pyscaf_app.main import cli
from pyscaf_core import Action


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "pyscaf-app" in result.output


def test_discover_actions_count():
    actions = discover_actions()
    assert len(actions) == 8
    for action_cls in actions:
        assert issubclass(action_cls, Action)
        assert action_cls is not Action
