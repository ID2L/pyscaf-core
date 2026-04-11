"""Tests for pyscaf_core.testing.runner module."""

from pathlib import Path

import pytest
import yaml

from pyscaf_core.testing.runner import ActionTestRunner


class TestActionTestRunner:
    def _write_yaml(self, tmp_path: Path, config: dict) -> Path:
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml.dump(config))
        return yaml_file

    def test_load_config_requires_checks(self, tmp_path: Path):
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text("cli_arguments: {}")
        with pytest.raises(ValueError, match="Missing 'checks'"):
            ActionTestRunner(yaml_file)

    def test_build_cli_command_defaults(self, tmp_path: Path):
        yaml_file = self._write_yaml(tmp_path, {"checks": []})
        runner = ActionTestRunner(yaml_file, cli_command="demo-scaf")
        cmd = runner._build_cli_command()
        assert cmd == ["demo-scaf", "init", "tmp_project", "--no-install"]

    def test_build_cli_command_with_options(self, tmp_path: Path):
        config = {
            "cli_arguments": {
                "options": {"author": "John", "git": True, "no-install": False}
            },
            "checks": [],
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file, cli_command="my-cli")
        cmd = runner._build_cli_command()

        assert "my-cli" == cmd[0]
        assert "--author" in cmd
        assert "John" in cmd
        assert "--git" in cmd
        assert "--no-no-install" in cmd

    def test_build_cli_command_with_list_options(self, tmp_path: Path):
        config = {
            "cli_arguments": {
                "options": {"apps": ["backend", "frontend"]}
            },
            "checks": [],
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file, cli_command="my-cli")
        cmd = runner._build_cli_command()

        assert cmd.count("--apps") == 2
        apps_indices = [i for i, v in enumerate(cmd) if v == "--apps"]
        assert cmd[apps_indices[0] + 1] == "backend"
        assert cmd[apps_indices[1] + 1] == "frontend"

    def test_build_cli_command_with_single_item_list(self, tmp_path: Path):
        config = {
            "cli_arguments": {
                "options": {"apps": ["backend"]}
            },
            "checks": [],
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file, cli_command="my-cli")
        cmd = runner._build_cli_command()

        assert cmd.count("--apps") == 1
        idx = cmd.index("--apps")
        assert cmd[idx + 1] == "backend"

    def test_build_cli_command_with_empty_list(self, tmp_path: Path):
        config = {
            "cli_arguments": {
                "options": {"apps": []}
            },
            "checks": [],
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file, cli_command="my-cli")
        cmd = runner._build_cli_command()

        assert "--apps" not in cmd

    def test_build_cli_command_mixed_option_types(self, tmp_path: Path):
        config = {
            "cli_arguments": {
                "options": {
                    "verbose": True,
                    "apps": ["backend", "frontend"],
                    "name": "myproject",
                    "no-cache": False,
                }
            },
            "checks": [],
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file, cli_command="my-cli")
        cmd = runner._build_cli_command()

        assert "--verbose" in cmd
        assert cmd.count("--apps") == 2
        assert "--name" in cmd
        assert "myproject" in cmd
        assert "--no-no-cache" in cmd

    def test_build_cli_command_with_positionals(self, tmp_path: Path):
        config = {
            "cli_arguments": {"positionals": ["create", "my-proj"]},
            "checks": [],
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file, cli_command="tool")
        cmd = runner._build_cli_command()
        assert cmd[:3] == ["tool", "create", "my-proj"]

    def test_check_file_exists(self, tmp_path: Path):
        yaml_file = self._write_yaml(tmp_path, {"checks": []})
        runner = ActionTestRunner(yaml_file)
        runner.temp_dir = tmp_path
        (tmp_path / "hello.txt").write_text("hi")

        assert runner._check_file_exists("hello.txt") is True
        assert runner._check_file_exists("missing.txt") is False

    def test_check_file_contains(self, tmp_path: Path):
        yaml_file = self._write_yaml(tmp_path, {"checks": []})
        runner = ActionTestRunner(yaml_file)
        runner.temp_dir = tmp_path
        (tmp_path / "file.txt").write_text("hello world")

        assert runner._check_file_contains("file.txt", "hello") is True
        assert runner._check_file_contains("file.txt", "missing") is False
        assert runner._check_file_contains("nope.txt", "x") is False

    def test_run_checks_exist(self, tmp_path: Path):
        config = {
            "checks": [
                {"name": "file exists", "type": "exist", "file_path": "a.txt"},
                {"name": "file missing", "type": "not_exist", "file_path": "b.txt"},
            ]
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file)
        runner.temp_dir = tmp_path
        (tmp_path / "a.txt").write_text("content")

        results = runner._run_checks()
        assert results[0]["success"] is True
        assert results[1]["success"] is True

    def test_run_checks_contains(self, tmp_path: Path):
        config = {
            "checks": [
                {"name": "has text", "type": "contains", "file_path": "f.txt", "content": "needle"},
                {"name": "no text", "type": "not_contains", "file_path": "f.txt", "content": "absent"},
            ]
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file)
        runner.temp_dir = tmp_path
        (tmp_path / "f.txt").write_text("find the needle here")

        results = runner._run_checks()
        assert results[0]["success"] is True
        assert results[1]["success"] is True

    def test_unknown_check_type(self, tmp_path: Path):
        config = {"checks": [{"name": "bad", "type": "invalid", "file_path": "x"}]}
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file)
        runner.temp_dir = tmp_path

        results = runner._run_checks()
        assert results[0]["success"] is False
        assert "Unknown check type" in results[0]["error"]

    def test_path_traversal_blocked(self, tmp_path: Path):
        yaml_file = self._write_yaml(tmp_path, {"checks": []})
        runner = ActionTestRunner(yaml_file)
        runner.temp_dir = tmp_path

        assert runner._check_file_exists("../../../etc/passwd") is False
        assert runner._check_file_exists("/etc/passwd") is False
        assert runner._check_file_contains("../../etc/passwd", "root") is False

    def test_custom_check_failure_propagates(self, tmp_path: Path):
        config = {
            "checks": [
                {
                    "name": "bad custom",
                    "type": "custom",
                    "function_path": "nonexistent.module:func",
                }
            ]
        }
        yaml_file = self._write_yaml(tmp_path, config)
        runner = ActionTestRunner(yaml_file)
        runner.temp_dir = tmp_path

        results = runner._run_checks()
        assert results[0]["success"] is False
        assert results[0]["error"] is not None
        assert "Custom check" in results[0]["error"]
