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

from pygluu.kubernetes.helpers import get_logger, prompt_password
from pygluu.kubernetes.terminal.helpers import confirm_yesno

logger = get_logger("gluu-prompt-config ")


class PromptConfiguration:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.config_settings = {"hostname": "", "country_code": "", "state": "", "city": "", "admin_pw": "",
                                "ldap_pw": "", "email": "", "org_name": "", "redis_pw": ""}
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

        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube"):
            self.settings.set("IS_GLUU_FQDN_REGISTERED", "N")

        if not self.settings.get("IS_GLUU_FQDN_REGISTERED"):
            self.settings.set("IS_GLUU_FQDN_REGISTERED", confirm_yesno("Are you using a globally resolvable FQDN"))

        if self.settings.get("IS_GLUU_FQDN_REGISTERED") == "N":
            self.enabled_services.append("update-lb-ip")
            self.settings.set("ENABLED_SERVICES_LIST", self.enabled_services)

        logger.info("You can mount your FQDN certification and key by placing them inside "
                    "gluu.crt and gluu.key respectivley at the same location pygluu-kuberentes.pyz is at.")
        self.generate_main_config()

    def generate_main_config(self):
        """Prepare generate.json and output it
        """
        self.config_settings["hostname"] = self.settings.get("GLUU_FQDN")
        self.config_settings["country_code"] = self.settings.get("COUNTRY_CODE")
        self.config_settings["state"] = self.settings.get("STATE")
        self.config_settings["city"] = self.settings.get("CITY")
        self.config_settings["admin_pw"] = self.settings.get("ADMIN_PW")
        self.config_settings["ldap_pw"] = self.settings.get("LDAP_PW")
        self.config_settings["redis_pw"] = self.settings.get("REDIS_PW")
        if self.settings.get("PERSISTENCE_BACKEND") == "couchbase":
            self.config_settings["ldap_pw"] = self.settings.get("COUCHBASE_PASSWORD")
        self.config_settings["email"] = self.settings.get("EMAIL")
        self.config_settings["org_name"] = self.settings.get("ORG_NAME")
        with open(Path('./config/base/generate.json'), 'w+') as file:
            logger.warning("Main configuration settings has been outputted to file: "
                           "./config/base/generate.json. Please store this file safely or delete it.")
            json.dump(self.config_settings, file)
