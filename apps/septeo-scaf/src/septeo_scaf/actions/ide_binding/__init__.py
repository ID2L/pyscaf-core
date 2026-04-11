"""
IDE Binding action: creates IDE-specific symlinks to .agents/ structure.
"""

from pathlib import Path

from pyscaf_core import Action


class IdeBindingAction(Action):
    """Creates IDE-specific symlinks from .cursor/ or .vscode/ to .agents/ directories."""

    depends = {"agents"}
    run_preferably_after = "agents"
    cli_options: list = []

    def activate(self, context: dict) -> bool:
        return context.get("ide", "cursor") not in ("none", None)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        ide = context.get("ide", "cursor")
        if ide == "cursor":
            return self._cursor_skeleton()
        if ide == "vscode":
            return self._vscode_skeleton()
        return {}

    def _cursor_skeleton(self) -> dict[Path, str | None]:
        return {Path(".cursor"): None}

    def _vscode_skeleton(self) -> dict[Path, str | None]:
        return {Path(".vscode"): None}

    def init(self, context: dict) -> None:
        ide = context.get("ide", "cursor")
        if ide == "cursor":
            self._create_cursor_symlinks()
        elif ide == "vscode":
            self._create_vscode_symlinks()

    def _create_cursor_symlinks(self) -> None:
        cursor_dir = self.project_path / ".cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        symlinks = {
            "rules": "../.agents/rules",
            "skills": "../.agents/skills",
            "commands": "../.agents/commands",
            "mcp": "../.agents/mcp",
        }
        for name, target in symlinks.items():
            link_path = cursor_dir / name
            if not link_path.exists():
                link_path.symlink_to(target)

    def _create_vscode_symlinks(self) -> None:
        vscode_dir = self.project_path / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)
