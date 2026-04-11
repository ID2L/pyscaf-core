"""
jupyter tools initialization actions.
"""

import logging
import os
from pathlib import Path

import tomli
from pyscaf_core import Action, CLIOption

logger = logging.getLogger(__name__)


class JupyterToolsAction(Action):
    """Action to provide Jupyter notebook manipulation tools."""

    depends = {"jupyter"}
    run_preferably_after = "jupyter"
    cli_options = [
        CLIOption(
            name="--jupyter_tools",
            type="bool",
            help="Add Jupyter notebook manipulation tools",
            prompt="Do you want to add Jupyter notebook manipulation tools ?",
            default=False,
        ),
    ]

    def __init__(self, project_path):
        super().__init__(project_path)

    def activate(self, context: dict) -> bool:
        return (
            context.get("jupyter", True) and context.get("jupyter_tools") is None
            or context.get("jupyter_tools", True)
        )

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """
        Define the filesystem skeleton for Jupyter tools.

        Returns:
            Dictionary mapping paths to content
        """

        # Read configuration file
        config_path = Path(__file__).parent / "config.toml"
        readme_path = Path(__file__).parent / "README.md"
        readme_content = readme_path.read_text() if readme_path.exists() else ""
        config_content = config_path.read_text() if config_path.exists() else ""

        # Parse config.toml to get directory paths
        config_dirs = []
        if config_path.exists():
            try:
                config_data = tomli.loads(config_content)
                if (
                    "tool" in config_data
                    and "pyscaf" in config_data["tool"]
                    and "jupyter_tools" in config_data["tool"]["pyscaf"]
                ):
                    jupyter_tools_config = config_data["tool"]["pyscaf"]["jupyter_tools"]
                    # Extract all directory paths from the config
                    for key, value in jupyter_tools_config.items():
                        if isinstance(value, str) and ("dir" in key or "directory" in key):
                            config_dirs.append(Path(value))
            except Exception as e:
                logger.info("Warning: Could not parse config.toml: %s", e)

        # Copy scripts from the source
        scripts_dir = Path(__file__).parent / "scripts"

        skeleton = {
            Path("src/pyscaf/jupyter_tools"): None,  # Create tools directory
            Path("README.md"): readme_content,  # Add to configuration
        }

        # Add configured directories to skeleton
        for dir_path in config_dirs:
            skeleton[dir_path] = None  # Create directory

        # Add all script files
        if scripts_dir.exists():
            # Add __init__.py for pyscaf directory in src
            skeleton[Path("src/pyscaf/__init__.py")] = ""
            skeleton[Path("src/pyscaf/jupyter_tools/__init__.py")] = ""
            skeleton[Path("src/pyscaf/jupyter_tools/scripts/__init__.py")] = ""

            for script_file in scripts_dir.glob("*.py"):
                script_content = script_file.read_text()
                skeleton[Path(f"src/pyscaf/jupyter_tools/scripts/{script_file.name}")] = script_content

        return skeleton

    def install(self, context: dict) -> None:
        """
        Set up the Jupyter tools for the project.

        This will make the tools executable and create convenience scripts.
        """
        logger.info("Setting up Jupyter tools...")

        try:
            # Ensure we're in the right directory
            os.chdir(self.project_path)

            # Make tools executable (on Unix-like systems)
            tools_dir = Path("tools")
            if tools_dir.exists():
                for script_file in tools_dir.glob("*.py"):
                    try:
                        # Make executable on Unix-like systems
                        script_file.chmod(0o755)
                        logger.info("Made %s executable", script_file.name)
                    except OSError:
                        # On Windows, this will fail but that's okay
                        pass

            logger.info("Jupyter tools setup complete!")
            logger.info("You can now use the tools in the tools/ directory.")

        except Exception as e:
            logger.info("Error setting up Jupyter tools: %s", e)
