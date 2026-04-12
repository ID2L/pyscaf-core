"""Shared testing framework for pyscaf-core action tests.

Provides YAML-driven action testing infrastructure that downstream
packages can reuse without duplicating test logic.
"""

from typing import Any

from pyscaf_core.testing.discovery import (
    ActionTestConfig,
    discover_test_configs_from_entry_points,
    discover_test_files,
    discover_test_files_from_entry_points,
)
from pyscaf_core.testing.runner import ActionTestRunner, CheckResult, TestResult

__all__ = [
    "ActionTestConfig",
    "ActionTestRunner",
    "CheckResult",
    "TestResult",
    "create_yaml_tests",
    "discover_test_configs_from_entry_points",
    "discover_test_files",
    "discover_test_files_from_entry_points",
]


def create_yaml_tests(
    cli_command: str | None = None,
    yaml_dir: str | None = None,
    *,
    entry_point_name: str | None = None,
) -> Any:
    """Create a parametrized pytest test function for YAML action tests.

    Usage in downstream test file::

        from pyscaf_core.testing import create_yaml_tests

        # Explicit directory + CLI command
        test_action = create_yaml_tests("demo-scaf", yaml_dir=__file__)

        # Auto-discover from entry points (cli_command from config)
        test_action = create_yaml_tests(entry_point_name="demo_scaf")

    Args:
        cli_command: CLI command to invoke.  Required when *yaml_dir* is given.
                     When using entry-point discovery this is optional (each
                     config provides its own ``cli_command``).
        yaml_dir: Path to directory containing YAML test files, or path to the
                  test file itself (will use its parent directory).
        entry_point_name: Filter entry points by this name.

    Returns:
        A pytest-parametrized test function named ``test_action``.
    """
    from pathlib import Path

    import pytest

    if yaml_dir is not None:
        if cli_command is None:
            raise ValueError("cli_command is required when yaml_dir is provided")
        base = Path(yaml_dir)
        if base.is_file():
            base = base.parent
        test_params = [(f, tid, cli_command) for f, tid in discover_test_files(base)]
    else:
        test_params = discover_test_files_from_entry_points(filter_name=entry_point_name)

    test_ids = [test_id for _, test_id, _ in test_params]

    @pytest.mark.parametrize("test_file,test_id,cmd", test_params, ids=test_ids)
    def test_action(test_file: Path, test_id: str, cmd: str):
        runner = ActionTestRunner(test_file, cli_command=cmd)
        result: TestResult = runner.run_test()

        failed = [c for c in result["check_results"] if not c["success"]]
        if failed:
            lines = [f"Test failed for {test_id}", f"Command: {result['command']}"]
            for c in failed:
                msg = f"  FAIL: {c['name']} ({c['type']} on {c['file_path']})"
                if c.get("error"):
                    msg += f" — {c['error']}"
                lines.append(msg)
            if result["stdout"]:
                lines.append(f"\nstdout:\n{result['stdout']}")
            if result["stderr"]:
                lines.append(f"\nstderr:\n{result['stderr']}")
            pytest.fail("\n".join(lines))

        assert result["return_code"] == 0, (
            f"Command exited with code {result['return_code']}:\n"
            f"  {result['command']}\n"
            f"stdout: {result['stdout']}\nstderr: {result['stderr']}"
        )

    return test_action
