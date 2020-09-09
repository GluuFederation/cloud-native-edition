"""
pygluu.kubernetes.terminal.gluugateway
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for gluu gateway terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click
from pygluu.kubernetes.helpers import prompt_password
from pygluu.kubernetes.terminal.helpers import confirm_yesno
from pygluu.kubernetes.terminal.postgres import PromptPostgres


class PromptGluuGateway:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.enabled_services = self.settings.get("ENABLED_SERVICES_LIST")
        self.postgres = PromptPostgres(self.settings)

    def prompt_gluu_gateway(self):
        """Prompts for Gluu Gateway
        """
        if not self.settings.get("INSTALL_GLUU_GATEWAY"):
            self.settings.set("INSTALL_GLUU_GATEWAY", confirm_yesno("Install Gluu Gateway Database mode"))

        if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            self.enabled_services.append("gluu-gateway-ui")
            self.settings.set("ENABLED_SERVICES_LIST", self.enabled_services)
            self.settings.set("ENABLE_OXD", "Y")
            self.postgres.prompt_postgres()
            if not self.settings.get("KONG_NAMESPACE"):
                self.settings.set("KONG_NAMESPACE", click.prompt("Please enter a namespace for Gluu Gateway",
                                                                 default="gluu-gateway"))

            if not self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"):
                self.settings.set("GLUU_GATEWAY_UI_NAMESPACE", click.prompt(
                    "Please enter a namespace for gluu gateway ui", default="gg-ui"))

            if not self.settings.get("KONG_PG_USER"):
                self.settings.set("KONG_PG_USER", click.prompt("Please enter a user for gluu-gateway postgres database",
                                                               default="kong"))

            if not self.settings.get("KONG_PG_PASSWORD"):
                self.settings.set("KONG_PG_PASSWORD", prompt_password("gluu-gateway-postgres"))

            if not self.settings.get("GLUU_GATEWAY_UI_PG_USER"):
                self.settings.set("GLUU_GATEWAY_UI_PG_USER", click.prompt(
                    "Please enter a user for gluu-gateway-ui postgres database", default="konga"))

            if not self.settings.get("GLUU_GATEWAY_UI_PG_PASSWORD"):
                self.settings.set("GLUU_GATEWAY_UI_PG_PASSWORD", prompt_password("gluu-gateway-ui-postgres"))

            if not self.settings.get("KONG_DATABASE"):
                self.settings.set("KONG_DATABASE", click.prompt("Please enter gluu-gateway postgres database name",
                                                                default="kong"))

            if not self.settings.get("GLUU_GATEWAY_UI_DATABASE"):
                self.settings.set("GLUU_GATEWAY_UI_DATABASE", click.prompt(
                    "Please enter gluu-gateway-ui postgres database name", default="konga"))
