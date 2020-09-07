"""
pygluu.kubernetes.terminal.architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for setup of arch backend in terminal installations.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click


class PromptArch:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_arch(self):
        """Prompts for the kubernetes infrastructure used.
        """
        # TODO: This should be auto-detected
        if not self.settings.get("DEPLOYMENT_ARCH"):
            print("|------------------------------------------------------------------|")
            print("|                     Test Environment Deployments                 |")
            print("|------------------------------------------------------------------|")
            print("| [1]  Microk8s [default]                                          |")
            print("| [2]  Minikube                                                    |")
            print("|------------------------------------------------------------------|")
            print("|                     Cloud Deployments                            |")
            print("|------------------------------------------------------------------|")
            print("| [3] Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)|")
            print("| [4] Google Cloud Engine - Google Kubernetes Engine (GKE)         |")
            print("| [5] Microsoft Azure (AKS)                                        |")
            print("| [6] Digital Ocean [Beta]                                         |")
            print("|------------------------------------------------------------------|")
            print("|                     Local Deployments                            |")
            print("|------------------------------------------------------------------|")
            print("| [7]  Manually provisioned Kubernetes cluster                     |")
            print("|------------------------------------------------------------------|")

            arch_map = {
                1: "microk8s",
                2: "minikube",
                3: "eks",
                4: "gke",
                5: "aks",
                6: "do",
                7: "local",
            }
            choice = click.prompt("Deploy on", default=1)
            self.settings.set("DEPLOYMENT_ARCH", arch_map.get(choice, "microk8s"))
