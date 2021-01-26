"""
pygluu.kubernetes.terminal.gluugateway
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for gluu gateway terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click
from pygluu.kubernetes.helpers import prompt_password
from pygluu.kubernetes.terminal.postgres import PromptPostgres


class PromptGluuGateway:
    """Prompt is used for prompting users for input used in deploying GluuGateway.
    """

    def __init__(self, settings):
        self.settings = settings
        self.postgres = PromptPostgres(self.settings)

    def prompt_gluu_gateway(self):
        """Prompts for Gluu Gateway
        """
        if self.settings.get("installer-settings.gluuGateway.install") in (None, ''):
            self.settings.set("installer-settings.gluuGateway.install",
                              click.confirm("Install Gluu Gateway Database mode"))

        if self.settings.get("installer-settings.gluuGateway.install"):
            self.settings.set("installer-settings.global.client-api.enabled", True)
            self.postgres.prompt_postgres()
            if self.settings.get("installer-settings.gluuGateway.kong.namespace") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.kong.namespace",
                                  click.prompt("Please enter a namespace for Gluu Gateway(Kong + Gluu plugins)",
                                               default="gluu-gateway"))

            if self.settings.get("installer-settings.gluuGateway.Ui.namespace") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.Ui.namespace", click.prompt(
                    "Please enter a namespace for gluu gateway ui", default="gg-ui"))

            if self.settings.get("installer-settings.gluuGateway.kong.postgresUser") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.kong.postgresUser",
                                  click.prompt("Please enter a user for gluu-gateway postgres database",
                                               default="kong"))

            if self.settings.get("installer-settings.gluuGateway.kong.postgresPassword") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.kong.postgresPassword",
                                  prompt_password("gluu-gateway-postgres"))

            if self.settings.get("installer-settings.gluuGateway.Ui.postgresUser") in (None, ''):

                self.settings.set("installer-settings.gluuGateway.Ui.postgresUser", click.prompt(
                    "Please enter a user for gluu-gateway-ui postgres database", default="konga"))

            if self.settings.get("installer-settings.gluuGateway.Ui.postgresPassword") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.Ui.postgresPassword",
                                  prompt_password("gluu-gateway-ui-postgres"))

            if self.settings.get("installer-settings.gluuGateway.kong.postgresDatabaseName") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.kong.postgresDatabaseName",
                                  click.prompt("Please enter gluu-gateway postgres database name",
                                               default="kong"))

            if self.settings.get("installer-settings.gluuGateway.Ui.postgresDatabaseName") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.Ui.postgresDatabaseName", click.prompt(
                    "Please enter gluu-gateway-ui postgres database name", default="konga"))
