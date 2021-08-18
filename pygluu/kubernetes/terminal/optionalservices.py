"""
pygluu.kubernetes.terminal.optionalservices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for optional services terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

import click
from pygluu.kubernetes.terminal.helpers import confirm_yesno


class PromptOptionalServices:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.enabled_services = self.settings.get("ENABLED_SERVICES_LIST")

    def prompt_optional_services(self):
        if not self.settings.get("ENABLE_CACHE_REFRESH"):
            self.settings.set("ENABLE_CACHE_REFRESH", confirm_yesno("Deploy Cr-Rotate"))
        if self.settings.get("ENABLE_CACHE_REFRESH") == "Y":
            self.enabled_services.append("cr-rotate")

        if not self.settings.get("ENABLE_OXAUTH_KEY_ROTATE"):
            self.settings.set("ENABLE_OXAUTH_KEY_ROTATE", confirm_yesno("Deploy Key-Rotation"))

        if self.settings.get("ENABLE_OXAUTH_KEY_ROTATE") == "Y":
            self.enabled_services.append("oxauth-key-rotation")
            if not self.settings.get("OXAUTH_KEYS_LIFE"):
                self.settings.set("OXAUTH_KEYS_LIFE", click.prompt("oxAuth keys life in hours", default=48))

        if not self.settings.get("ENABLE_OXPASSPORT"):
            self.settings.set("ENABLE_OXPASSPORT", confirm_yesno("Deploy Passport"))
        if self.settings.get("ENABLE_OXPASSPORT") == "Y":
            self.enabled_services.append("oxpassport")
            self.settings.set("ENABLE_OXPASSPORT_BOOLEAN", "true")

        if not self.settings.get("ENABLE_OXSHIBBOLETH"):
            self.settings.set("ENABLE_OXSHIBBOLETH", confirm_yesno("Deploy Shibboleth SAML IDP"))
        if self.settings.get("ENABLE_OXSHIBBOLETH") == "Y":
            self.enabled_services.append("oxshibboleth")
            self.settings.set("ENABLE_SAML_BOOLEAN", "true")

        if not self.settings.get("ENABLE_CASA"):
            self.settings.set("ENABLE_CASA", confirm_yesno("Deploy Casa"))
        if self.settings.get("ENABLE_CASA") == "Y":
            self.enabled_services.append("casa")
            self.settings.set("ENABLE_CASA_BOOLEAN", "true")
            self.settings.set("ENABLE_OXD", "Y")

        if not self.settings.get("ENABLE_FIDO2"):
            self.settings.set("ENABLE_FIDO2", confirm_yesno("Deploy fido2"))
        if self.settings.get("ENABLE_FIDO2") == "Y":
            self.enabled_services.append("fido2")

        if not self.settings.get("ENABLE_SCIM"):
            self.settings.set("ENABLE_SCIM", confirm_yesno("Deploy scim"))
        if self.settings.get("ENABLE_SCIM") == "Y":
            if not self.settings.get("GLUU_SCIM_PROTECTION_MODE"):
                self.settings.set("GLUU_SCIM_PROTECTION_MODE", click.prompt("SCIM Protection mode", default="OAUTH",
                                                                       type=click.Choice(["OAUTH", "TEST", "UMA"])))
            self.enabled_services.append("scim")

        if not self.settings.get("ENABLE_OXD"):
            self.settings.set("ENABLE_OXD", confirm_yesno("Deploy oxd server"))

        if self.settings.get("ENABLE_OXD") == "Y":
            self.enabled_services.append("oxd-server")
            if not self.settings.get("OXD_APPLICATION_KEYSTORE_CN"):
                self.settings.set("OXD_APPLICATION_KEYSTORE_CN", click.prompt("oxd server application keystore name",
                                                                              default="oxd-server"))
            if not self.settings.get("OXD_ADMIN_KEYSTORE_CN"):
                self.settings.set("OXD_ADMIN_KEYSTORE_CN", click.prompt("oxd server admin keystore name",
                                                                        default="oxd-server"))

        if not self.settings.get("ENABLE_OXTRUST_API"):
            self.settings.set("ENABLE_OXTRUST_API", confirm_yesno("Enable oxTrust API"))

        if self.settings.get("ENABLE_OXTRUST_API"):
            self.settings.set("ENABLE_OXTRUST_API_BOOLEAN", "true")
            if not self.settings.get("ENABLE_OXTRUST_TEST_MODE"):
                self.settings.set("ENABLE_OXTRUST_TEST_MODE", confirm_yesno("Enable oxTrust Test Mode"))
        if self.settings.get("ENABLE_OXTRUST_TEST_MODE") == "Y":
            self.settings.set("ENABLE_OXTRUST_TEST_MODE_BOOLEAN", "true")
        self.settings.set("ENABLED_SERVICES_LIST", self.enabled_services)
