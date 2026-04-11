"""YAML-driven action test runner.

Adapted from pyscaf's ``tests/actions/test_actions.py``.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, TypedDict

import yaml


class CheckResult(TypedDict):
    name: str
    type: str
    file_path: str
    success: bool
    error: str | None


class TestResult(TypedDict):
    test_file: str
    command: str
    return_code: int
    stdout: str
    stderr: str
    check_results: list[CheckResult]
    all_checks_passed: bool


class ActionTestRunner:
    """Run a single YAML test specification against a CLI scaffolder."""

    def __init__(self, test_file_path: Path, *, cli_command: str = "pyscaf"):
        self.test_file_path = Path(test_file_path)
        self.cli_command = cli_command
        self.config = self._load_config()
        self.temp_dir: Path | None = None

    def _load_config(self) -> dict[str, Any]:
        with open(self.test_file_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if "checks" not in config:
            raise ValueError(f"Missing 'checks' in {self.test_file_path}")
        return config

    def _build_cli_command(self) -> list[str]:
        cmd = [self.cli_command]

        positionals = self.config.get("cli_arguments", {}).get("positionals", [])
        cmd.extend(positionals or ["init", "tmp_project"])

        cmd.append("--no-install")

        for key, value in self.config.get("cli_arguments", {}).get("options", {}).items():
            if isinstance(value, bool):
                cmd.append(f"--{key}" if value else f"--no-{key}")
            else:
                cmd.extend([f"--{key}", str(value)])

        return cmd

    def _resolve_safe_path(self, file_path: str) -> Path | None:
        """Resolve *file_path* inside ``self.temp_dir``, rejecting escapes."""
        if not self.temp_dir:
            return None
        resolved = (self.temp_dir / file_path).resolve()
        if not resolved.is_relative_to(self.temp_dir.resolve()):
            return None
        return resolved

    def _check_file_exists(self, file_path: str) -> bool:
        safe = self._resolve_safe_path(file_path)
        return safe is not None and safe.exists()

    def _check_file_contains(self, file_path: str, content: str) -> bool:
        safe = self._resolve_safe_path(file_path)
        if safe is None or not safe.exists():
            return False
        try:
            return content in safe.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise RuntimeError(f"Cannot read {file_path}: {exc}") from exc

    def _execute_custom_check(self, function_path: str) -> bool:
        """Execute a custom check function.

        Only modules prefixed with ``tests.`` or within the project's own
        test package are expected.  Callers must ensure YAML sources are trusted.
        """
        try:
            module_path, function_name = function_path.rsplit(":", 1)
            module = __import__(module_path, fromlist=[function_name])
            func = getattr(module, function_name)
            return bool(func(self.temp_dir))
        except Exception as exc:
            raise RuntimeError(f"Custom check {function_path} failed: {exc}") from exc

    def _run_checks(self) -> list[CheckResult]:
        results: list[CheckResult] = []
        for check in self.config["checks"]:
            result: CheckResult = {
                "name": check["name"],
                "type": check["type"],
                "file_path": check.get("file_path", ""),
                "success": False,
                "error": None,
            }
            try:
                match check["type"]:
                    case "exist":
                        result["success"] = self._check_file_exists(check["file_path"])
                    case "not_exist":
                        result["success"] = not self._check_file_exists(check["file_path"])
                    case "contains":
                        result["success"] = self._check_file_contains(check["file_path"], check["content"])
                    case "not_contains":
                        result["success"] = not self._check_file_contains(check["file_path"], check["content"])
                    case "custom":
                        result["success"] = self._execute_custom_check(check["function_path"])
                    case _:
                        result["error"] = f"Unknown check type: {check['type']}"
            except Exception as exc:
                result["error"] = str(exc)
            results.append(result)
        return results

    def run_test(self) -> TestResult:
        self.temp_dir = Path(tempfile.mkdtemp())
        try:
            cmd = self._build_cli_command()
            proc = subprocess.run(cmd, cwd=self.temp_dir, capture_output=True, text=True, timeout=60)
            check_results = self._run_checks()
            return {
                "test_file": str(self.test_file_path),
                "command": " ".join(cmd),
                "return_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "check_results": check_results,
                "all_checks_passed": all(c["success"] for c in check_results),
            }
        finally:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
