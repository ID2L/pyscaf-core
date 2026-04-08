import tempfile
from pathlib import Path

import tomlkit
from pyscaf_core.tools.toml_merge import merge_toml_files


def write_toml(path: Path, data: dict) -> None:
    path.write_text(tomlkit.dumps(data), encoding="utf-8")


def read_toml(path: Path) -> dict:
    return tomlkit.parse(path.read_text(encoding="utf-8"))


def test_simple_merge():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.toml"
        dst = Path(tmpdir) / "dst.toml"
        write_toml(src, {"a": 1, "b": 2})
        write_toml(dst, {"b": 3, "c": 4})
        merge_toml_files(src, dst)
        result = read_toml(dst)
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["c"] == 4


def test_nested_merge():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.toml"
        dst = Path(tmpdir) / "dst.toml"
        write_toml(src, {"tool": {"scaffolder": {"x": 1, "y": {"z": 2}}}})
        write_toml(dst, {"tool": {"scaffolder": {"y": {"w": 3}, "other": 5}}})
        merge_toml_files(src, dst)
        result = read_toml(dst)
        assert result["tool"]["scaffolder"]["x"] == 1
        assert result["tool"]["scaffolder"]["y"]["z"] == 2
        assert result["tool"]["scaffolder"]["y"]["w"] == 3
        assert result["tool"]["scaffolder"]["other"] == 5


def test_list_merge():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.toml"
        dst = Path(tmpdir) / "dst.toml"
        write_toml(src, {"a": [1, 2, 3]})
        write_toml(dst, {"a": [3, 4]})
        merge_toml_files(src, dst)
        result = read_toml(dst)
        assert sorted(result["a"]) == [1, 2, 3, 4]


def test_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.toml"
        dst = Path(tmpdir) / "dst.toml"
        write_toml(src, {"a": "new", "b": 2})
        write_toml(dst, {"a": "old", "b": 1, "c": 3})
        merge_toml_files(src, dst)
        result = read_toml(dst)
        assert result["a"] == "new"
        assert result["b"] == 2
        assert result["c"] == 3


def test_no_overwrite_unrelated():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "src.toml"
        dst = Path(tmpdir) / "dst.toml"
        write_toml(src, {"x": 1})
        write_toml(dst, {"y": 2})
        merge_toml_files(src, dst)
        result = read_toml(dst)
        assert result["x"] == 1
        assert result["y"] == 2
