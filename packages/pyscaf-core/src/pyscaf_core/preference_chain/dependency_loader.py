import logging
from collections import defaultdict

import yaml
from pydantic import ValidationError

from .model import Node

logger = logging.getLogger(__name__)


def load_and_complete_dependencies(yaml_path: str) -> list[Node]:
    """Load dependencies from a YAML file and complete the 'after' property if possible."""
    with open(yaml_path) as f:
        raw_dependencies = yaml.safe_load(f)

    dependencies: list[Node] = []
    for entry in raw_dependencies:
        try:
            node_data = {
                "id": entry["id"],
                "depends": set(entry.get("depends", [])),
                "after": entry.get("after"),
            }
            dep = Node(**node_data)
        except ValidationError as e:
            logger.warning(f"Validation error for dependency '{entry.get('id', '?')}': {e}")
            continue
        if dep.after is None:
            if dep.depends:
                if len(dep.depends) == 1:
                    dep.after = next(iter(dep.depends))
                else:
                    logger.warning(f"Dependency '{dep.id}' has multiple 'depends' but no 'after'.")
        dependencies.append(dep)
    return dependencies


def build_dependency_tree(dependencies: list[Node], root_id: str) -> tuple[dict, set[str]]:
    """Build a dependency tree starting from root_id, following 'after' recursively."""
    after_targets: defaultdict[str, list[Node]] = defaultdict(list)
    for dep in dependencies:
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

    tree = {root_id: _build(root_id)}
    return tree, extra_depends
