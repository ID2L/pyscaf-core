"""Action classes for project scaffolding — core engine."""

import importlib
import logging
import os
import pkgutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from pyscaf_core.tools.format_toml import format_toml
from pyscaf_core.tools.toml_merge import merge_toml_files

logger = logging.getLogger(__name__)


class ChoiceOption(BaseModel):
    """Represents a choice option with different display formats for CLI and interactive modes."""

    key: str
    display: str
    value: Any


class CLIOption(BaseModel):
    """Declares a CLI option for an action, supporting strings, booleans, integers, and rich choices."""

    name: str
    type: str = "str"
    help: str | None = None
    default: Any = None
    prompt: str | None = None
    choices: list[ChoiceOption] | None = None
    is_flag: bool | None = None
    multiple: bool | None = None
    required: bool | None = None
    postfill_hook: Callable[[dict[str, str]], dict[str, str]] | None = None
    visible_when: Callable[[dict], bool] | None = None

    model_config = {"arbitrary_types_allowed": True}

    def get_choice_keys(self) -> list[str]:
        if self.choices and isinstance(self.choices[0], ChoiceOption):
            return [choice.key for choice in self.choices]
        return []

    def get_choice_displays(self) -> list[str]:
        if self.choices and isinstance(self.choices[0], ChoiceOption):
            return [choice.display for choice in self.choices]
        return []

    def get_choice_values(self) -> list[Any]:
        if self.choices and isinstance(self.choices[0], ChoiceOption):
            return [choice.value for choice in self.choices]
        return []

    def get_choice_by_key(self, key: str) -> Any | None:
        if self.choices and isinstance(self.choices[0], ChoiceOption):
            for choice in self.choices:
                if choice.key == key:
                    return choice.value
        return None

    def get_choice_by_display(self, display: str) -> Any | None:
        if self.choices and isinstance(self.choices[0], ChoiceOption):
            for choice in self.choices:
                if choice.display == display:
                    return choice.value
        return None

    def get_default_display(self) -> str | None:
        if self.type == "choice" and self.choices and isinstance(self.default, int):
            if 0 <= self.default < len(self.choices):
                if isinstance(self.choices[0], ChoiceOption):
                    return self.choices[self.default].display
        return None

    def get_default_value(self) -> Any:
        if self.type == "choice" and self.choices and isinstance(self.default, int):
            if 0 <= self.default < len(self.choices):
                if isinstance(self.choices[0], ChoiceOption):
                    return self.choices[self.default].value
                else:
                    return self.choices[self.default]
        return self.default


class Action:
    """Abstract base class for all project actions.

    Actions can:
    1. Generate file/directory skeleton via the skeleton() method
    2. Initialize content/behavior via the init() method
    3. Install dependencies via the install() method
    """

    depends: set[str] = set()
    run_preferably_after: str | None = None
    cli_options: list[CLIOption] = []

    def __init_subclass__(cls) -> None:
        if hasattr(cls, "depends") and len(cls.depends) > 1 and not getattr(cls, "run_preferably_after", None):
            raise ValueError(f"Action '{cls.__name__}' has multiple depends but no run_preferably_after")

    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """Define the filesystem skeleton for this action.

        Returns a dictionary mapping paths to content:
        - None -> directory
        - str -> file with that content
        """
        return {}

    def init(self, context: dict) -> None:
        """Default: merges config.toml from the action's directory into pyproject.toml."""
        module = importlib.import_module(self.__class__.__module__)
        module_file = module.__file__
        if not module_file:
            raise RuntimeError(f"Module {module} has no __file__ attribute")
        action_dir = Path(module_file).parent
        config_path = action_dir / "config.toml"
        pyproject_path = self.project_path / "pyproject.toml"
        if config_path.exists():
            merge_toml_files(input_path=config_path, output_path=pyproject_path)
            format_toml(pyproject_path)
            logger.info("Merged %s into %s", config_path, pyproject_path)

    def install(self, context: dict) -> None:
        """Install dependencies or run post-initialization commands."""
        return None

    def create_skeleton(self, context: dict) -> set[Path]:
        """Create the filesystem skeleton for this action."""
        created_paths: set[Path] = set()
        skeleton = self.skeleton(context)

        for path, content in skeleton.items():
            full_path = self.project_path / path

            full_path.parent.mkdir(parents=True, exist_ok=True)

            if content is None:
                full_path.mkdir(exist_ok=True)
            else:
                if full_path.exists():
                    with open(full_path, "a") as f:
                        f.write("\n" + content)
                else:
                    full_path.write_text(content)

            created_paths.add(full_path)

        return created_paths

    def activate(self, context: dict) -> bool:
        """Return True if this action should be executed given the current context."""
        return True


def cli_option_to_key(cli_option: CLIOption) -> str:
    """Convert a CLI option name to a context dictionary key."""
    return cli_option.name.lstrip("-").replace("-", "_")


def discover_actions_from_package(package_path: str, package_name: str) -> list[type[Action]]:
    """Discover Action subclasses by walking a package directory (pkgutil-based).

    Args:
        package_path: Filesystem path to the package directory
        package_name: Fully qualified Python package name for import
    """
    actions: list[type[Action]] = []
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        if module_name in ("base", "manager", "__pycache__"):
            continue
        mod = importlib.import_module(f"{package_name}.{module_name}")
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, Action) and obj is not Action:
                actions.append(obj)
    return actions


def discover_actions_from_entry_points(group: str = "pyscaf_core.plugins") -> list[type[Action]]:
    """Discover Action subclasses registered via importlib.metadata entry points.

    Each entry point should reference either:
    - A callable that returns a list of Action subclasses
    - A module containing Action subclasses
    """
    from importlib.metadata import entry_points

    actions: list[type[Action]] = []
    eps = entry_points().select(group=group)
    for ep in eps:
        obj = ep.load()
        if isinstance(obj, type) and issubclass(obj, Action) and obj is not Action:
            actions.append(obj)
        elif callable(obj):
            result = obj()
            if isinstance(result, list):
                actions.extend(result)
            elif isinstance(result, type) and issubclass(result, Action):
                actions.append(result)
        elif isinstance(obj, type(os)):
            for attr_name in dir(obj):
                attr = getattr(obj, attr_name)
                if isinstance(attr, type) and issubclass(attr, Action) and attr is not Action:
                    actions.append(attr)
    return actions
