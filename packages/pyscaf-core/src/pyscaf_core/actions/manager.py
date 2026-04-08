"""Project action manager module — core engine."""

import logging
from pathlib import Path
from typing import Any

import questionary

from pyscaf_core.actions import Action, cli_option_to_key
from pyscaf_core.preference_chain import best_execution_order
from pyscaf_core.preference_chain.model import Node

logger = logging.getLogger(__name__)


class ActionManager:
    """Manager for all project actions."""

    def __init__(
        self,
        project_name: str | Path,
        context: dict[str, Any],
        action_classes: list[type[Action]] | None = None,
        discover: Any = None,
    ):
        self.project_path = Path.cwd() / project_name
        logger.info("Project path: %s", self.project_path)
        self.context = context
        self.actions: list[Action] = []

        if action_classes is not None:
            self._action_classes = action_classes
        elif discover is not None:
            self._action_classes = discover()
        else:
            from pyscaf_core.actions import discover_actions_from_entry_points

            self._action_classes = discover_actions_from_entry_points()

        self._determine_actions()

    def _determine_actions(self) -> None:
        """Determine which actions to include based on configuration using the preference chain logic."""
        nodes: list[Node] = []
        action_class_by_id: dict[str, type[Action]] = {}

        for action_cls in self._action_classes:
            action_id = action_cls.__name__.replace("Action", "").lower()
            depends = getattr(action_cls, "depends", set())
            after = getattr(action_cls, "run_preferably_after", None)

            node = Node(id=action_id, depends=depends, after=after)
            nodes.append(node)
            action_class_by_id[action_id] = action_cls

        logger.debug("Created %d action nodes", len(nodes))

        if not nodes:
            self.actions = []
            return

        order = best_execution_order(nodes)

        logger.debug("Final action execution order: %s", order)

        self.actions = [
            action_class_by_id[action_id](self.project_path)
            for action_id in order
            if action_id in action_class_by_id
        ]

    def run_postfill_hooks(self, context: dict) -> dict:
        """Run all postfill hooks for actions in optimal order."""
        for action in self.actions:
            if action.activate(context):
                for opt in action.cli_options:
                    context_key = cli_option_to_key(opt)
                    if context.get(context_key) is None:
                        continue
                    if opt.visible_when and not opt.visible_when(context):
                        continue
                    if opt.postfill_hook:
                        context = opt.postfill_hook(context)
        return context

    def ask_interactive_questions(self, context: dict) -> dict:
        """Ask all relevant questions for actions in optimal order, updating the context."""
        for action in self.actions:
            if action.activate(context):
                for opt in action.cli_options:
                    context_key = cli_option_to_key(opt)
                    if context.get(context_key) is not None:
                        continue
                    if opt.visible_when and not opt.visible_when(context):
                        continue
                    prompt = opt.prompt or context_key
                    if opt.type == "choice":
                        default = opt.get_default_value()
                    else:
                        default = opt.default() if callable(opt.default) else opt.default
                    if opt.type == "bool":
                        answer = questionary.confirm(prompt, default=bool(default)).ask()
                    elif opt.type == "int":
                        answer = questionary.text(
                            prompt, default=str(default) if default is not None else ""
                        ).ask()
                        answer = int(answer) if answer is not None and answer != "" else None
                    elif opt.type == "choice" and opt.choices:
                        choices = opt.get_choice_displays()
                        default_display = opt.get_default_display()

                        if opt.multiple:
                            answer = questionary.checkbox(
                                prompt, choices=choices, default=default_display
                            ).ask()
                        else:
                            answer = questionary.select(
                                prompt, choices=choices, default=default_display
                            ).ask()

                        if answer:
                            if opt.multiple:
                                converted_answer = []
                                for display in answer:
                                    for choice in opt.choices:
                                        if choice.display == display:
                                            converted_answer.append(choice.key)
                                            break
                                answer = converted_answer
                            else:
                                for choice in opt.choices:
                                    if choice.display == answer:
                                        answer = choice.key
                                        break

                    else:
                        answer = questionary.text(
                            prompt, default=default if default is not None else ""
                        ).ask()
                    context[context_key] = answer
                    if opt.postfill_hook:
                        context = opt.postfill_hook(context)
        return context

    def create_project(self) -> None:
        """Create the project structure and initialize it."""
        self.project_path.mkdir(parents=True, exist_ok=True)

        logger.info("Creating project at: %s", self.project_path)

        for action in self.actions:
            if not action.activate(self.context):
                logger.info("Skipping %s", action.__class__.__name__)
                continue
            action_name = action.__class__.__name__
            logger.info("Creating skeleton for: %s", action_name)
            action.create_skeleton(self.context)

        for action in self.actions:
            if not action.activate(self.context):
                continue
            action_name = action.__class__.__name__
            logger.info("Initializing: %s", action_name)
            action.init(self.context)

        if not self.context.get("no_install", False):
            for action in self.actions:
                if not action.activate(self.context):
                    continue
                action_name = action.__class__.__name__
                logger.info("Installing dependencies for: %s", action_name)
                action.install(self.context)
        else:
            logger.info("Skipping installation.")

        logger.info("Project creation complete!")
