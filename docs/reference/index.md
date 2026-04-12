# API Reference

Complete reference for the `pyscaf_core` public API.

## Top-Level Exports

The following symbols are available directly from `pyscaf_core`:

| Symbol | Type | Description |
|--------|------|-------------|
| [`Action`][pyscaf_core.actions.Action] | class | Base class for all scaffolder actions |
| [`ActionManager`][pyscaf_core.actions.manager.ActionManager] | class | Orchestrates action discovery, ordering, and execution |
| [`CLIOption`][pyscaf_core.actions.CLIOption] | class | Declares a CLI option for an action |
| [`ChoiceOption`][pyscaf_core.actions.ChoiceOption] | class | Rich choice with separate key/display/value |
| [`build_cli`][pyscaf_core.cli.build_cli] | function | Builds a complete Click CLI group |
| [`make_main`][pyscaf_core.cli.make_main] | function | Creates a `main()` entry point from a CLI group |
| [`cli_option_to_key`][pyscaf_core.actions.cli_option_to_key] | function | Converts a CLI option name to a context key |

## Modules

- [**actions**](actions.md) — Action base class, CLI options, and discovery
- [**cli**](cli.md) — CLI framework (Click integration)
- [**preference_chain**](preference_chain.md) — Dependency resolution algorithm
- [**tools**](tools.md) — TOML utilities
- [**testing**](testing.md) — YAML-driven test framework and pytest plugin
