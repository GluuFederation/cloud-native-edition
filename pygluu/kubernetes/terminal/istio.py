"""
pygluu.kubernetes.terminal.istio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for istio terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click
from pygluu.kubernetes.helpers import get_logger
from pygluu.kubernetes.terminal.helpers import confirm_yesno

logger = get_logger("gluu-prompt-istio  ")


class PromptIstio:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.enabled_services = self.settings.get("ENABLED_SERVICES_LIST")

    def prompt_istio(self):
        """Prompt for Istio
        """
        if not self.settings.get("USE_ISTIO_INGRESS") and self.settings.get("DEPLOYMENT_ARCH") not in (
                "microk8s", "minikube"):
            self.settings.set("USE_ISTIO_INGRESS", confirm_yesno("[Alpha] Would you like to use "
                                                                 "Istio Ingress with Gluu ?"))
        if self.settings.get("USE_ISTIO_INGRESS") == "Y":
            self.settings.set("USE_ISTIO", "Y")

        if not self.settings.get("USE_ISTIO"):
            logger.info("Please follow https://istio.io/latest/docs/ to learn more.")
            logger.info("Istio will auto inject side cars into all pods in Gluus namespace chosen. "
                        "The label istio-injection=enabled will be added to the namespace Gluu will be installed in "
                        "if the namespace does not exist. If it does please run "
                        "kubectl label namespace <namespace> istio-injection=enabled")
            self.settings.set("USE_ISTIO", confirm_yesno("[Alpha] Would you like to use Istio with Gluu ?"))

        if not self.settings.get("ISTIO_SYSTEM_NAMESPACE") and self.settings.get("USE_ISTIO") == "Y":
            self.settings.set("ISTIO_SYSTEM_NAMESPACE", click.prompt("Istio namespace",
                                                                     default="istio-system"))
        if self.settings.get("USE_ISTIO_INGRESS") == "Y":
            self.enabled_services.append("gluu-istio-ingress")
            self.settings.set("ENABLED_SERVICES_LIST", self.enabled_services)

            if not self.settings.get("LB_ADD"):
                self.settings.set("LB_ADD", click.prompt("Istio loadbalancer adderss(eks) or "
                                                         "ip (gke, aks, digital ocean, local)", default=""))
