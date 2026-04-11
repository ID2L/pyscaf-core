"""pytest plugin providing ``--action-filter`` for YAML action tests.

Registered via the ``pytest11`` entry-point group in ``pyproject.toml``.
"""


def pytest_addoption(parser):
    group = parser.getgroup("pyscaf-action-tests", "PyScaf Action Test Filtering")
    group.addoption(
        "--action-filter",
        action="store",
        default=None,
        help="Filter action tests by module:test_name (e.g. 'core:test_author')",
    )


def pytest_collection_modifyitems(config, items):
    action_filter = config.getoption("--action-filter", default=None)
    if not action_filter:
        return

    module_filter = None
    test_name_filter = None
    if ":" in action_filter:
        module_filter, test_name_filter = action_filter.split(":", 1)
    else:
        module_filter = action_filter

    selected = []
    deselected = []

    for item in items:
        if hasattr(item, "callspec") and item.callspec.id:
            test_id = item.callspec.id
            if ":" in test_id:
                cur_module, cur_name = test_id.split(":", 1)
                match_mod = not module_filter or cur_module == module_filter
                match_name = not test_name_filter or cur_name == test_name_filter
                if match_mod and match_name:
                    selected.append(item)
                else:
                    deselected.append(item)
            else:
                selected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
