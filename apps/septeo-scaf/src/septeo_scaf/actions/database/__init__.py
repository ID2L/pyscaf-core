"""
Database action: generates PostgreSQL/MySQL init scripts.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pyscaf_core import Action, ChoiceOption, CLIOption


def _render_template(template_dir: Path, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)
    return env.get_template(template_name).render(**context)


class DatabaseAction(Action):
    """Generates database initialization scripts."""

    depends = {"core"}
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--database-extensions",
            type="choice",
            help="Database extensions",
            prompt="Database extensions",
            default=0,
            multiple=True,
            choices=[
                ChoiceOption(key="pgvector", display="pgvector (vector similarity)", value="pgvector"),
                ChoiceOption(key="postgis", display="PostGIS (geospatial)", value="postgis"),
            ],
            visible_when=lambda ctx: str(ctx.get("database", "")).startswith("postgres"),
        ),
    ]

    def activate(self, context: dict) -> bool:
        db = context.get("database", "none")
        return db is not None and db != "none"

    def _get_templates_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        templates_dir = self._get_templates_dir()
        database = context.get("database", "none")
        project_name = context.get("project_name", "project")
        extensions = context.get("database_extensions", [])
        if isinstance(extensions, str):
            extensions = [extensions]

        db_version = database.split("-")[1] if "-" in database else ""
        db_type = "postgres" if "postgres" in database else "mysql"

        ctx = {
            "project_name": project_name,
            "database": database,
            "db_type": db_type,
            "db_version": db_version,
            "extensions": extensions,
        }

        return {
            Path(".docker/db/init.sql"): _render_template(templates_dir, "init.sql.j2", ctx),
        }
