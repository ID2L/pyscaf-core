"""pyscaf-app CLI entry point — built on pyscaf-core."""

from pyscaf_core import build_cli, make_main

from pyscaf_app import __version__
from pyscaf_app.actions import discover_actions

cli = build_cli(
    app_name="pyscaf-app",
    version=__version__,
    discover=discover_actions,
)

main = make_main(cli)

if __name__ == "__main__":
    main()
