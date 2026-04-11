"""YAML test file discovery — filesystem and entry-point based."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ActionTestConfig:
    """Configuration returned by a ``pyscaf_core.test_yamls`` entry point."""

    yaml_dir: Path
    cli_command: str


def discover_test_files(
    base_dir: Path,
    *,
    module_filter: str | None = None,
    test_filter: str | None = None,
) -> list[tuple[Path, str]]:
    """Scan *base_dir* for ``*.yaml`` test files organised in sub-directories.

    Returns a list of ``(yaml_path, test_id)`` tuples where *test_id*
    has the form ``"module:test_name"`` (e.g. ``"core:test_default"``).
    """
    base_dir = Path(base_dir)
    files: list[tuple[Path, str]] = []

    for yaml_file in sorted(base_dir.rglob("*.yaml")):
        relative = yaml_file.relative_to(base_dir)
        if len(relative.parts) < 2:
            continue
        module_name = relative.parts[0]
        test_name = yaml_file.stem

        if module_filter and module_name != module_filter:
            continue
        if test_filter and test_name != test_filter:
            continue

        files.append((yaml_file, f"{module_name}:{test_name}"))

    return files


def discover_test_configs_from_entry_points(
    *,
    group: str = "pyscaf_core.test_yamls",
    filter_name: str | None = None,
) -> list[ActionTestConfig]:
    """Return all :class:`ActionTestConfig` registered via entry points."""
    from importlib.metadata import entry_points

    configs: list[ActionTestConfig] = []
    for ep in entry_points().select(group=group):
        if filter_name and ep.name != filter_name:
            continue
        obj = ep.load()
        if callable(obj):
            config = obj()
        else:
            config = obj

        if isinstance(config, ActionTestConfig):
            configs.append(config)
        elif isinstance(config, tuple) and len(config) == 2:
            configs.append(ActionTestConfig(yaml_dir=Path(config[0]), cli_command=str(config[1])))

    return configs


def discover_test_files_from_entry_points(
    *,
    group: str = "pyscaf_core.test_yamls",
    filter_name: str | None = None,
) -> list[tuple[Path, str, str]]:
    """Discover YAML test files registered via ``pyscaf_core.test_yamls`` entry points.

    Returns ``(yaml_path, test_id, cli_command)`` tuples.
    """
    all_files: list[tuple[Path, str, str]] = []
    for config in discover_test_configs_from_entry_points(group=group, filter_name=filter_name):
        for yaml_path, test_id in discover_test_files(config.yaml_dir):
            all_files.append((yaml_path, test_id, config.cli_command))
    return all_files
