"""
pygluu.kubernetes.terminal.configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for configuration terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

from pathlib import Path
import re
import json
import click
import random
import string

from pygluu.kubernetes.helpers import get_logger, prompt_password
from pygluu.kubernetes.terminal.helpers import confirm_yesno

logger = get_logger("gluu-prompt-config ")


class PromptConfiguration:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.enabled_services = self.settings.get("ENABLED_SERVICES_LIST")

    def prompt_config(self):
        """Prompts for generation of configuration layer
        """
        check_fqdn_provided = False

        while True:
            if not self.settings.get("GLUU_FQDN") or check_fqdn_provided:
                self.settings.set("GLUU_FQDN", click.prompt("Enter Hostname", default="demoexample.gluu.org"))

            regex_bool = re.match(
                '^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.){2,}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]){2,}$',
                # noqa: W605
                self.settings.get("GLUU_FQDN"))

            if regex_bool:
                break
            else:
                check_fqdn_provided = True
                logger.error("Input not FQDN structred. Please enter a FQDN with the format demoexample.gluu.org")

        if not self.settings.get("COUNTRY_CODE"):
            self.settings.set("COUNTRY_CODE", click.prompt("Enter Country Code", default="US"))

        if not self.settings.get("STATE"):
            self.settings.set("STATE", click.prompt("Enter State", default="TX"))

        if not self.settings.get("CITY"):
            self.settings.set("CITY", click.prompt("Enter City", default="Austin"))

        if not self.settings.get("EMAIL"):
            self.settings.set("EMAIL", click.prompt("Enter email", default="support@gluu.org"))

        if not self.settings.get("ORG_NAME"):
            self.settings.set("ORG_NAME", click.prompt("Enter Organization", default="Gluu"))

        if not self.settings.get("ADMIN_PW"):
            self.settings.set("ADMIN_PW", prompt_password("oxTrust"))

        if not self.settings.get("LDAP_PW"):
            if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
                self.settings.set("LDAP_PW", prompt_password("LDAP"))
            else:
                self.settings.set("LDAP_PW", self.settings.get("COUCHBASE_PASSWORD"))
                # set dummy password to pass configuration check. @TODO: Configuration pod should skip check
                if not self.settings.db.get("COUCHBASE_PASSWORD"):
                    self.settings.set("LDAP_PW", "P@ssw0rdummy")

        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube"):
            self.settings.set("IS_GLUU_FQDN_REGISTERED", "N")

        if not self.settings.get("IS_GLUU_FQDN_REGISTERED"):
            self.settings.set("IS_GLUU_FQDN_REGISTERED", confirm_yesno("Are you using a globally resolvable FQDN"))

        if self.settings.get("IS_GLUU_FQDN_REGISTERED") == "N":
            self.enabled_services.append("update-lb-ip")
            self.settings.set("ENABLED_SERVICES_LIST", self.enabled_services)

        if not self.settings.get("MIGRATION_ENABLED"):
            self.settings.set("MIGRATION_ENABLED",
                              confirm_yesno("Are you migrating from the Gluu community edition (VM base)"))

        if self.settings.get("MIGRATION_ENABLED") == "Y":
            if not self.settings.get("MIGRATION_DIR"):
                self.settings.set("MIGRATION_DIR",
                                  click.prompt("Directory holding the community edition migration files",
                                               default="ce-migration"))
            if not self.settings.get("MIGRATION_DATA_FORMAT"):
                while self.settings.get("MIGRATION_DATA_FORMAT") not in ("ldif", "couchbase+json", "spanner+avro",
                                                                         "postgresql+json", "mysql+json"):
                    logger.info("Supported data formats are ldif, couchbase+json, spanner+avro, "
                                "postgresql+json, and mysql+json ")
                    self.settings.set("MIGRATION_DATA_FORMAT",
                                      click.prompt("Migration data-format depending on persistence backend. "
                                                   "Supported data formats are ldif, couchbase+json, spanner+avro, "
                                                   "postgresql+json, and mysql+json ",
                                                   default="ldif"))

        if not self.settings.get("CONTAINER_REGISTRY_SECRET_NAME"):
            self.settings.set(
                "CONTAINER_REGISTRY_SECRET_NAME",
                click.prompt("container registry secret name", default="regcred")
            )

        if not self.settings.get("USE_CUSTOM_SALT"):
            self.settings.set(
                "USE_CUSTOM_SALT",
                confirm_yesno("Are you using custom salt"),
            )

        if self.settings.get("USE_CUSTOM_SALT") == "Y":
            while True:
                if not self.settings.get("SALT"):
                    self.settings.set(
                        "SALT",
                        click.prompt(
                            "Salt for encoding/decoding sensitive data",
                            default="".join(random.choices(string.ascii_letters + string.digits, k=24)),
                        ),
                    )

                salt = self.settings.get("SALT")

                if len(salt) == 24 and salt.isalnum():
                    break

                logger.error("Salt value must be 24 characters of alphanumeric")

                # reset to force prompt
                self.settings.set("SALT", "")

        logger.info("You can mount your FQDN certification and key by placing them inside "
                    "gluu.crt and gluu.key respectivley at the same location pygluu-kubernetes.pyz is at.")
