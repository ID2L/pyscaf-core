from pathlib import Path


def format_toml(path: Path) -> None:
    """Ensures there is exactly one empty line between each section in the TOML file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    formatted_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            while formatted_lines and formatted_lines[-1] == "":
                formatted_lines.pop()
            if formatted_lines:
                formatted_lines.append("")
            formatted_lines.append(line)
        else:
            formatted_lines.append(line)

    path.write_text("\n".join(formatted_lines) + "\n", encoding="utf-8")
