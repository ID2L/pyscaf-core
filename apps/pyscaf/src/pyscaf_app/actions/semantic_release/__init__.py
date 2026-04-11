"""
Semantic release configuration actions.
"""

import logging
from pathlib import Path

import tomli
import tomli_w
from pyscaf_core import Action, CLIOption

logger = logging.getLogger(__name__)


class SemanticReleaseAction(Action):
    """Action to configure semantic release for the project."""

    depends = {"git"}
    run_preferably_after = "git"
    cli_options = [
        CLIOption(
            name="--semantic-release",
            type="bool",
            help="Enable semantic release configuration",
            prompt="Do you want to configure semantic release for this project?",
            default=False,
        ),
    ]

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        """Only activate if versionning is enabled and semantic-release is requested."""
        return context.get("versionning", False) and (
            context.get("semantic_release") is None or context.get("semantic_release", True)
        )

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for semantic release.

        Returns:
            Dictionary mapping paths to content
        """
        skeleton = {}

        # Add README.md documentation
        readme_path = Path(__file__).parent / "README.md"
        if readme_path.exists():
            skeleton[Path("README.md")] = readme_path.read_text()
            logger.info("Added semantic-release README.md")

        # Copy GitHub workflows if git_host is github
        git_host = context.get("git_host")
        if git_host == "github":
            workflows_dir = Path(__file__).parent / "github" / "workflows"
            if workflows_dir.exists():
                for workflow_file in workflows_dir.glob("*.yml"):
                    # Copy to .github/workflows/ in the generated project
                    target_path = Path(".github") / "workflows" / workflow_file.name
                    skeleton[target_path] = workflow_file.read_text()
                    logger.info("Added GitHub workflow: %s", target_path)

        return skeleton

    def init(self, context: dict) -> None:
        """
        Initialize semantic release configuration.

        This will:
        1. Merge the config.toml like other actions
        2. Update the version_variables based on the context.project name
        3. Update the remote type based on context.git_host
        """
        logger.info("Configuring semantic release...")

        # First, call the parent init to merge config.toml
        super().init(context)

        # Update configuration with tomli_w
        pyproject_path = self.project_path / "pyproject.toml"
        self._update_config_with_tomli(context, pyproject_path)

        logger.info("Semantic release configuration completed!")

    def _update_config_with_tomli(self, context: dict, pyproject_path: Path) -> None:
        """Update configuration using tomli_w."""
        if not pyproject_path.exists():
            logger.info("pyproject.toml not found, skipping configuration updates")
            return

        try:
            # Read current pyproject.toml
            with pyproject_path.open("rb") as f:
                pyproject_data = tomli.load(f)

            # Update version_variables path
            project_name = context.get("project_name", "myproject")
            curated_project_name = project_name.replace("-", "_")
            new_init_path = f"src/{curated_project_name}/__init__.py:__version__"

            if "tool" in pyproject_data and "semantic_release" in pyproject_data["tool"]:
                pyproject_data["tool"]["semantic_release"]["version_variables"] = [new_init_path]
                logger.info("Updated __init__.py path to: %s", new_init_path)

                # Update remote type
                git_host = context.get("git_host")
                if git_host:
                    if "remote" not in pyproject_data["tool"]["semantic_release"]:
                        pyproject_data["tool"]["semantic_release"]["remote"] = {}
                    pyproject_data["tool"]["semantic_release"]["remote"]["type"] = git_host
                    logger.info("Updated remote type to: %s", git_host)

                # Write back the updated configuration
                with pyproject_path.open("wb") as f:
                    f.write(tomli_w.dumps(pyproject_data).encode("utf-8"))

        except Exception as e:
            logger.info("Error updating configuration: %s", e)

    def install(self, context: dict) -> None:
        """
        No additional installation steps needed for semantic release.
        """
        pass
