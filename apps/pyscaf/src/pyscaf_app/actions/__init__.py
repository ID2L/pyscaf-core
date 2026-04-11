"""pyscaf-app actions — stress-test of pyscaf-core plugin API."""

import os

from pyscaf_core.actions import discover_actions_from_package


def discover_actions():
    package_dir = os.path.dirname(__file__)
    return discover_actions_from_package(package_dir, "pyscaf_app.actions")
