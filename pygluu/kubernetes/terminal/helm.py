"""
pygluu.kubernetes.terminal.helm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for helm terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click
from pygluu.kubernetes.terminal.helpers import confirm_yesno


class PromptHelm:

    def __init__(self, settings):
        self.settings = settings

    def prompt_helm(self):
        """Prompts for helm installation and returns updated settings.

        :return:
        """
        if not self.settings.get("GLUU_HELM_RELEASE_NAME"):
            self.settings.set("GLUU_HELM_RELEASE_NAME", click.prompt("Please enter Gluu helm name", default="gluu"))

        # ALPHA-FEATURE: Multi cluster ldap replication
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and \
                not self.settings.get("GLUU_LDAP_MULTI_CLUSTER"):
            self.settings.set("GLUU_LDAP_MULTI_CLUSTER",
                              confirm_yesno("ALPHA-FEATURE-Are you setting up a multi kubernetes cluster"))

        if self.settings.get("GLUU_LDAP_MULTI_CLUSTER") == "Y":
            if not self.settings.get("GLUU_LDAP_ADVERTISE_ADDRESS"):
                self.settings.set("GLUU_LDAP_ADVERTISE_ADDRESS", click.prompt("Please enter Serf advertise "
                                                                              "address suffix. You must be able to "
                                                                              "resolve this address in your DNS",
                                                                              default="regional.gluu.org"))
            if not self.settings.get("GLUU_LDAP_MUTLI_CLUSTER_REPLICAS"):
                self.settings.set("GLUU_LDAP_MUTLI_CLUSTER_REPLICAS",
                                  int(click.prompt("ALPHA-FEATURE-Enter the number of opendj statefulsets to create."
                                                   " Each will have an advertise address of"
                                                   " RELEASE-NAME-opendj-regional-"
                                                   "{{statefulset number}}-{Serf address suffix }} ", default="1",
                                                   type=click.Choice(["1", "2", "3", "4", "5", "6", "7", "8", "9"]))))

            if not self.settings.get("GLUU_LDAP_SECONDARY_CLUSTER"):
                self.settings.set("GLUU_LDAP_SECONDARY_CLUSTER",
                                  confirm_yesno("ALPHA-FEATURE-Is this a subsequent kubernetes cluster "
                                                "(2nd and above)"))
            if not self.settings.get("GLUU_LDAP_SERF_PEERS") or \
                    not isinstance(self.settings.get("GLUU_LDAP_SERF_PEERS"), list):
                alist = []
                for i in range(self.settings.get("GLUU_LDAP_MUTLI_CLUSTER_REPLICAS")):
                    alist.append(f'{self.settings.get("GLUU_HELM_RELEASE_NAME")}'
                                 f'-opendj-regional-{i}-'
                                 f'{self.settings.get("GLUU_LDAP_ADVERTISE_ADDRESS")}:3094{i}')
                self.settings.set("GLUU_LDAP_SERF_PEERS", alist)

            if not self.settings.get("GLUU_LDAP_MUTLI_CLUSTER_CLUSTER_ID"):
                self.settings.set("GLUU_LDAP_MUTLI_CLUSTER_CLUSTER_ID",
                                  int(click.prompt("ALPHA-FEATURE-Please enter a cluster ID that distinguishes "
                                                   "this cluster from any subsequent clusters. i.e "
                                                   "west, east, north, south, test..", default="test")))
        if not self.settings.get("NGINX_INGRESS_RELEASE_NAME") and self.settings.get("AWS_LB_TYPE") != "alb":
            self.settings.set("NGINX_INGRESS_RELEASE_NAME", click.prompt("Please enter nginx-ingress helm name",
                                                                         default="ningress"))

        if not self.settings.get("NGINX_INGRESS_NAMESPACE") and self.settings.get("AWS_LB_TYPE") != "alb":
            self.settings.set("NGINX_INGRESS_NAMESPACE", click.prompt("Please enter nginx-ingress helm namespace",
                                                                      default="ingress-nginx"))
