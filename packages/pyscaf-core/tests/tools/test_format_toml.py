import tempfile
from pathlib import Path

from pyscaf_core.tools.format_toml import format_toml


def test_format_toml_adds_blank_between_sections():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "test.toml"
        p.write_text("[section1]\na = 1\n[section2]\nb = 2\n", encoding="utf-8")
        format_toml(p)
        content = p.read_text(encoding="utf-8")
        assert "\n\n[section2]" in content


def test_format_toml_removes_extra_blanks():
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "test.toml"
        p.write_text("[section1]\na = 1\n\n\n\n[section2]\nb = 2\n", encoding="utf-8")
        format_toml(p)
        content = p.read_text(encoding="utf-8")
        assert "\n\n\n" not in content
