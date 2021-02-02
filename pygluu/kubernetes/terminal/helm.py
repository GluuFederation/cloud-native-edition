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
        if self.settings.get("installer-settings.releaseName") in ("None", ''):
            self.settings.set("installer-settings.releaseName",
                              click.prompt("Please enter Gluu helm name", default="gluu"))

        # ALPHA-FEATURE: Multi cluster ldap replication
        if self.settings.get("global.cnPersistenceType") in ("hybrid", "ldap") and \
                not self.settings.get("opendj.multiCluster.enabled"):
            self.settings.set("opendj.multiCluster.enabled",
                              click.confirm("ALPHA-FEATURE-Are you setting up a multi kubernetes cluster"))

        if self.settings.get("opendj.multiCluster.enabled"):
            if self.settings.get("opendj.ports.tcp-serf.nodePort") in (None, ''):
                self.settings.set("opendj.ports.tcp-serf.nodePort",
                                  int(click.prompt("ALPHA-FEATURE-Please enter LDAP serf port (NodePort)",
                                                   default="30946")))
            if self.settings.get("opendj.multiCluster.serfAdvertiseAddr") in (None, ''):
                self.settings.set("opendj.multiCluster.serfAdvertiseAddr",
                                  int(click.prompt("Please enter Serf advertise address",
                                                   default="demoexample.gluu.org:30946")))
            if self.settings.get("opendj.ports.tcp-admin.nodePort") in (None, ''):
                self.settings.set("opendj.ports.tcp-admin.nodePort",
                                  int(click.prompt("ALPHA-FEATURE-Please enter LDAP advertise admin port (NodePort)",
                                                   default="30444")))
            if self.settings.get("opendj.ports.tcp-ldaps.nodePort") in (None, ''):
                self.settings.set("opendj.ports.tcp-ldaps.nodePort",
                                  int(click.prompt("ALPHA-FEATURE-Please enter LDAP advertise LDAPS port (NodePort)",
                                                   default="30636")))
            if self.settings.get("opendj.ports.tcp-repl.nodePort") in (None, ''):
                self.settings.set("opendj.ports.tcp-repl.nodePort",
                                  int(click.prompt(
                                      "ALPHA-FEATURE-Please enter LDAP advertise replication port (NodePort)",
                                      default="30989")))
            if self.settings.get("installer-settings.ldap.subsequentCluster") in (None, ''):
                self.settings.set("installer-settings.ldap.subsequentCluster",
                                  click.confirm("ALPHA-FEATURE-Is this a subsequent kubernetes cluster "
                                                     "( 2nd and above)"))
            if self.settings.get("opendj.multiCluster.serfPeers") in (None, ''):
                self.settings.set("opendj.multiCluster.serfPeers",
                                  click.prompt("ALPHA-FEATURE-Please enter LDAP advertise serf peers as an array",
                                               default="['firstldap.gluu.org:30946', 'secondldap.gluu.org:31946']"))

        if self.settings.get("installer-settings.nginxIngress.releaseName") in (None, '') and \
                self.settings.get("installer-settings.aws.lbType") != "alb":
            self.settings.set("installer-settings.nginxIngress.releaseName",
                              click.prompt("Please enter nginx-ingress helm name",
                                                                            default="ningress"))

        if self.settings.get("installer-settings.nginxIngress.namespace") in (None,'') and self.settings.get("installer-settings.aws.lbType") != "alb":
            self.settings.set("installer-settings.nginxIngress.namespace", click.prompt("Please enter nginx-ingress helm namespace",
                                                                         default="ingress-nginx"))

        if self.settings.get("installer-settings.gluuGateway.install"):
            if self.settings.get("installer-settings.gluuGateway.kong.releaseName") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.kong.releaseName", click.prompt("Please enter Gluu Gateway helm name",
                                                                            default="gluu-gateway"))

            if self.settings.get("installer-settings.gluuGateway.uI.releaseName") in (None, ''):
                self.settings.set("installer-settings.gluuGateway.uI.releaseName", click.prompt(
                    "Please enter Gluu Gateway UI helm name", default="gluu-gateway-ui"))
