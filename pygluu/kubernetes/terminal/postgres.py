"""
pygluu.kubernetes.terminal.postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for postgres terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

import click
from pygluu.kubernetes.terminal.helpers import confirm_yesno


class PromptPostgres:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_postgres(self):
        """Prompts for Postgres.
        """
        if not self.settings.get("INSTALL_POSTGRES"):
            self.settings.set("INSTALL_POSTGRES", confirm_yesno("For the following prompt if N is placed "
                                                                "Postgres is assumed to be"
                                                                " installed or remotely provisioned. "
                                                                "Install Bitnami Postgres chart?",
                                                                default=True))
        if self.settings.get("INSTALL_POSTGRES") == "Y":
            if not self.settings.get("POSTGRES_NAMESPACE"):
                namespace = click.prompt("Please enter a namespace for postgres", default="postgres")
                self.settings.set("POSTGRES_NAMESPACE", namespace)

        if not self.settings.get("POSTGRES_URL"):
            url = click.prompt(
                "Please enter  postgres (remote or local) "
                "URL base name. If postgres is to be installed",
                default=f"postgresql.{self.settings.get('POSTGRES_NAMESPACE')}.svc.cluster.local",
            )
            self.settings.set("POSTGRES_URL", url)
