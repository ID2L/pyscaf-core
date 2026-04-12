# cli

CLI framework for pyscaf-core based applications.

This module provides the [`build_cli()`][pyscaf_core.cli.build_cli] factory that creates a complete Click CLI group with dynamic options from all discovered actions, and [`make_main()`][pyscaf_core.cli.make_main] to create an entry point.

See the [Architecture](../architecture.md) guide for how the CLI integrates with the action system.

::: pyscaf_core.cli
