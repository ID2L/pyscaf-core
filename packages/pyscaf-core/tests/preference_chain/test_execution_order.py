import pytest
from pyscaf_core.preference_chain import CircularDependencyError, best_execution_order
from pyscaf_core.preference_chain.model import Node


class TestBestExecutionOrder:
    """Test the best_execution_order function directly with the expected input format."""

    def test_simple_linear_execution_order(self):
        nodes = [
            Node(id="A", depends=set(), after=None),
            Node(id="B", depends={"A"}, after="A"),
            Node(id="C", depends={"B"}, after="B"),
        ]

        result = best_execution_order(nodes)
        expected = ["A", "B", "C"]

        assert result == expected, f"Expected {expected}, got {result}"

    def test_diamond_execution_order(self):
        nodes = [
            Node(id="A", depends=set(), after=None),
            Node(id="B", depends={"A"}, after="A"),
            Node(id="C", depends={"A"}, after="A"),
            Node(id="D", depends={"B", "C"}, after="B"),
        ]

        result = best_execution_order(nodes)

        assert result[0] == "A", f"Expected A to be first, got {result}"
        assert result[-1] == "D", f"Expected D to be last, got {result}"

        a_index = result.index("A")
        b_index = result.index("B")
        c_index = result.index("C")
        d_index = result.index("D")

        assert a_index < b_index and a_index < c_index, "A should come before B and C"
        assert b_index < d_index and c_index < d_index, "B and C should come before D"

    def test_single_dependency_auto_after(self):
        nodes = [
            Node(id="root", depends=set(), after=None),
            Node(id="setup", depends={"root"}, after="root"),
            Node(id="build", depends={"setup"}, after="setup"),
        ]

        result = best_execution_order(nodes)
        expected = ["root", "setup", "build"]

        assert result == expected, f"Expected {expected}, got {result}"

    def test_multiple_external_dependencies(self):
        nodes = [
            Node(id="A", depends=set(), after=None),
            Node(id="B", depends=set(), after=None),
            Node(id="C", depends={"A", "B"}, after="A"),
        ]

        result = best_execution_order(nodes)

        a_index = result.index("A")
        b_index = result.index("B")
        c_index = result.index("C")

        assert a_index < c_index, "A should come before C"
        assert b_index < c_index, "B should come before C"
        assert result[-1] == "C", "C should be last"

    def test_circular_dependency_detection(self):
        nodes = [
            Node(id="A", depends={"C"}, after="C"),
            Node(id="B", depends={"A"}, after="A"),
            Node(id="C", depends={"B"}, after="B"),
        ]

        with pytest.raises(CircularDependencyError):
            best_execution_order(nodes)

    def test_complex_circular_dependency_detection(self):
        nodes = [
            Node(id="root", depends={"A"}, after="A"),
            Node(id="A", depends={"C"}, after="C"),
            Node(id="B", depends={"A"}, after="A"),
            Node(id="C", depends={"B"}, after="B"),
        ]

        with pytest.raises(CircularDependencyError):
            best_execution_order(nodes)

    def test_complex_real_world_scenario(self):
        nodes = [
            Node(id="checkout", depends=set(), after=None),
            Node(id="install-deps", depends={"checkout"}, after="checkout"),
            Node(id="lint", depends={"install-deps"}, after="install-deps"),
            Node(id="test", depends={"install-deps"}, after="install-deps"),
            Node(id="build", depends={"lint", "test"}, after="lint"),
            Node(id="docker-build", depends={"build"}, after="build"),
            Node(id="deploy-staging", depends={"docker-build"}, after="docker-build"),
            Node(id="e2e-tests", depends={"deploy-staging"}, after="deploy-staging"),
            Node(id="deploy-prod", depends={"e2e-tests"}, after="e2e-tests"),
        ]

        result = best_execution_order(nodes)

        checkout_index = result.index("checkout")
        install_deps_index = result.index("install-deps")
        lint_index = result.index("lint")
        test_index = result.index("test")
        build_index = result.index("build")
        docker_build_index = result.index("docker-build")
        deploy_staging_index = result.index("deploy-staging")
        e2e_tests_index = result.index("e2e-tests")
        deploy_prod_index = result.index("deploy-prod")

        assert checkout_index < install_deps_index
        assert install_deps_index < lint_index
        assert install_deps_index < test_index
        assert lint_index < build_index and test_index < build_index
        assert build_index < docker_build_index
        assert docker_build_index < deploy_staging_index
        assert deploy_staging_index < e2e_tests_index
        assert e2e_tests_index < deploy_prod_index

    def test_empty_input(self):
        nodes = []
        result = best_execution_order(nodes)
        assert result == [], "Empty input should return empty result"

    def test_single_node(self):
        nodes = [Node(id="single", depends=set(), after=None)]
        result = best_execution_order(nodes)
        assert result == ["single"], f"Expected ['single'], got {result}"

    def test_invalid_after_field(self):
        nodes = [
            Node(id="A", depends=set(), after=None),
            Node(id="B", depends={"A"}, after="C"),
        ]

        with pytest.raises(ValueError, match="Node 'B' has 'after'='C' but it's not in depends"):
            best_execution_order(nodes)

    def test_auto_after_for_single_dependency(self):
        nodes = [
            Node(id="A", depends=set(), after=None),
            Node(id="B", depends={"A"}, after=None),
        ]

        result = best_execution_order(nodes)
        expected = ["A", "B"]
        assert result == expected, f"Expected {expected}, got {result}"
