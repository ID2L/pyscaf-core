"""Tests for pyscaf_core.testing.discovery module."""

from pathlib import Path

from pyscaf_core.testing.discovery import ActionTestConfig, discover_test_files


class TestDiscoverTestFiles:
    def test_finds_yaml_in_subdirectories(self, tmp_path: Path):
        core_dir = tmp_path / "core"
        core_dir.mkdir()
        (core_dir / "test_default.yaml").write_text("checks: []")
        (core_dir / "test_author.yaml").write_text("checks: []")

        git_dir = tmp_path / "git"
        git_dir.mkdir()
        (git_dir / "test_default.yaml").write_text("checks: []")

        files = discover_test_files(tmp_path)
        ids = [tid for _, tid in files]

        assert len(files) == 3
        assert "core:test_author" in ids
        assert "core:test_default" in ids
        assert "git:test_default" in ids

    def test_ignores_yaml_at_root_level(self, tmp_path: Path):
        (tmp_path / "stray.yaml").write_text("checks: []")

        files = discover_test_files(tmp_path)
        assert len(files) == 0

    def test_module_filter(self, tmp_path: Path):
        for name in ("core", "git"):
            d = tmp_path / name
            d.mkdir()
            (d / "test_a.yaml").write_text("checks: []")

        files = discover_test_files(tmp_path, module_filter="core")
        assert len(files) == 1
        assert files[0][1] == "core:test_a"

    def test_test_filter(self, tmp_path: Path):
        d = tmp_path / "core"
        d.mkdir()
        (d / "test_a.yaml").write_text("checks: []")
        (d / "test_b.yaml").write_text("checks: []")

        files = discover_test_files(tmp_path, test_filter="test_b")
        assert len(files) == 1
        assert files[0][1] == "core:test_b"

    def test_empty_directory(self, tmp_path: Path):
        files = discover_test_files(tmp_path)
        assert files == []


class TestActionTestConfig:
    def test_dataclass_fields(self):
        config = ActionTestConfig(yaml_dir=Path("/tmp/yamls"), cli_command="my-cli")
        assert config.yaml_dir == Path("/tmp/yamls")
        assert config.cli_command == "my-cli"
