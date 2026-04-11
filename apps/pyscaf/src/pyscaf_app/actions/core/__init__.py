"""
Poetry initialization actions.
"""

import logging
import os
import re
import subprocess
from pathlib import Path

import tomli
import tomli_w
from pyscaf_core import Action, CLIOption

logger = logging.getLogger(__name__)


def get_local_git_author():
    """Get the author name from the local git config."""
    try:
        git_name = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
        git_email = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
        default_author = f"{git_name} <{git_email}>"
    except subprocess.CalledProcessError:
        default_author = ""
    return default_author


class CoreAction(Action):
    """Action to initialize a project with uv."""

    depends = set()  # uv is the root action
    run_preferably_after = None
    cli_options = [
        CLIOption(
            name="--author",
            type="str",
            help="Author name",
            prompt="Who is the main author of this project ?",
            default=get_local_git_author,
        ),
    ]

    def __init__(self, project_path):
        super().__init__(project_path)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for Core initialization.

        Returns:
            Dictionary mapping paths to content
        """
        project_name = context.get("project_name", "myproject")
        currated_projet_name = project_name.replace("-", "_")

        # Read uv documentation
        uv_doc_path = Path(__file__).parent / "README.md"
        uv_doc = uv_doc_path.read_text() if uv_doc_path.exists() else ""

        # Add default ruff settings for VSCode
        vscode_settings_path = Path(__file__).parent / "default_settings.json"
        vscode_settings = vscode_settings_path.read_text() if vscode_settings_path.exists() else ""
        # Return skeleton dictionary
        skeleton = {
            Path("README.md"): (f"# {project_name}\n\nA Python project created with pyscaf\n\n{uv_doc}\n"),
            Path(f"src/{currated_projet_name}/__init__.py"): (
                f'"""\n{project_name} package.\n"""\n\n__version__ = "0.0.0"\n'
            ),
            Path(".vscode/settings.json"): vscode_settings if vscode_settings else None,
        }
        return skeleton

    def init(self, context: dict) -> None:
        """
        Initialize Core after skeleton creation.

        This will run 'poetry init' in non-interactive mode.
        """
        logger.info("Initializing core project...")

        try:
            # Change to project directory
            os.chdir(self.project_path)

            # Use subprocess.call to pass control to the terminal
            result = subprocess.call(
                [
                    "uv",
                    "init",
                    "--bare",
                    "--lib",
                    "--no-workspace",
                    "--author-from",
                    "none",
                ],
                # No redirection,
                # allows full terminal interaction
                stdin=None,
                stdout=None,
                stderr=None,
            )

            # Ajout dynamique de la clé authors dans [project] du pyproject.toml
            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                with pyproject_path.open("rb") as f:
                    pyproject_data = tomli.load(f)
                try:
                    # Ensure project properties exists
                    if "project" not in pyproject_data:
                        pyproject_data["project"] = {}
                    if "authors" not in pyproject_data["project"]:
                        pyproject_data["project"]["authors"] = []

                    author = context.get("author", "")
                    if author:
                        match = re.match(r"(?P<name>[^<]+)\s*<(?P<email>[^>]+)>", author)
                        if match:
                            pyproject_data["project"]["authors"].append(
                                {"name": match.group("name").strip(), "email": match.group("email").strip()}
                            )
                        else:
                            pyproject_data["project"]["authors"].append({"name": author.strip()})

                    with pyproject_path.open("wb") as f:
                        f.write(tomli_w.dumps(pyproject_data).encode("utf-8"))
                    logger.info("Added authors configuration in pyproject.toml")
                except Exception as e:
                    logger.info("Section [project] not found or error: %s", e)
            else:
                logger.info("pyproject.toml not found after uv init.")

            if result == 0:
                logger.info("uv initialization successful!")
            else:
                logger.info("uv init exited with code %s", result)

        except FileNotFoundError:
            logger.info("uv not found. Please install it first.")

    def install(self, context: dict) -> None:
        """
        Install dependencies with uv.

        This will run 'uv sync' to install all dependencies.
        """
        super().init(context)

        logger.info("Installing dependencies with uv...")
        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Run uv sync
            logger.info("Running uv sync...")
            result = subprocess.call(["uv", "sync"], stdin=None, stdout=None, stderr=None)

            if result == 0:
                logger.info("uv dependencies installed successfully!")
            else:
                logger.info("uv sync exited with code %s", result)

        except FileNotFoundError:
            logger.info("uv not found. Please install it first.")
            logger.info("https://docs.astral.sh/uv/getting-started/installation")
            return

        # Separate block for VSCode Ruff extension installation
        try:
            logger.info("Installing VSCode Ruff extension...")
            subprocess.call(["code", "--install-extension", "charliermarsh.ruff", "--force"])
        except FileNotFoundError:
            logger.info("VSCode not found. Please install it first:")
            logger.info("https://code.visualstudio.com/download")
