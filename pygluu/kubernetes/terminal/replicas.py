"""
pygluu.kubernetes.terminal.replicas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for terminal replicas prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
import click


class PromptReplicas:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_replicas(self):
        """Prompt number of replicas for Gluu apps
        """
        if not self.settings.get("OXAUTH_REPLICAS"):
            self.settings.set("OXAUTH_REPLICAS", click.prompt("Number of oxAuth replicas", default=1))

        if self.settings.get("ENABLE_FIDO2") == "Y" and not self.settings.get("FIDO2_REPLICAS"):
            self.settings.set("FIDO2_REPLICAS", click.prompt("Number of fido2 replicas", default=1))

        if self.settings.get("ENABLE_SCIM") == "Y" and not self.settings.get("SCIM_REPLICAS"):
            self.settings.set("SCIM_REPLICAS", click.prompt("Number of scim replicas", default=1))

        if not self.settings.get("OXTRUST_REPLICAS"):
            self.settings.set("OXTRUST_REPLICAS", click.prompt("Number of oxTrust replicas", default=1))

        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and not self.settings.get("LDAP_REPLICAS"):
            self.settings.set("LDAP_REPLICAS", click.prompt("Number of LDAP replicas", default=1))

        if self.settings.get("ENABLE_OXSHIBBOLETH") == "Y" and not self.settings.get("OXSHIBBOLETH_REPLICAS"):
            self.settings.set("OXSHIBBOLETH_REPLICAS", click.prompt("Number of oxShibboleth replicas", default=1))

        if self.settings.get("ENABLE_OXPASSPORT") == "Y" and not self.settings.get("OXPASSPORT_REPLICAS"):
            self.settings.set("OXPASSPORT_REPLICAS", click.prompt("Number of oxPassport replicas", default=1))

        if self.settings.get("ENABLE_OXD") == "Y" and not self.settings.get("OXD_SERVER_REPLICAS"):
            self.settings.set("OXD_SERVER_REPLICAS", click.prompt("Number of oxd-server replicas", default=1))

        if self.settings.get("ENABLE_CASA") == "Y" and not self.settings.get("CASA_REPLICAS"):
            self.settings.set("CASA_REPLICAS", click.prompt("Number of Casa replicas", default=1))
