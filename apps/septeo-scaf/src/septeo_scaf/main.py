"""septeo-scaf CLI entry point — built on pyscaf-core."""

from pyscaf_core import build_cli, make_main

from septeo_scaf import __version__
from septeo_scaf.actions import discover_actions

cli = build_cli(
    app_name="septeo-scaf",
    version=__version__,
    discover=discover_actions,
)

main = make_main(cli)

if __name__ == "__main__":
    main()
