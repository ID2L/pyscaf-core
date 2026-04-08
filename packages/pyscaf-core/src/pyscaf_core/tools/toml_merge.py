from pathlib import Path

import tomlkit


def merge_toml_files(input_path: Path, output_path: Path) -> None:
    """Merges all content from input_path TOML file into output_path TOML file.

    Recursively merges sections and avoids duplicates by intelligently combining content.
    """
    input_doc = tomlkit.parse(input_path.read_text(encoding="utf-8")) if input_path.exists() else tomlkit.document()
    output_doc = tomlkit.parse(output_path.read_text(encoding="utf-8")) if output_path.exists() else tomlkit.document()

    def deep_merge(source: dict, dest: dict) -> None:
        for key in source:
            if key in dest:
                if isinstance(source[key], dict) and isinstance(dest[key], dict):
                    deep_merge(source[key], dest[key])
                elif isinstance(source[key], list) and isinstance(dest[key], list):
                    for item in source[key]:
                        if item not in dest[key]:
                            dest[key].append(item)
                else:
                    dest[key] = source[key]
            else:
                dest[key] = source[key]

    deep_merge(input_doc, output_doc)

    output_path.write_text(tomlkit.dumps(output_doc), encoding="utf-8")
