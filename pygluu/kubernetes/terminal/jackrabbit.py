"""
pygluu.kubernetes.terminal.jackrabbit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for jackrabbit terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click

from pygluu.kubernetes.helpers import get_logger, prompt_password
from pygluu.kubernetes.terminal.helpers import confirm_yesno
from pygluu.kubernetes.terminal.postgres import PromptPostgres
logger = get_logger("gluu-prompt-jackrabbit")


class PromptJackrabbit:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.postgres = PromptPostgres(self.settings)

    def prompt_jackrabbit(self):
        """Prompts for Jackrabbit content repository
        """
        if not self.settings.get("INSTALL_JACKRABBIT"):
            logger.info("Jackrabbit must be installed. If the following prompt is answered with N it is assumed "
                        "the jackrabbit content repository is either installed locally or remotely")
            self.settings.set("INSTALL_JACKRABBIT",
                              confirm_yesno("Install Jackrabbit content repository", default=True))

        jackrabbit_cluster_prompt = "Is"
        if self.settings.get("INSTALL_JACKRABBIT") == "Y":
            if not self.settings.get("JACKRABBIT_STORAGE_SIZE"):
                self.settings.set("JACKRABBIT_STORAGE_SIZE", click.prompt(
                    "Size of Jackrabbit content repository volume storage", default="4Gi"))
            self.settings.set("JACKRABBIT_URL", "http://jackrabbit:8080")
            jackrabbit_cluster_prompt = "Enable"

        if not self.settings.get("JACKRABBIT_URL"):
            self.settings.set("JACKRABBIT_URL", click.prompt("Please enter jackrabbit url.",
                                                             default="http://jackrabbit:8080"))
        if not self.settings.get("JACKRABBIT_ADMIN_ID"):
            self.settings.set("JACKRABBIT_ADMIN_ID",
                              click.prompt("Please enter Jackrabit admin user", default="admin"))

        if not self.settings.get("JACKRABBIT_ADMIN_PASSWORD"):
            self.settings.set("JACKRABBIT_ADMIN_PASSWORD", prompt_password("jackrabbit-admin", 24))

        if not self.settings.get("JACKRABBIT_CLUSTER"):
            self.settings.set("JACKRABBIT_CLUSTER", confirm_yesno("{} Jackrabbit in cluster mode[beta] "
                                                                  "Recommended in production"
                                                                  .format(jackrabbit_cluster_prompt), default=True))
        if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
            self.postgres.prompt_postgres()
            if not self.settings.get("JACKRABBIT_PG_USER"):
                self.settings.set("JACKRABBIT_PG_USER", click.prompt("Please enter a user for jackrabbit postgres "
                                                                     "database",
                                                                     default="jackrabbit"))

            if not self.settings.get("JACKRABBIT_PG_PASSWORD"):
                self.settings.set("JACKRABBIT_PG_PASSWORD", prompt_password("jackrabbit-postgres"))

            if not self.settings.get("JACKRABBIT_DATABASE"):
                self.settings.set("JACKRABBIT_DATABASE", click.prompt("Please enter jackrabbit postgres database name",
                                                                      default="jackrabbit"))
