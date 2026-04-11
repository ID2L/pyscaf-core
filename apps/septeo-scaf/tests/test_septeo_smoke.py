"""Smoke tests for septeo-scaf — validates plugin discovery and CLI wiring."""

from click.testing import CliRunner
from pyscaf_core import Action
from septeo_scaf.actions import discover_actions
from septeo_scaf.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "septeo-scaf" in result.output


def test_discover_actions_count():
    actions = discover_actions()
    assert len(actions) == 17
    for action_cls in actions:
        assert issubclass(action_cls, Action)
        assert action_cls is not Action
