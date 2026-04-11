"""
Jupyter initialization actions.
"""

import logging
import os
import subprocess
from pathlib import Path

from pyscaf_core import Action, CLIOption

logger = logging.getLogger(__name__)


class JupyterAction(Action):
    """Action to initialize Jupyter notebook support in a project."""

    depends = {"core", "git"}
    run_preferably_after = "git"
    cli_options = [
        CLIOption(
            name="--jupyter",
            type="bool",
            help="Handle Jupyter notebook support",
            prompt="Does this project will use Jupyter notebook ?",
            default=False,
        ),
    ]  # Add Jupyter-specific options if needed

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        return context.get("jupyter") is None or context.get("jupyter", True)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for Jupyter notebook support.

        Returns:
            Dictionary mapping paths to content
        """
        project_name = context.get("project_name", "myproject")

        # Read Jupyter documentation
        jupyter_doc_path = Path(__file__).parent / "README.md"
        jupyter_doc = jupyter_doc_path.read_text() if jupyter_doc_path.exists() else ""

        # Create a README for notebooks
        notebook_readme = f"""# {project_name} - Notebooks

This directory contains Jupyter notebooks for the {project_name} project.

{jupyter_doc}
"""

        # Ajout conditionnel du .gitignore si git est activé
        skeleton = {
            Path("notebooks"): None,  # Create main notebook directory
            Path("notebooks/README.md"): notebook_readme,
        }
        if context.get("versionning"):
            gitignore_path = Path(__file__).parent / "template.gitignore"
            gitignore_content = gitignore_path.read_text() if gitignore_path.exists() else ""
            skeleton[Path(".gitignore")] = gitignore_content
        return skeleton

    def install(self, context: dict) -> None:
        """
        Set up the Jupyter kernel for the project.

        This will create a Jupyter kernel specific to this project.
        """
        logger.info("Setting up Jupyter kernel for the project...")

        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Create a Jupyter kernel for this project
            logger.info("Creating Jupyter kernel for this project...")

            project_name = context.get("project_name", "myproject")

            # Remove VIRTUAL_ENV from environment to avoid uv warnings when running inside another venv
            env = os.environ.copy()
            env.pop("VIRTUAL_ENV", None)

            # Run the ipykernel installation via uv
            result = subprocess.call(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "ipykernel",
                    "install",
                    "--user",
                    "--name",
                    project_name,
                    "--display-name",
                    f"{project_name} (uv)",
                ],
                env=env,
                stdin=None,
                stdout=None,
                stderr=None,
            )

            if result == 0:
                logger.info("Jupyter kernel created successfully!")
                logger.info("You can now use the '%s (uv)' kernel in Jupyter.", project_name)
            else:
                logger.info("Jupyter kernel creation exited with code %s", result)

        except FileNotFoundError:
            logger.info("uv or Jupyter not found. Make sure they are installed.")
