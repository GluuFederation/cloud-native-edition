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
            if not self.settings.get("GLUU_LDAP_SERF_PORT"):
                self.settings.set("GLUU_LDAP_SERF_PORT",
                                  click.prompt("ALPHA-FEATURE-Please enter LDAP serf port (NodePort)",
                                               default="30946"))
            if not self.settings.get("GLUU_LDAP_ADVERTISE_ADDRESS"):
                self.settings.set("GLUU_LDAP_ADVERTISE_ADDRESS", click.prompt("Please enter Serf advertise address",
                                                                              default="demoexample.gluu.org:30946"))
            if not self.settings.get("GLUU_LDAP_ADVERTISE_ADMIN_PORT"):
                self.settings.set("GLUU_LDAP_ADVERTISE_ADMIN_PORT",
                                  click.prompt("ALPHA-FEATURE-Please enter LDAP advertise admin port (NodePort)", default="30444"))
            if not self.settings.get("GLUU_LDAP_ADVERTISE_LDAPS_PORT"):
                self.settings.set("GLUU_LDAP_ADVERTISE_LDAPS_PORT",
                                  click.prompt("ALPHA-FEATURE-Please enter LDAP advertise LDAPS port (NodePort)", default="30636"))
            if not self.settings.get("GLUU_LDAP_ADVERTISE_REPLICATION_PORT"):
                self.settings.set("GLUU_LDAP_ADVERTISE_REPLICATION_PORT",
                                  click.prompt("ALPHA-FEATURE-Please enter LDAP advertise replication port (NodePort)",
                                               default="30989"))
            if not self.settings.get("GLUU_LDAP_SECONDARY_CLUSTER"):
                self.settings.set("GLUU_LDAP_SECONDARY_CLUSTER",
                                  confirm_yesno("ALPHA-FEATURE-Is this a subsequent kubernetes cluster "
                                                "(2nd and above)"))
            if not self.settings.get("GLUU_LDAP_SERF_PEERS") or \
                    not isinstance(self.settings.get("GLUU_LDAP_SERF_PEERS"), list):
                temp = click.prompt("ALPHA-FEATURE-Please enter LDAP advertise serf peers seperated by a comma with "
                                    "no quotes , or brackets",
                             default="firstldap.gluu.org:30946,secondldap.gluu.org:31946")
                temp = temp.replace(" ", "")
                serf_peers_array = temp.split(",")
                self.settings.set("GLUU_LDAP_SERF_PEERS", list(serf_peers_array))
        if not self.settings.get("NGINX_INGRESS_RELEASE_NAME") and self.settings.get("AWS_LB_TYPE") != "alb":
            self.settings.set("NGINX_INGRESS_RELEASE_NAME", click.prompt("Please enter nginx-ingress helm name",
                                                                         default="ningress"))

        if not self.settings.get("NGINX_INGRESS_NAMESPACE") and self.settings.get("AWS_LB_TYPE") != "alb":
            self.settings.set("NGINX_INGRESS_NAMESPACE", click.prompt("Please enter nginx-ingress helm namespace",
                                                                      default="ingress-nginx"))
