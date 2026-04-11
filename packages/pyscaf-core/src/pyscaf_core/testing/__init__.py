"""Shared testing framework for pyscaf-core action tests.

Provides YAML-driven action testing infrastructure that downstream
packages can reuse without duplicating test logic.
"""

from pyscaf_core.testing.discovery import (
    ActionTestConfig,
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
    "discover_test_files",
    "discover_test_files_from_entry_points",
]


def create_yaml_tests(
    cli_command: str,
    yaml_dir: str | None = None,
    *,
    entry_point_name: str | None = None,
):
    """Create a parametrized pytest test function for YAML action tests.

    Usage in downstream test file::

        from pyscaf_core.testing import create_yaml_tests
        test_action = create_yaml_tests("demo-scaf", yaml_dir=__file__)

    Args:
        cli_command: CLI command to invoke (e.g. "demo-scaf", "pyscaf-app")
        yaml_dir: Path to directory containing YAML test files, or path to the
                  test file itself (will use its parent directory). If None,
                  uses entry points.
        entry_point_name: If yaml_dir is None, filter entry points by this name.

    Returns:
        A pytest-parametrized test function named ``test_action``.
    """
    from pathlib import Path

    import pytest

    if yaml_dir is not None:
        base = Path(yaml_dir)
        if base.is_file():
            base = base.parent
        files = discover_test_files(base)
    else:
        files = discover_test_files_from_entry_points(filter_name=entry_point_name)

    test_ids = [test_id for _, test_id in files]

    @pytest.mark.parametrize("test_file,test_id", files, ids=test_ids)
    def test_action(test_file: Path, test_id: str):
        runner = ActionTestRunner(test_file, cli_command=cli_command)
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
