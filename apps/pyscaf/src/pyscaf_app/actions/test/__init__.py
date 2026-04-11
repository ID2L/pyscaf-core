"""
Test initialization actions using pytest.
"""

import logging
import os
import subprocess
from pathlib import Path

from pyscaf_core import Action, CLIOption

logger = logging.getLogger(__name__)


class TestAction(Action):
    """Action to initialize a project with pytest testing framework."""

    depends = {"core", "git"}
    run_preferably_after = "git"
    cli_options = [
        CLIOption(
            name="--testing",
            type="bool",
            help="Enable testing with pytest",
            prompt="Do you want to set up testing with pytest?",
            default=False,
        ),
    ]

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        """Activate this action only if testing is enabled."""
        return context.get("testing") is None or context.get("testing", True)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for pytest initialization.

        Returns:
            Dictionary mapping paths to content
        """
        # Read pytest documentation
        pytest_doc_path = Path(__file__).parent / "README.md"
        pytest_doc = pytest_doc_path.read_text() if pytest_doc_path.exists() else ""

        # Read test example template
        test_example_path = Path(__file__).parent / "template_test_example.py"
        test_example_template = test_example_path.read_text() if test_example_path.exists() else ""

        # Basic test example
        project_name = context.get("project_name", "myproject")
        curated_project_name = project_name.replace("-", "_")

        # Format the test example with project variables
        test_example = test_example_template.format(
            project_name=project_name, curated_project_name=curated_project_name
        )

        # Ajout conditionnel du .gitignore si git est activé
        skeleton = {
            Path("tests"): None,  # Create tests directory
            Path("tests/__init__.py"): "",  # Empty init file for tests package
            Path(f"tests/test_{curated_project_name}.py"): test_example,
            Path("tests/README.md"): pytest_doc,
        }
        if context.get("versionning"):
            gitignore_path = Path(__file__).parent / "template.gitignore"
            gitignore_content = gitignore_path.read_text() if gitignore_path.exists() else ""
            skeleton[Path(".gitignore")] = gitignore_content
        return skeleton

    def install(self, context: dict) -> None:
        """
        Install test dependencies and run initial test.
        """
        logger.info("Installing test dependencies...")

        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Run a quick test to validate setup
            logger.info("Running initial test validation...")
            # Remove VIRTUAL_ENV from environment to avoid uv warnings when running inside another venv
            env = os.environ.copy()
            env.pop("VIRTUAL_ENV", None)

            result = subprocess.call(
                ["uv", "run", "pytest", "--version"],
                env=env,
                stdin=None,
                stdout=None,
                stderr=None,
            )

            if result == 0:
                logger.info("Pytest setup validated successfully!")

                # Run the actual tests
                logger.info("Running initial tests...")
                test_result = subprocess.call(
                    ["uv", "run", "pytest", "tests/", "-v"],
                    env=env,
                    stdin=None,
                    stdout=None,
                    stderr=None,
                )

                if test_result == 0:
                    logger.info("All tests passed!")
                else:
                    logger.info("Some tests failed (exit code %s)", test_result)
            else:
                logger.info("Pytest validation failed (exit code %s)", result)

        except FileNotFoundError:
            logger.info("uv not found. Please install it first.")
            logger.info("https://docs.astral.sh/uv/getting-started/installation")
