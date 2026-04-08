import logging

from pyscaf_core.preference_chain.chain import (
    build_chains,
    compute_all_resolution_pathes,
    compute_path_score,
    extend_nodes,
)

from .circular_dependency_error import CircularDependencyError
from .dependency_loader import load_and_complete_dependencies
from .model import Node
from .tree_walker import DependencyTreeWalker

logger = logging.getLogger(__name__)

__all__ = [
    "CircularDependencyError",
    "DependencyTreeWalker",
    "best_execution_order",
    "build_chains",
    "compute_all_resolution_pathes",
    "compute_path_score",
    "extend_nodes",
    "load_and_complete_dependencies",
]


def best_execution_order(nodes: list[Node]) -> list[str]:
    """Determine the best execution order using the preference chain logic.

    Args:
        nodes: List of Node objects with 'id', 'depends', and 'after' attributes

    Returns:
        List of node IDs in optimal execution order

    Raises:
        CircularDependencyError: If no valid resolution path can be found
        ValueError: If a node's 'after' is not in its 'depends'
    """
    node_objects: list[Node] = []
    for node in nodes:
        if node.depends and node.after is None:
            after = next(iter(node.depends))
        else:
            after = node.after

        if after is not None and after not in node.depends:
            raise ValueError(f"Node '{node.id}' has 'after'='{after}' but it's not in depends={node.depends}")

        node_obj = Node(id=node.id, depends=node.depends, after=after)
        node_objects.append(node_obj)

    logger.debug(f"Processed {len(node_objects)} nodes")

    extended_dependencies = extend_nodes(node_objects)
    clusters = build_chains(extended_dependencies)

    logger.debug(f"Built {len(clusters)} chains")

    all_resolution_paths = list(compute_all_resolution_pathes(clusters))

    if not all_resolution_paths:
        node_ids = [node.id for node in node_objects]
        error_msg = (
            f"No valid resolution path found for nodes: {node_ids}. "
            "This indicates circular dependencies or unsatisfiable constraints."
        )
        logger.error(error_msg)
        raise CircularDependencyError(error_msg)

    logger.debug(f"Found {len(all_resolution_paths)} resolution paths")

    all_resolution_paths.sort(key=lambda path: -compute_path_score(list(path)))

    best_path = all_resolution_paths[0]
    final_order = [node_id for chain in best_path for node_id in chain.ids]

    logger.debug(f"Best execution order: {final_order}")

    return final_order
