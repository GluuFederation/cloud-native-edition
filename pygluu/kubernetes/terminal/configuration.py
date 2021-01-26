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

logger = get_logger("gluu-prompt-config ")


class PromptConfiguration:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.config_settings = {"hostname": "", "country_code": "", "state": "", "city": "", "admin_pw": "",
                                "ldap_pw": "", "email": "", "org_name": "", "redis_pw": ""}

    def prompt_config(self):
        """Prompts for generation of configuration layer
        """
        check_fqdn_provided = False

        while True:
            if self.settings.get("global.fqdn") in (None, '') or check_fqdn_provided:
                self.settings.set("global.fqdn", click.prompt("Enter Hostname", default="demoexample.gluu.org"))

            regex_bool = re.match(
                '^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.){2,}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]){2,}$',
                # noqa: W605
                self.settings.get("global.fqdn"))

            if regex_bool:
                break
            else:
                check_fqdn_provided = True
                logger.error("Input not FQDN structred. Please enter a FQDN with the format demoexample.gluu.org")

        if self.settings.get("config.countryCode") in (None, ''):
            self.settings.set("config.countryCode", click.prompt("Enter Country Code", default="US"))

        if self.settings.get("config.state") in (None, ''):
            self.settings.set("config.state", click.prompt("Enter State", default="TX"))

        if self.settings.get("config.city") in (None, ''):
            self.settings.set("config.city", click.prompt("Enter City", default="Austin"))

        if self.settings.get("config.email") in (None, ''):
            self.settings.set("config.email", click.prompt("Enter email", default="support@gluu.org"))

        if self.settings.get("config.orgName") in (None, ''):
            self.settings.set("config.orgName", click.prompt("Enter Organization", default="Gluu"))

        if self.settings.get("config.adminPassword") in (None, ''):
            self.settings.set("config.adminPassword", prompt_password("Admin GUI"))

        if self.settings.get("config.ldapPassword") in (None, ''):
            if self.settings.get("global.cnPersistenceType") in ("hybrid", "ldap"):
                self.settings.set("config.ldapPassword", prompt_password("OpenDJ"))
            else:
                self.settings.set("config.ldapPassword", self.settings.get("config.configmap.cnCouchbasePass"))

        if self.settings.get("global.storageClass.provisioner") in ("microk8s.io/hostpath", "k8s.io/minikube-hostpath"):
            self.settings.set("global.isFqdnRegistered", False)

        if self.settings.get("global.isFqdnRegistered") in (None, ''):
            self.settings.set("global.isFqdnRegistered", click.confirm("Are you using a globally resolvable FQDN"))

        logger.info("You can mount your FQDN certification and key by placing them inside "
                    "gluu.crt and gluu.key respectivley at the same location pygluu-kubernetes.pyz is at.")
