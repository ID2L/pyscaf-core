"""
MCP action: MCP configuration in .agents/mcp/.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action, ChoiceOption, CLIOption


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    """Render a Jinja2 template with the given context."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )
    template = env.get_template(template_name)
    return template.render(**context)


class McpAction(Action):
    """MCP action: generates MCP config in .agents/mcp/."""

    depends = {"agents"}
    run_preferably_after = "agents"
    cli_options = [
        CLIOption(
            name="--mcp-servers",
            type="choice",
            help="MCP servers to include",
            prompt="Select MCP servers",
            default=0,
            multiple=True,
            choices=[
                ChoiceOption(key="context7", display="Context7", value="context7"),
                ChoiceOption(key="playwright", display="Playwright", value="playwright"),
                ChoiceOption(
                    key="starlight", display="Starlight Docs", value="starlight"
                ),
            ],
        ),
    ]

    def _get_templates_dir(self) -> Path:
        """Return the path to the templates directory."""
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        """Create MCP config in .agents/mcp/."""
        templates_dir = self._get_templates_dir()
        ctx = {"project_name": context.get("project_name", "project")}
        raw = context.get("mcp_servers")
        ctx["mcp_servers"] = list(raw) if isinstance(raw, (list, tuple)) else []

        return {
            Path(".agents/mcp/cursor-mcp.json"): _render_template(
                templates_dir, "cursor-mcp.json.j2", ctx
            ),
        }
