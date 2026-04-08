from collections import defaultdict

from .model import Node


class DependencyTreeWalker:
    def __init__(self, dependencies: list[Node], root_id: str):
        self.dependencies = dependencies
        self.root_id = root_id
        self.tree: dict | None = None
        self.external_depends: set[str] = set()
        self.fullfilled_depends: set[str] = set()
        self._build_tree()

    def _build_tree(self) -> None:
        after_targets: defaultdict[str, list[Node]] = defaultdict(list)
        for dep in self.dependencies:
            if dep.after:
                after_targets[dep.after].append(dep)

        visited: set[str] = set()
        extra_depends: set[str] = set()

        def _build(current_id: str) -> dict:
            if current_id in visited:
                return {}
            visited.add(current_id)
            children = {}
            for dep in after_targets.get(current_id, []):
                children[dep.id] = _build(dep.id)
                if dep.depends and len(dep.depends) > 1:
                    for d in dep.depends:
                        if d != current_id:
                            extra_depends.add(d)
            return children

        self.tree = {self.root_id: _build(self.root_id)}
        self.external_depends = extra_depends
        self.fullfilled_depends = visited

    def format_tree(self) -> str:
        """Format the dependency tree as a string (like the 'tree' utility)."""
        lines: list[str] = []

        def _format_subtree(subtree: dict, prefix: str = "") -> None:
            items = list(subtree.items())
            for idx, (node, children) in enumerate(items):
                connector = "└── " if idx == len(items) - 1 else "├── "
                lines.append(prefix + connector + node)
                if children:
                    extension = "    " if idx == len(items) - 1 else "│   "
                    _format_subtree(children, prefix + extension)

        if self.tree:
            _format_subtree(self.tree)
        return "\n".join(lines)

    def print_tree(self) -> None:
        """Print the dependency tree in a graphical way (like the 'tree' utility)."""
        print(self.format_tree())
