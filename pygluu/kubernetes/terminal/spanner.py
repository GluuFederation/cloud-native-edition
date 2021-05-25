"""
pygluu.kubernetes.terminal.spanner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for spanner terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click


class PromptSpanner:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_spanner(self):
        """Prompts for spanner ids
        """
        if not self.settings.get("GOOGLE_SPANNER_INSTANCE_ID"):
            self.settings.set("GOOGLE_SPANNER_INSTANCE_ID", click.prompt("Please enter the google spanner instance ID.",
                                                                         default=""))

        if not self.settings.get("GOOGLE_SPANNER_DATABASE_ID"):
            self.settings.set("GOOGLE_SPANNER_DATABASE_ID", click.prompt("Please enter the google spanner database ID",
                                                                         default=""))
