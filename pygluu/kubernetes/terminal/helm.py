"""
pygluu.kubernetes.terminal.helm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for helm terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click


class PromptHelm:

    def __init__(self, settings):
        self.settings = settings

    def prompt_helm(self):
        """Prompts for helm installation and returns updated settings.

        :return:
        """
        if not self.settings.get("GLUU_HELM_RELEASE_NAME"):
            self.settings.set("GLUU_HELM_RELEASE_NAME", click.prompt("Please enter Gluu helm name", default="gluu"))

        if not self.settings.get("NGINX_INGRESS_RELEASE_NAME") and self.settings.get("AWS_LB_TYPE") != "alb":
            self.settings.set("NGINX_INGRESS_RELEASE_NAME", click.prompt("Please enter nginx-ingress helm name",
                                                                         default="ningress"))

        if not self.settings.get("NGINX_INGRESS_NAMESPACE") and self.settings.get("AWS_LB_TYPE") != "alb":
            self.settings.set("NGINX_INGRESS_NAMESPACE", click.prompt("Please enter nginx-ingress helm namespace",
                                                                      default="ingress-nginx"))

        if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            if not self.settings.get("KONG_HELM_RELEASE_NAME"):
                self.settings.set("KONG_HELM_RELEASE_NAME", click.prompt("Please enter Gluu Gateway helm name",
                                                                         default="gluu-gateway"))

            if not self.settings.get("GLUU_GATEWAY_UI_HELM_RELEASE_NAME"):
                self.settings.set("GLUU_GATEWAY_UI_HELM_RELEASE_NAME", click.prompt(
                    "Please enter Gluu Gateway UI helm name", default="gluu-gateway-ui"))
