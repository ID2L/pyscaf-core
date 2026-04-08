import itertools
import logging

from pyscaf_core.preference_chain.model import ChainLink, ExtendedNode, Node

from .circular_dependency_error import CircularDependencyError

logger = logging.getLogger(__name__)


def extend_nodes(tree: list[Node]) -> list[ExtendedNode]:
    extended_nodes: list[ExtendedNode] = []
    for node in tree:
        extended_nodes.append(ExtendedNode(id=node.id, depends=node.depends, after=node.after))
    for node in extended_nodes:
        for dep_id in node.depends:
            found_node = next((x for x in extended_nodes if x.id == dep_id), None)
            if found_node:
                found_node.referenced_by.add(node.id)
    return extended_nodes


def update_chains(node: ExtendedNode, chains: list[ChainLink]) -> ChainLink:
    for chain in chains:
        if (
            chain.head is not None
            and node.id == chain.head.id
            and node.referenced_by.issubset(chain.ids)
            and (
                set(node.external_dependencies).issubset(chain.external_dependencies)
                or len(chain.external_dependencies) == 0
            )
        ):
            logger.debug(f"HEAD updated chain {chain.ids} with {node.id}")
            chain.head = node
            chain.children.append(node)
            return chain
        if (
            node.after is not None
            and node.after == chain.tail.id
            and set(node.external_dependencies).issubset(chain.external_dependencies)
            and len(chain.tail.referenced_by) <= 1
        ):
            logger.debug(f"QUEUED updated chain {chain.ids} with {node.id}")
            chain.tail = node
            chain.children.append(node)
            return chain

    chain = ChainLink(children=[node], head=node, tail=node)
    chains.append(chain)
    return chain


def merge_chains(chain: ChainLink, chains: list[ChainLink]) -> ChainLink:
    for other_chain in chains:
        if chain == other_chain:
            continue
        if (
            chain.tail.id == other_chain.head.id
            and chain.tail.referenced_by.issubset(other_chain.ids)
            and (
                set(chain.external_dependencies).issubset(other_chain.external_dependencies.union(set(other_chain.ids)))
                or len(other_chain.external_dependencies) == 0
            )
        ):
            logger.debug(f"HEAD merged chain {chain.ids} with {other_chain.ids}")
            other_chain.head = chain.head
            other_chain.children.extend(chain.children)
            chains.remove(chain)
            return other_chain
        if (
            chain.head.after == other_chain.tail.id
            and set(chain.external_dependencies).issubset(other_chain.external_dependencies.union(set(other_chain.ids)))
            and len(other_chain.tail.referenced_by) <= 1
        ):
            logger.debug(f"QUEUED merged chain {other_chain.ids} with {chain.ids}\n")
            other_chain.tail = chain.tail
            other_chain.children.extend(chain.children)
            chains.remove(chain)
            return other_chain
    logger.debug(f"no merge for {chain.ids}")
    return chain


def build_chains(tree: list[ExtendedNode]) -> list[ChainLink]:
    chains: list[ChainLink] = []
    for node in tree:
        logger.debug(f"Processing node {node}")
        chain = update_chains(node, chains)
        logger.debug(f"Chain (before merging): {chain.ids}")
        chain = merge_chains(chain, chains)

        if chain.tail.referenced_by is not None and chain.head.id in chain.tail.referenced_by:
            logger.debug(f"Chain (after merging): {chain.ids} is a loop")
            raise CircularDependencyError("Circular dependency detected")
        logger.debug(
            f"Chain (after merging):"
            f"Chain: {chain.ids} referenced by {chain.referenced_by}"
            f" depends on {chain.external_dependencies}\n",
        )

    return chains


def compute_all_resolution_pathes(chains: list[ChainLink]) -> list[list[ChainLink]]:
    """Compute valid topological orderings of chains using DFS with pruning.

    For small chain counts (<=8), enumerate all valid permutations.
    For larger counts, use greedy topological sort to avoid factorial explosion.
    """
    if len(chains) <= 8:
        return _enumerate_valid_paths(chains)
    return _topological_resolution(chains)


def _enumerate_valid_paths(chains: list[ChainLink]) -> list[list[ChainLink]]:
    valid_pathes: list[list[ChainLink]] = []
    for path in itertools.permutations(chains):
        is_valid = True
        for i, chain in enumerate(path):
            previous_ids = set().union(*(prev_chain.ids for prev_chain in path[:i])) if i > 0 else set()
            if not chain.depends.issubset(previous_ids):
                is_valid = False
                break
        if is_valid:
            valid_pathes.append(list(path))
    return valid_pathes


def _topological_resolution(chains: list[ChainLink]) -> list[list[ChainLink]]:
    """Greedy topological sort: at each step pick the chain with fewest unmet deps."""
    chain_by_ids = {tuple(c.ids): c for c in chains}
    remaining = set(chain_by_ids.keys())
    resolved_ids: set[str] = set()
    result: list[ChainLink] = []

    while remaining:
        ready = [
            k for k in remaining
            if chain_by_ids[k].depends.issubset(resolved_ids)
        ]
        if not ready:
            logger.error(f"No ready chains among {remaining}, resolved={resolved_ids}")
            return []
        ready.sort(key=lambda k: (-len(chain_by_ids[k].referenced_by), len(chain_by_ids[k].depends)))
        chosen = ready[0]
        remaining.remove(chosen)
        result.append(chain_by_ids[chosen])
        resolved_ids.update(chosen)

    return [result]


def compute_path_score(path: list[ChainLink]) -> int:
    score = 0
    for i in range(1, len(path)):
        chain = path[i]
        previous_chain = path[i - 1]

        if chain.head.after != previous_chain.tail.id:
            score -= 1

    return score
