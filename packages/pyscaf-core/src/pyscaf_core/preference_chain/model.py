from pydantic import BaseModel, Field


class Node(BaseModel):
    id: str
    depends: set[str] = Field(default_factory=set)
    after: str | None = None

    @property
    def external_dependencies(self) -> set[str]:
        return self.depends - ({self.after} if self.after is not None else set())


class ExtendedNode(Node):
    referenced_by: set[str] = Field(default_factory=set)


class ChainLink(BaseModel):
    children: list[ExtendedNode]
    head: ExtendedNode
    tail: ExtendedNode

    @property
    def ids(self) -> list[str]:
        return [node.id for node in self.children]

    @property
    def external_dependencies(self) -> set[str]:
        return set().union(*[node.external_dependencies for node in self.children]) - set(self.ids)

    @property
    def depends(self) -> set[str]:
        return set().union(*[node.depends for node in self.children]) - set(self.ids)

    @property
    def referenced_by(self) -> set[str]:
        return set().union(*[node.referenced_by for node in self.children])
