# Original Prompt

From `septeo-agentic-scaffolder/KNOWN_ISSUES.md`:

Click options with `multiple=True` default to `()` (empty tuple) when not provided on the command line. In `ask_interactive_questions`, the guard `if context.get(context_key) is not None: continue` treats `()` as an already-answered value and **skips the interactive prompt entirely**.

In interactive mode, the `--bricks` checkbox is never shown for `brick-app` / `brick-package` project types. The user goes straight from "Select project type" to "Enter a name for the brick" — `bricks` stays `()`, no generator action activates, and the command produces zero output.

The same issue affects `run_postfill_hooks` which skips hooks for `None` values but incorrectly runs them on empty tuples.
