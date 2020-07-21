"""
pygluu.kubernetes.prompt
~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

from pathlib import Path
import ipaddress
import re
import shutil
import json
import base64

import click

from .kubeapi import Kubernetes
from .common import update_settings_json_file, get_logger, exec_cmd, prompt_password, get_supported_versions

logger = get_logger("gluu-prompt        ")


def confirm_yesno(text, *args, **kwargs):
    """Like ``click.confirm`` but returns ``Y`` or ``N`` character
    instead of boolean.
    """
    default = "[N]"
    # Default is always N unless default is set in kwargs
    if "default" in kwargs and kwargs["default"]:
        default = "[Y]"

    confirmed = click.confirm(f"{text} {default}", *args, **kwargs)
    return "Y" if confirmed else "N"


class Prompt:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, accept_license=False, version=""):
        self.settings = self.default_settings
        self.kubernetes = Kubernetes()
        self.get_settings()
        self.config_settings = {"hostname": "", "country_code": "", "state": "", "city": "", "admin_pw": "",
                                "ldap_pw": "", "email": "", "org_name": "", "redis_pw": ""}

        if accept_license:
            self.settings["ACCEPT_GLUU_LICENSE"] = "Y"
        self.prompt_license()

        if not self.settings["GLUU_VERSION"]:
            self.settings["GLUU_VERSION"] = version
        self.prompt_version()

    @property
    def default_settings(self):
        default_settings = dict(ACCEPT_GLUU_LICENSE="",
                                GLUU_VERSION="",
                                TEST_ENVIRONMENT="",
                                GLUU_UPGRADE_TARGET_VERSION="",
                                GLUU_HELM_RELEASE_NAME="",
                                NGINX_INGRESS_RELEASE_NAME="",
                                NGINX_INGRESS_NAMESPACE="",
                                INSTALL_GLUU_GATEWAY="",
                                POSTGRES_NAMESPACE="",
                                KONG_NAMESPACE="",
                                GLUU_GATEWAY_UI_NAMESPACE="",
                                KONG_PG_USER="",
                                KONG_PG_PASSWORD="",
                                GLUU_GATEWAY_UI_PG_USER="",
                                GLUU_GATEWAY_UI_PG_PASSWORD="",
                                KONG_DATABASE="",
                                GLUU_GATEWAY_UI_DATABASE="",
                                POSTGRES_REPLICAS="",
                                POSTGRES_URL="",
                                KONG_HELM_RELEASE_NAME="",
                                GLUU_GATEWAY_UI_HELM_RELEASE_NAME="",
                                NODES_IPS=[],
                                NODES_ZONES=[],
                                NODES_NAMES=[],
                                NODE_SSH_KEY="",
                                HOST_EXT_IP="",
                                VERIFY_EXT_IP="",
                                AWS_LB_TYPE="",
                                USE_ARN="",
                                ARN_AWS_IAM="",
                                LB_ADD="",
                                REDIS_URL="",
                                REDIS_TYPE="",
                                REDIS_PW="",
                                REDIS_USE_SSL="false",
                                REDIS_SSL_TRUSTSTORE="",
                                REDIS_SENTINEL_GROUP="",
                                REDIS_MASTER_NODES="",
                                REDIS_NODES_PER_MASTER="",
                                REDIS_NAMESPACE="",
                                INSTALL_REDIS="",
                                INSTALL_JACKRABBIT="",
                                JACKRABBIT_STORAGE_SIZE="",
                                JACKRABBIT_URL="",
                                JACKRABBIT_USER="",
                                DEPLOYMENT_ARCH="",
                                PERSISTENCE_BACKEND="",
                                INSTALL_COUCHBASE="",
                                COUCHBASE_NAMESPACE="",
                                COUCHBASE_VOLUME_TYPE="",
                                COUCHBASE_CLUSTER_NAME="",
                                COUCHBASE_URL="",
                                COUCHBASE_USER="",
                                COUCHBASE_PASSWORD="",
                                COUCHBASE_CRT="",
                                COUCHBASE_CN="",
                                COUCHBASE_SUBJECT_ALT_NAME="",
                                COUCHBASE_CLUSTER_FILE_OVERRIDE="",
                                COUCHBASE_USE_LOW_RESOURCES="",
                                COUCHBASE_DATA_NODES="",
                                COUCHBASE_QUERY_NODES="",
                                COUCHBASE_INDEX_NODES="",
                                COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES="",
                                COUCHBASE_GENERAL_STORAGE="",
                                COUCHBASE_DATA_STORAGE="",
                                COUCHBASE_INDEX_STORAGE="",
                                COUCHBASE_QUERY_STORAGE="",
                                COUCHBASE_ANALYTICS_STORAGE="",
                                COUCHBASE_INCR_BACKUP_SCHEDULE="",
                                COUCHBASE_FULL_BACKUP_SCHEDULE="",
                                COUCHBASE_BACKUP_RETENTION_TIME="",
                                COUCHBASE_BACKUP_STORAGE_SIZE="",
                                LDAP_BACKUP_SCHEDULE="",
                                NUMBER_OF_EXPECTED_USERS="",
                                EXPECTED_TRANSACTIONS_PER_SEC="",
                                USING_CODE_FLOW="",
                                USING_SCIM_FLOW="",
                                USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW="",
                                DEPLOY_MULTI_CLUSTER="",
                                HYBRID_LDAP_HELD_DATA="",
                                LDAP_JACKRABBIT_VOLUME="",
                                APP_VOLUME_TYPE="",
                                LDAP_STATIC_VOLUME_ID="",
                                LDAP_STATIC_DISK_URI="",
                                GLUU_CACHE_TYPE="",
                                GLUU_NAMESPACE="",
                                GLUU_FQDN="",
                                COUNTRY_CODE="",
                                STATE="",
                                EMAIL="",
                                CITY="",
                                ORG_NAME="",
                                GMAIL_ACCOUNT="",
                                GOOGLE_NODE_HOME_DIR="",
                                IS_GLUU_FQDN_REGISTERED="",
                                LDAP_PW="",
                                ADMIN_PW="",
                                OXD_APPLICATION_KEYSTORE_CN="",
                                OXD_ADMIN_KEYSTORE_CN="",
                                LDAP_STORAGE_SIZE="",
                                OXAUTH_REPLICAS="",
                                OXTRUST_REPLICAS="",
                                LDAP_REPLICAS="",
                                OXSHIBBOLETH_REPLICAS="",
                                OXPASSPORT_REPLICAS="",
                                OXD_SERVER_REPLICAS="",
                                CASA_REPLICAS="",
                                RADIUS_REPLICAS="",
                                FIDO2_REPLICAS="",
                                SCIM_REPLICAS="",
                                ENABLE_OXTRUST_API="",
                                ENABLE_OXTRUST_TEST_MODE="",
                                ENABLE_CACHE_REFRESH="",
                                ENABLE_OXD="",
                                ENABLE_FIDO2="",
                                ENABLE_SCIM="",
                                ENABLE_RADIUS="",
                                ENABLE_OXPASSPORT="",
                                ENABLE_OXSHIBBOLETH="",
                                ENABLE_CASA="",
                                ENABLE_OXAUTH_KEY_ROTATE="",
                                ENABLE_OXTRUST_API_BOOLEAN="false",
                                ENABLE_OXTRUST_TEST_MODE_BOOLEAN="false",
                                ENABLE_RADIUS_BOOLEAN="false",
                                ENABLE_OXPASSPORT_BOOLEAN="false",
                                ENABLE_CASA_BOOLEAN="false",
                                ENABLE_SAML_BOOLEAN="false",
                                OXAUTH_KEYS_LIFE="",
                                EDIT_IMAGE_NAMES_TAGS="",
                                CASA_IMAGE_NAME="",
                                CASA_IMAGE_TAG="",
                                CONFIG_IMAGE_NAME="",
                                CONFIG_IMAGE_TAG="",
                                CACHE_REFRESH_ROTATE_IMAGE_NAME="",
                                CACHE_REFRESH_ROTATE_IMAGE_TAG="",
                                CERT_MANAGER_IMAGE_NAME="",
                                CERT_MANAGER_IMAGE_TAG="",
                                LDAP_IMAGE_NAME="",
                                LDAP_IMAGE_TAG="",
                                JACKRABBIT_IMAGE_NAME="",
                                JACKRABBIT_IMAGE_TAG="",
                                OXAUTH_IMAGE_NAME="",
                                OXAUTH_IMAGE_TAG="",
                                FIDO2_IMAGE_NAME="",
                                FIDO2_IMAGE_TAG="",
                                SCIM_IMAGE_NAME="",
                                SCIM_IMAGE_TAG="",
                                OXD_IMAGE_NAME="",
                                OXD_IMAGE_TAG="",
                                OXPASSPORT_IMAGE_NAME="",
                                OXPASSPORT_IMAGE_TAG="",
                                OXSHIBBOLETH_IMAGE_NAME="",
                                OXSHIBBOLETH_IMAGE_TAG="",
                                OXTRUST_IMAGE_NAME="",
                                OXTRUST_IMAGE_TAG="",
                                PERSISTENCE_IMAGE_NAME="",
                                PERSISTENCE_IMAGE_TAG="",
                                RADIUS_IMAGE_NAME="",
                                RADIUS_IMAGE_TAG="",
                                GLUU_GATEWAY_IMAGE_NAME="",
                                GLUU_GATEWAY_IMAGE_TAG="",
                                GLUU_GATEWAY_UI_IMAGE_NAME="",
                                GLUU_GATEWAY_UI_IMAGE_TAG="",
                                UPGRADE_IMAGE_NAME="",
                                UPGRADE_IMAGE_TAG="",
                                CONFIRM_PARAMS="N",
                                )
        return default_settings

    def get_settings(self):
        """Get merged settings (default and custom settings from json file).
        """
        # Check if running in container and settings.json mounted
        try:
            shutil.copy(Path("./installer-settings.json"), "./settings.json")
        except FileNotFoundError:
            logger.info("No installation settings mounted as /installer-settings.json. Checking settings.json...")
        filename = Path("./settings.json")
        try:
            with open(filename) as f:
                custom_settings = json.load(f)
            self.settings.update(custom_settings)
        except FileNotFoundError:
            pass

    def prompt_version(self):
        """Prompts for Gluu versions
        """
        versions, version_number = get_supported_versions()

        if not self.settings["GLUU_VERSION"]:
            self.settings["GLUU_VERSION"] = click.prompt(
                "Please enter the current version of Gluu or the version to be installed",
                default=version_number,
            )

        image_names_and_tags = versions.get(self.settings["GLUU_VERSION"], {})
        self.settings.update(image_names_and_tags)

    def confirm_params(self):
        """Formats output of settings from prompts to the user. Passwords are not displayed.
        """
        hidden_settings = ["NODES_IPS", "NODES_ZONES", "NODES_NAMES",
                           "COUCHBASE_PASSWORD", "LDAP_PW", "ADMIN_PW", "REDIS_PW",
                           "COUCHBASE_SUBJECT_ALT_NAME", "KONG_PG_PASSWORD", "GLUU_GATEWAY_UI_PG_PASSWORD"]
        print("{:<1} {:<40} {:<10} {:<35} {:<1}".format('|', 'Setting', '|', 'Value', '|'))
        for k, v in self.settings.items():
            if k not in hidden_settings:
                print("{:<1} {:<40} {:<10} {:<35} {:<1}".format('|', k, '|', v, '|'))

        if click.confirm("Please confirm the above settings"):
            self.settings["CONFIRM_PARAMS"] = "Y"
        else:
            self.settings = self.default_settings
            self.check_settings_and_prompt

    @property
    def prompt_helm(self):
        """Prompts for helm installation and returns updated settings.

        :return:
        """
        if not self.settings["GLUU_HELM_RELEASE_NAME"]:
            self.settings["GLUU_HELM_RELEASE_NAME"] = click.prompt("Please enter Gluu helm name", default="gluu")

        if not self.settings["NGINX_INGRESS_RELEASE_NAME"]:
            self.settings["NGINX_INGRESS_RELEASE_NAME"] = click.prompt("Please enter nginx-ingress helm name",
                                                                       default="ningress")

        if not self.settings["NGINX_INGRESS_NAMESPACE"]:
            self.settings["NGINX_INGRESS_NAMESPACE"] = click.prompt("Please enter nginx-ingress helm namespace",
                                                                    default="ingress-nginx")

        if self.settings["INSTALL_GLUU_GATEWAY"] == "Y":
            if not self.settings["KONG_HELM_RELEASE_NAME"]:
                self.settings["KONG_HELM_RELEASE_NAME"] = click.prompt("Please enter Gluu Gateway helm name",
                                                                       default="gluu-gateway")

            if not self.settings["GLUU_GATEWAY_UI_HELM_RELEASE_NAME"]:
                self.settings["GLUU_GATEWAY_UI_HELM_RELEASE_NAME"] = click.prompt(
                    "Please enter Gluu Gateway UI helm name", default="gluu-gateway-ui")

        update_settings_json_file(self.settings)
        return self.settings

    @property
    def prompt_upgrade(self):
        """Prompts for upgrade and returns updated settings.

        :return:
        """
        versions, version_number = get_supported_versions()

        if not self.settings["GLUU_UPGRADE_TARGET_VERSION"]:
            self.settings["GLUU_UPGRADE_TARGET_VERSION"] = click.prompt(
                "Please enter the version to upgrade Gluu to", default=version_number,
            )

        image_names_and_tags = versions.get(self.settings["GLUU_UPGRADE_TARGET_VERSION"], {})
        self.settings.update(image_names_and_tags)
        update_settings_json_file(self.settings)
        return self.settings

    def prompt_image_name_tag(self):
        """Manual prompts for image names and tags if changed from default or at a different repository.
        """

        def prompt_and_set_setting(service, image_name_key, image_tag_key):
            self.settings[image_name_key] = click.prompt(f"{service} image name", default=self.settings[image_name_key])
            self.settings[image_tag_key] = click.prompt(f"{service} image tag", default=self.settings[image_tag_key])

        if not self.settings["EDIT_IMAGE_NAMES_TAGS"]:
            self.settings["EDIT_IMAGE_NAMES_TAGS"] = confirm_yesno(
                "Would you like to manually edit the image source/name and tag")

        if self.settings["EDIT_IMAGE_NAMES_TAGS"] == "Y":
            # CASA
            if self.settings["ENABLE_CASA"] == "Y":
                prompt_and_set_setting("Casa", "CASA_IMAGE_NAME", "CASA_IMAGE_TAG")
            # CONFIG
            prompt_and_set_setting("Config", "CONFIG_IMAGE_NAME", "CONFIG_IMAGE_TAG")
            # CACHE_REFRESH_ROTATE
            if self.settings["ENABLE_CACHE_REFRESH"] == "Y":
                prompt_and_set_setting("CR-rotate", "CACHE_REFRESH_ROTATE_IMAGE_NAME", "CACHE_REFRESH_ROTATE_IMAGE_TAG")
            # KEY_ROTATE
            if self.settings["ENABLE_OXAUTH_KEY_ROTATE"] == "Y":
                prompt_and_set_setting("Key rotate", "CERT_MANAGER_IMAGE_NAME", "CERT_MANAGER_IMAGE_TAG")
            # LDAP
            if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                    self.settings["PERSISTENCE_BACKEND"] == "ldap":
                prompt_and_set_setting("WrenDS", "LDAP_IMAGE_NAME", "LDAP_IMAGE_TAG")
            # Jackrabbit
            prompt_and_set_setting("jackrabbit", "JACKRABBIT_IMAGE_NAME", "JACKRABBIT_IMAGE_TAG")
            # OXAUTH
            prompt_and_set_setting("oxAuth", "OXAUTH_IMAGE_NAME", "OXAUTH_IMAGE_TAG")
            # OXD
            if self.settings["ENABLE_OXD"] == "Y":
                prompt_and_set_setting("OXD server", "OXD_IMAGE_NAME", "OXD_IMAGE_TAG")
            # OXPASSPORT
            if self.settings["ENABLE_OXPASSPORT"] == "Y":
                prompt_and_set_setting("oxPassport", "OXPASSPORT_IMAGE_NAME", "OXPASSPORT_IMAGE_TAG")
            # OXSHIBBBOLETH
            if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
                prompt_and_set_setting("oxShibboleth", "OXSHIBBOLETH_IMAGE_NAME", "OXSHIBBOLETH_IMAGE_TAG")
            # OXTRUST
            prompt_and_set_setting("oxTrust", "OXTRUST_IMAGE_NAME", "OXTRUST_IMAGE_TAG")
            # PERSISTENCE
            prompt_and_set_setting("Persistence", "PERSISTENCE_IMAGE_NAME", "PERSISTENCE_IMAGE_TAG")
            # RADIUS
            if self.settings["ENABLE_RADIUS"] == "Y":
                prompt_and_set_setting("Radius", "RADIUS_IMAGE_NAME", "RADIUS_IMAGE_TAG")
            # Gluu-Gateway
            if self.settings["INSTALL_GLUU_GATEWAY"] == "Y":
                prompt_and_set_setting("Gluu-Gateway", "GLUU_GATEWAY_IMAGE_NAME", "GLUU_GATEWAY_IMAGE_TAG")
                # Gluu-Gateway-UI
                prompt_and_set_setting("Gluu-Gateway-UI", "GLUU_GATEWAY_UI_IMAGE_NAME", "GLUU_GATEWAY_UI_IMAGE_TAG")
            self.settings["EDIT_IMAGE_NAMES_TAGS"] = "N"
        update_settings_json_file(self.settings)

    def prompt_volumes_identifier(self):
        """Prompts for Static volume IDs.
        """
        if self.settings["PERSISTENCE_BACKEND"] in ("hybrid", "ldap") and not self.settings["LDAP_STATIC_VOLUME_ID"]:
            logger.info("EBS Volume ID example: vol-049df61146c4d7901")
            logger.info("Persistent Disk Name example: "
                        "gke-demoexamplegluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd")
            self.settings["LDAP_STATIC_VOLUME_ID"] = click.prompt(
                "Please enter Persistent Disk Name or EBS Volume ID for LDAP")
        update_settings_json_file(self.settings)

    def prompt_disk_uris(self):
        """Prompts for static volume Disk URIs (AKS)
        """
        if self.settings["PERSISTENCE_BACKEND"] in ("hybrid", "ldap") and not self.settings["LDAP_STATIC_DISK_URI"]:
            logger.info("DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                        "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk")
            self.settings["LDAP_STATIC_DISK_URI"] = click.prompt("Please enter the disk uri for LDAP")
        update_settings_json_file(self.settings)

    def prompt_gke(self):
        """GKE prompts
        """
        if not self.settings["GMAIL_ACCOUNT"]:
            self.settings["GMAIL_ACCOUNT"] = click.prompt("Please enter valid email for Google Cloud account")

        if self.settings["APP_VOLUME_TYPE"] == 11:
            for node_name in self.settings["NODES_NAMES"]:
                for zone in self.settings["NODES_ZONES"]:
                    response, error, retcode = exec_cmd("gcloud compute ssh user@{} --zone={} "
                                                        "--command='echo $HOME'".format(node_name, zone))
                    self.settings["GOOGLE_NODE_HOME_DIR"] = str(response, "utf-8")
                    if self.settings["GOOGLE_NODE_HOME_DIR"]:
                        break
                if self.settings["GOOGLE_NODE_HOME_DIR"]:
                    break
        update_settings_json_file(self.settings)

    def prompt_config(self):
        """Prompts for generation of configuration layer
        """
        check_fqdn_provided = False

        while True:
            if not self.settings["GLUU_FQDN"] or check_fqdn_provided:
                self.settings["GLUU_FQDN"] = click.prompt("Enter Hostname", default="demoexample.gluu.org")

            regex_bool = re.match(
                '^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.){2,}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]){2,}$',
                # noqa: W605
                self.settings["GLUU_FQDN"])

            if regex_bool:
                break
            else:
                check_fqdn_provided = True
                logger.error("Input not FQDN structred. Please enter a FQDN with the format demoexample.gluu.org")

        if not self.settings["COUNTRY_CODE"]:
            self.settings["COUNTRY_CODE"] = click.prompt("Enter Country Code", default="US")

        if not self.settings["STATE"]:
            self.settings["STATE"] = click.prompt("Enter State", default="TX")

        if not self.settings["CITY"]:
            self.settings["CITY"] = click.prompt("Enter City", default="Austin")

        if not self.settings["EMAIL"]:
            self.settings["EMAIL"] = click.prompt("Enter email", default="support@gluu.org")

        if not self.settings["ORG_NAME"]:
            self.settings["ORG_NAME"] = click.prompt("Enter Organization", default="Gluu")

        if not self.settings["ADMIN_PW"]:
            self.settings["ADMIN_PW"] = prompt_password("oxTrust")

        if not self.settings["LDAP_PW"]:
            if self.settings["PERSISTENCE_BACKEND"] in ("hybrid", "ldap"):
                self.settings["LDAP_PW"] = prompt_password("LDAP")
            else:
                self.settings["LDAP_PW"] = self.settings["COUCHBASE_PASSWORD"]

        if self.settings["DEPLOYMENT_ARCH"] in ("microk8s", "minikube"):
            self.settings["IS_GLUU_FQDN_REGISTERED"] = "N"

        if not self.settings["IS_GLUU_FQDN_REGISTERED"]:
            self.settings["IS_GLUU_FQDN_REGISTERED"] = confirm_yesno("Are you using a globally resolvable FQDN")

        logger.info("You can mount your FQDN certification and key by placing them inside "
                    "gluu.crt and gluu.key respectivley at the same location pygluu-kuberentest.pyz is at.")
        self.generate_main_config()
        update_settings_json_file(self.settings)

    def generate_main_config(self):
        """Prepare generate.json and output it
        """
        self.config_settings["hostname"] = self.settings["GLUU_FQDN"]
        self.config_settings["country_code"] = self.settings["COUNTRY_CODE"]
        self.config_settings["state"] = self.settings["STATE"]
        self.config_settings["city"] = self.settings["CITY"]
        self.config_settings["admin_pw"] = self.settings["ADMIN_PW"]
        self.config_settings["ldap_pw"] = self.settings["LDAP_PW"]
        self.config_settings["redis_pw"] = self.settings["REDIS_PW"]
        if self.settings["PERSISTENCE_BACKEND"] == "couchbase":
            self.config_settings["ldap_pw"] = self.settings["COUCHBASE_PASSWORD"]
        self.config_settings["email"] = self.settings["EMAIL"]
        self.config_settings["org_name"] = self.settings["ORG_NAME"]
        with open(Path('./config/base/generate.json'), 'w+') as file:
            logger.warning("Main configuration settings has been outputted to file: "
                           "./config/base/generate.json. Please store this file safely or delete it.")
            json.dump(self.config_settings, file)

    def prompt_jackrabbit(self):
        """Prompts for Jackrabbit content repository
        """
        if not self.settings["INSTALL_JACKRABBIT"]:
            logger.info("Jackrabbit must be installed. If the following prompt is answered with N it is assumed "
                        "the jackrabbit content repository is either installed locally or remotely")
            self.settings["INSTALL_JACKRABBIT"] = confirm_yesno("Install Jackrabbit content repository", default=True)

        if self.settings["INSTALL_JACKRABBIT"] == "N":
            if not self.settings["JACKRABBIT_URL"]:
                self.settings["JACKRABBIT_URL"] = click.prompt("Please enter jackrabbit url",
                                                               default="http://jackrabbit:8080")
            if not self.settings["JACKRABBIT_USER"]:
                self.settings["JACKRABBIT_USER"] = click.prompt("Please enter jackrabbit user", default="admin")
            logger.info("Jackrabbit password if exits must be mounted at /etc/gluu/conf/jca_password inside each pod")
        else:
            if not self.settings["JACKRABBIT_STORAGE_SIZE"]:
                self.settings["JACKRABBIT_STORAGE_SIZE"] = click.prompt(
                    "Size of Jackrabbit content repository volume storage", default="4Gi")
            self.settings["JACKRABBIT_USER"] = "admin"
            self.settings["JACKRABBIT_URL"] = "http://jackrabbit:8080"

    def prompt_postgres(self):
        """Prompts for PostGres. Injected in a file postgres.yaml used with kubedb
        """
        if not self.settings["POSTGRES_NAMESPACE"]:
            self.settings["POSTGRES_NAMESPACE"] = click.prompt("Please enter a namespace for postgres",
                                                               default="postgres")

        if not self.settings["POSTGRES_REPLICAS"]:
            self.settings["POSTGRES_REPLICAS"] = click.prompt("Please enter number of replicas for postgres", default=3)

        if not self.settings["POSTGRES_URL"]:
            self.settings["POSTGRES_URL"] = click.prompt(
                "Please enter  postgres (remote or local) "
                "URL base name. If postgres is to be installed",
                default=f"postgres.{self.settings['POSTGRES_NAMESPACE']}.svc.cluster.local",
            )

    def prompt_gluu_gateway(self):
        """Prompts for Gluu Gateway
        """
        if not self.settings["INSTALL_GLUU_GATEWAY"]:
            self.settings["INSTALL_GLUU_GATEWAY"] = confirm_yesno("Install Gluu Gateway Database mode")

        if self.settings["INSTALL_GLUU_GATEWAY"] == "Y":
            self.settings["ENABLE_OXD"] = "Y"
            self.prompt_postgres()
            if not self.settings["KONG_NAMESPACE"]:
                self.settings["KONG_NAMESPACE"] = click.prompt("Please enter a namespace for Gluu Gateway",
                                                               default="gluu-gateway")

            if not self.settings["GLUU_GATEWAY_UI_NAMESPACE"]:
                self.settings["GLUU_GATEWAY_UI_NAMESPACE"] = click.prompt(
                    "Please enter a namespace for gluu gateway ui", default="gg-ui")

            if not self.settings["KONG_PG_USER"]:
                self.settings["KONG_PG_USER"] = click.prompt("Please enter a user for gluu-gateway postgres database",
                                                             default="kong")

            if not self.settings["KONG_PG_PASSWORD"]:
                self.settings["KONG_PG_PASSWORD"] = prompt_password("gluu-gateway-postgres")

            if not self.settings["GLUU_GATEWAY_UI_PG_USER"]:
                self.settings["GLUU_GATEWAY_UI_PG_USER"] = click.prompt(
                    "Please enter a user for gluu-gateway-ui postgres database", default="konga")

            if not self.settings["GLUU_GATEWAY_UI_PG_PASSWORD"]:
                self.settings["GLUU_GATEWAY_UI_PG_PASSWORD"] = prompt_password("gluu-gateway-ui-postgres")

            if not self.settings["KONG_DATABASE"]:
                self.settings["KONG_DATABASE"] = click.prompt("Please enter gluu-gateway postgres database name",
                                                              default="kong")

            if not self.settings["GLUU_GATEWAY_UI_DATABASE"]:
                self.settings["GLUU_GATEWAY_UI_DATABASE"] = click.prompt(
                    "Please enter gluu-gateway-ui postgres database name", default="konga")

    def prompt_storage(self):
        """Prompt for LDAP storage size
        """
        if self.settings["PERSISTENCE_BACKEND"] in ("hybrid", "ldap") and not self.settings["LDAP_STORAGE_SIZE"]:
            self.settings["LDAP_STORAGE_SIZE"] = click.prompt("Size of ldap volume storage", default="4Gi")
        update_settings_json_file(self.settings)

    def prompt_backup(self):
        """Prompt for LDAP and or Couchbase backup strategies
        """
        if self.settings["PERSISTENCE_BACKEND"] in ("hybrid", "couchbase"):
            if not self.settings["COUCHBASE_INCR_BACKUP_SCHEDULE"]:
                self.settings["COUCHBASE_INCR_BACKUP_SCHEDULE"] = click.prompt(
                    "Please input couchbase backup cron job schedule for incremental backups. "
                    "This will run backup job every 30 mins by default.",
                    default="*/30 * * * *",
                )

            if not self.settings["COUCHBASE_FULL_BACKUP_SCHEDULE"]:
                self.settings["COUCHBASE_FULL_BACKUP_SCHEDULE"] = click.prompt(
                    "Please input couchbase backup cron job schedule for full backups. "
                    "This will run backup job on Saturday at 2am",
                    default="0 2 * * 6",
                )

            if not self.settings["COUCHBASE_BACKUP_RETENTION_TIME"]:
                self.settings["COUCHBASE_BACKUP_RETENTION_TIME"] = click.prompt(
                    "Please enter the time period in which to retain existing backups. "
                    "Older backups outside this time frame are deleted",
                    default="168h",
                )

            if not self.settings["COUCHBASE_BACKUP_STORAGE_SIZE"]:
                self.settings["COUCHBASE_BACKUP_STORAGE_SIZE"] = click.prompt("Size of couchbase backup volume storage",
                                                                              default="20Gi")

        elif self.settings["PERSISTENCE_BACKEND"] == "ldap":
            if not self.settings["LDAP_BACKUP_SCHEDULE"]:
                self.settings["LDAP_BACKUP_SCHEDULE"] = click.prompt(
                    "Please input ldap backup cron job schedule. "
                    "This will run backup job every 30 mins by default.",
                    default="*/30 * * * *",
                )

    def prompt_replicas(self):
        """Prompt number of replicas for Gluu apps
        """
        if not self.settings["OXAUTH_REPLICAS"]:
            self.settings["OXAUTH_REPLICAS"] = click.prompt("Number of oxAuth replicas", default=1)

        if self.settings["ENABLE_FIDO2"] == "Y" and not self.settings["FIDO2_REPLICAS"]:
            self.settings["FIDO2_REPLICAS"] = click.prompt("Number of fido2 replicas", default=1)

        if self.settings["ENABLE_SCIM"] == "Y" and not self.settings["SCIM_REPLICAS"]:
            self.settings["SCIM_REPLICAS"] = click.prompt("Number of scim replicas", default=1)

        if not self.settings["OXTRUST_REPLICAS"]:
            self.settings["OXTRUST_REPLICAS"] = click.prompt("Number of oxTrust replicas", default=1)

        if self.settings["PERSISTENCE_BACKEND"] in ("hybrid", "ldap") and not self.settings["LDAP_REPLICAS"]:
            self.settings["LDAP_REPLICAS"] = click.prompt("Number of LDAP replicas", default=1)

        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y" and not self.settings["OXSHIBBOLETH_REPLICAS"]:
            self.settings["OXSHIBBOLETH_REPLICAS"] = click.prompt("Number of oxShibboleth replicas", default=1)

        if self.settings["ENABLE_OXPASSPORT"] == "Y" and not self.settings["OXPASSPORT_REPLICAS"]:
            self.settings["OXPASSPORT_REPLICAS"] = click.prompt("Number of oxPassport replicas", default=1)

        if self.settings["ENABLE_OXD"] == "Y" and not self.settings["OXD_SERVER_REPLICAS"]:
            self.settings["OXD_SERVER_REPLICAS"] = click.prompt("Number of oxd-server replicas", default=1)

        if self.settings["ENABLE_CASA"] == "Y" and not self.settings["CASA_REPLICAS"]:
            self.settings["CASA_REPLICAS"] = click.prompt("Number of Casa replicas", default=1)

        if self.settings["ENABLE_RADIUS"] == "Y" and not self.settings["RADIUS_REPLICAS"]:
            self.settings["RADIUS_REPLICAS"] = click.prompt("Number of Radius replicas", default=1)
        update_settings_json_file(self.settings)

    @property
    def prompt_couchbase(self):
        self.prompt_arch()
        self.prompt_gluu_namespace()

        if self.settings["DEPLOYMENT_ARCH"] != "microk8s" and self.settings["DEPLOYMENT_ARCH"] != "minikube":
            self.prompt_backup()

        if not self.settings["HOST_EXT_IP"]:
            ip = self.gather_ip
            self.settings["HOST_EXT_IP"] = ip

        if not self.settings["INSTALL_COUCHBASE"]:
            logger.info("For the following prompt  if placed [N] the couchbase is assumed to be"
                        " installed or remotely provisioned")
            self.settings["INSTALL_COUCHBASE"] = confirm_yesno("Install Couchbase", default=True)

        if self.settings["INSTALL_COUCHBASE"] == "N":
            if not self.settings["COUCHBASE_CRT"]:
                print("Place the Couchbase certificate authority certificate in a file called couchbase.crt at "
                      "the same location as the installation script.")
                print("This can also be found in your couchbase UI Security > Root Certificate")
                _ = input("Hit 'enter' or 'return' when ready.")
                with open(Path("./couchbase.crt")) as content_file:
                    ca_crt = content_file.read()
                    encoded_ca_crt_bytes = base64.b64encode(ca_crt.encode("utf-8"))
                    encoded_ca_crt_string = str(encoded_ca_crt_bytes, "utf-8")
                self.settings["COUCHBASE_CRT"] = encoded_ca_crt_string
        else:
            self.settings["COUCHBASE_CRT"] = ""

        self.prompt_override_couchbase_files()

        if self.settings["DEPLOYMENT_ARCH"] in ("microk8s", "minikube"):
            self.settings["COUCHBASE_USE_LOW_RESOURCES"] = "Y"

        if not self.settings["COUCHBASE_USE_LOW_RESOURCES"]:
            self.settings["COUCHBASE_USE_LOW_RESOURCES"] = confirm_yesno(
                "Setup CB nodes using low resources for demo purposes")

        if self.settings["COUCHBASE_USE_LOW_RESOURCES"] == "N" and \
                self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"] == "N" and \
                self.settings["INSTALL_COUCHBASE"] == "Y":
            self.prompt_couchbase_calculator()

        if not self.settings["COUCHBASE_NAMESPACE"]:
            self.settings["COUCHBASE_NAMESPACE"] = click.prompt("Please enter a namespace for CB objects.",
                                                                default="cbns")

        if not self.settings["COUCHBASE_CLUSTER_NAME"]:
            self.settings["COUCHBASE_CLUSTER_NAME"] = click.prompt("Please enter a cluster name.", default="cbgluu")

        if not self.settings["COUCHBASE_URL"]:
            self.settings["COUCHBASE_URL"] = click.prompt(
                "Please enter  couchbase (remote or local) URL base name",
                default=f"{self.settings['COUCHBASE_CLUSTER_NAME']}.{self.settings['COUCHBASE_NAMESPACE']}.svc.cluster.local",
            )

        if not self.settings["COUCHBASE_USER"]:
            self.settings["COUCHBASE_USER"] = click.prompt("Please enter couchbase username.", default="admin")

        if not self.settings["COUCHBASE_PASSWORD"]:
            self.settings["COUCHBASE_PASSWORD"] = prompt_password("Couchbase")

        self.find_couchbase_certs_or_set_san_cn()
        update_settings_json_file(self.settings)
        return self.settings

    def prompt_override_couchbase_files(self):
        if not self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"]:
            self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"] = confirm_yesno(
                "Override couchbase-cluster.yaml with a custom couchbase-cluster.yaml",
            )

        if self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"] == "Y":
            try:
                shutil.copy(Path("./couchbase-cluster.yaml"), Path("./couchbase/couchbase-cluster.yaml"))
                shutil.copy(Path("./couchbase-buckets.yaml"), Path("./couchbase/couchbase-buckets.yaml"))
                shutil.copy(Path("./couchbase-ephemeral-buckets.yaml"),
                            Path("./couchbase/couchbase-ephemeral-buckets.yaml"))

            except FileNotFoundError:
                logger.error("An override option has been chosen but there is a missing couchbase file that "
                             "could not be found at the current path. Please place the override files under the name"
                             " couchbase-cluster.yaml, couchbase-buckets.yaml, and couchbase-ephemeral-buckets.yaml"
                             " in the same directory pygluu-kubernetes.pyz exists ")
                raise SystemExit(1)
        update_settings_json_file(self.settings)

    def find_couchbase_certs_or_set_san_cn(self):
        """Finds couchbase certs inside couchbase_crts-keys folder and if not existent sets couchbase SAN and prompts
        for couchbase common name.
        """
        custom_cb_ca_crt = Path("./couchbase_crts_keys/ca.crt")
        custom_cb_crt = Path("./couchbase_crts_keys/chain.pem")
        custom_cb_key = Path("./couchbase_crts_keys/pkey.key")
        if not custom_cb_ca_crt.exists() or not custom_cb_crt.exists() and not custom_cb_key.exists():
            if not self.settings['COUCHBASE_SUBJECT_ALT_NAME']:
                self.settings['COUCHBASE_SUBJECT_ALT_NAME'] = [
                    "*.{}".format(self.settings["COUCHBASE_CLUSTER_NAME"]),
                    "*.{}.{}".format(self.settings["COUCHBASE_CLUSTER_NAME"], self.settings["COUCHBASE_NAMESPACE"]),
                    "*.{}.{}.svc".format(self.settings["COUCHBASE_CLUSTER_NAME"], self.settings["COUCHBASE_NAMESPACE"]),
                    "{}-srv".format(self.settings["COUCHBASE_CLUSTER_NAME"]),
                    "{}-srv.{}".format(self.settings["COUCHBASE_CLUSTER_NAME"],
                                       self.settings["COUCHBASE_NAMESPACE"]),
                    "{}-srv.{}.svc".format(self.settings["COUCHBASE_CLUSTER_NAME"],
                                           self.settings["COUCHBASE_NAMESPACE"]),
                    "localhost"
                ]
            if not self.settings["COUCHBASE_CN"]:
                self.settings["COUCHBASE_CN"] = click.prompt("Enter Couchbase certificate common name.",
                                                             default="Couchbase CA")
        update_settings_json_file(self.settings)

    def prompt_couchbase_calculator(self):
        """Attempt to Calculate resources needed
        """
        if not self.settings["NUMBER_OF_EXPECTED_USERS"]:
            self.settings["NUMBER_OF_EXPECTED_USERS"] = click.prompt("Please enter the number of expected users",
                                                                     default="1000000")

        if not self.settings["USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW"]:
            self.settings["USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW"] = confirm_yesno(
                "Will you be using the resource owner password credential grant flow", default=True,
            )

        if not self.settings["USING_CODE_FLOW"]:
            self.settings["USING_CODE_FLOW"] = confirm_yesno("Will you be using the code flow", default=True)

        if not self.settings["USING_SCIM_FLOW"]:
            self.settings["USING_SCIM_FLOW"] = confirm_yesno("Will you be using the SCIM flow", default=True)

        if not self.settings["EXPECTED_TRANSACTIONS_PER_SEC"]:
            self.settings["EXPECTED_TRANSACTIONS_PER_SEC"] = click.prompt("Expected transactions per second",
                                                                          default=2000)

        # couchbase-cluster.yaml specs
        if not self.settings["COUCHBASE_DATA_NODES"]:
            self.settings["COUCHBASE_DATA_NODES"] = click.prompt(
                "Please enter the number of data nodes. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_INDEX_NODES"]:
            self.settings["COUCHBASE_INDEX_NODES"] = click.prompt(
                "Please enter the number of index nodes. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_QUERY_NODES"]:
            self.settings["COUCHBASE_QUERY_NODES"] = click.prompt(
                "Please enter the number of query nodes. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"]:
            self.settings["COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"] = click.prompt(
                "Please enter the number of search, eventing and analytics nodes. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_GENERAL_STORAGE"]:
            self.settings["COUCHBASE_GENERAL_STORAGE"] = click.prompt(
                "Please enter the general storage size used for couchbase. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_DATA_STORAGE"]:
            self.settings["COUCHBASE_DATA_STORAGE"] = click.prompt(
                "Please enter the data node storage size used for couchbase. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_INDEX_STORAGE"]:
            self.settings["COUCHBASE_INDEX_STORAGE"] = click.prompt(
                "Please enter the index node storage size used for couchbase. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_QUERY_STORAGE"]:
            self.settings["COUCHBASE_QUERY_STORAGE"] = click.prompt(
                "Please enter the query node storage size used for couchbase. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_ANALYTICS_STORAGE"]:
            self.settings["COUCHBASE_ANALYTICS_STORAGE"] = click.prompt(
                "Please enter the analytics node storage size used for couchbase. (auto-calculated)", default="",
            )

        if not self.settings["COUCHBASE_VOLUME_TYPE"]:
            logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
            logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
            logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
            self.settings["COUCHBASE_VOLUME_TYPE"] = click.prompt("Please enter the volume type.", default="io1")
        update_settings_json_file(self.settings)

    def prompt_couchbase_multi_cluster(self):
        """Prompts for couchbase multi cluster
        """
        print("|------------------------------------------------------------------|")
        print("|         Is this a multi-cloud/region setup[N] ? [Y/N]            |")
        print("|------------------------------------------------------------------|")
        print("|                             Notes                                |")
        print("|------------------------------------------------------------------|")
        print("If you are planning for a multi-cloud/region setup and this is the first cluster answer N or"
              " leave blank. You will answer Y for the second and more cluster setup   ")
        print("|------------------------------------------------------------------|")
        self.settings["DEPLOY_MULTI_CLUSTER"] = confirm_yesno("Is this a multi-cloud/region setup")
        update_settings_json_file(self.settings)

    def prompt_arch(self):
        """Prompts for the kubernetes infrastructure used.
        """
        # TODO: This should be auto-detected
        if not self.settings["DEPLOYMENT_ARCH"]:
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
            self.settings["DEPLOYMENT_ARCH"] = arch_map.get(choice, "microk8s")
        update_settings_json_file(self.settings)

    def prompt_license(self):
        """Prompts user to accept Apache 2.0 license
        """
        if self.settings["ACCEPT_GLUU_LICENSE"] != "Y":
            with open("./LICENSE") as f:
                print(f.read())

            self.settings["ACCEPT_GLUU_LICENSE"] = confirm_yesno("Do you accept the Gluu license stated above")
            if self.settings["ACCEPT_GLUU_LICENSE"] != "Y":
                logger.info("License not accepted.")
                raise SystemExit(1)
        update_settings_json_file(self.settings)

    def prompt_gluu_namespace(self):
        """Prompt to enable optional services
        """
        if not self.settings["GLUU_NAMESPACE"]:
            self.settings["GLUU_NAMESPACE"] = click.prompt("Namespace to deploy Gluu in", default="gluu")

    def prompt_optional_services(self):
        if not self.settings["ENABLE_CACHE_REFRESH"]:
            self.settings["ENABLE_CACHE_REFRESH"] = confirm_yesno("Deploy Cr-Rotate")

        if not self.settings["ENABLE_OXAUTH_KEY_ROTATE"]:
            self.settings["ENABLE_OXAUTH_KEY_ROTATE"] = confirm_yesno("Deploy Key-Rotation")

        if self.settings["ENABLE_OXAUTH_KEY_ROTATE"] == "Y":
            if not self.settings["OXAUTH_KEYS_LIFE"]:
                self.settings["OXAUTH_KEYS_LIFE"] = click.prompt("oxAuth keys life in hours", default=48)

        if not self.settings["ENABLE_RADIUS"]:
            self.settings["ENABLE_RADIUS"] = confirm_yesno("Deploy Radius")
        if self.settings["ENABLE_RADIUS"] == "Y":
            self.settings["ENABLE_RADIUS_BOOLEAN"] = "true"

        if not self.settings["ENABLE_OXPASSPORT"]:
            self.settings["ENABLE_OXPASSPORT"] = confirm_yesno("Deploy Passport")
        if self.settings["ENABLE_OXPASSPORT"] == "Y":
            self.settings["ENABLE_OXPASSPORT_BOOLEAN"] = "true"

        if not self.settings["ENABLE_OXSHIBBOLETH"]:
            self.settings["ENABLE_OXSHIBBOLETH"] = confirm_yesno("Deploy Shibboleth SAML IDP")
        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            self.settings["ENABLE_SAML_BOOLEAN"] = "true"

        if not self.settings["ENABLE_CASA"]:
            self.settings["ENABLE_CASA"] = confirm_yesno("Deploy Casa")
        if self.settings["ENABLE_CASA"] == "Y":
            self.settings["ENABLE_CASA_BOOLEAN"] = "true"
            self.settings["ENABLE_OXD"] = "Y"

        if not self.settings["ENABLE_FIDO2"]:
            self.settings["ENABLE_FIDO2"] = confirm_yesno("Deploy fido2")

        if not self.settings["ENABLE_SCIM"]:
            self.settings["ENABLE_SCIM"] = confirm_yesno("Deploy scim")

        if not self.settings["ENABLE_OXD"]:
            self.settings["ENABLE_OXD"] = confirm_yesno("Deploy oxd server")

        if self.settings["ENABLE_OXD"] == "Y":
            if not self.settings["OXD_APPLICATION_KEYSTORE_CN"]:
                self.settings["OXD_APPLICATION_KEYSTORE_CN"] = click.prompt("oxd server application keystore name",
                                                                            default="oxd-server")
            if not self.settings["OXD_ADMIN_KEYSTORE_CN"]:
                self.settings["OXD_ADMIN_KEYSTORE_CN"] = click.prompt("oxd server admin keystore name",
                                                                      default="oxd-server")

        if not self.settings["ENABLE_OXTRUST_API"]:
            self.settings["ENABLE_OXTRUST_API"] = confirm_yesno("Enable oxTrust API")

        if self.settings["ENABLE_OXTRUST_API"]:
            self.settings["ENABLE_OXTRUST_API_BOOLEAN"] = "true"
            if not self.settings["ENABLE_OXTRUST_TEST_MODE"]:
                self.settings["ENABLE_OXTRUST_TEST_MODE"] = confirm_yesno("Enable oxTrust Test Mode")
        if self.settings["ENABLE_OXTRUST_TEST_MODE"] == "Y":
            self.settings["ENABLE_OXTRUST_TEST_MODE_BOOLEAN"] = "true"
        update_settings_json_file(self.settings)

    @property
    def gather_ip(self):
        """Attempts to detect and return ip automatically.
        Also set node names, zones, and addresses in a cloud deployment.

        :return:
        """
        logger.info("Determining OS type and attempting to gather external IP address")
        ip = ""

        # detect IP address automatically (if possible)
        try:
            node_ip_list = []
            node_zone_list = []
            node_name_list = []
            node_list = self.kubernetes.list_nodes().items

            for node in node_list:
                node_name = node.metadata.name
                node_addresses = self.kubernetes.read_node(name=node_name).status.addresses
                if self.settings["DEPLOYMENT_ARCH"] in ("microk8s", "minikube"):
                    for add in node_addresses:
                        if add.type == "InternalIP":
                            ip = add.address
                            node_ip_list.append(ip)
                else:
                    for add in node_addresses:
                        if add.type == "ExternalIP":
                            ip = add.address
                            node_ip_list.append(ip)
                    # Digital Ocean does not provide zone support yet
                    if self.settings["DEPLOYMENT_ARCH"] not in ("do", "local"):
                        node_zone = node.metadata.labels["failure-domain.beta.kubernetes.io/zone"]
                        node_zone_list.append(node_zone)
                    node_name_list.append(node_name)

            self.settings["NODES_NAMES"] = node_name_list
            self.settings["NODES_ZONES"] = node_zone_list
            self.settings["NODES_IPS"] = node_ip_list

            if self.settings["DEPLOYMENT_ARCH"] in ("eks", "gke", "do", "local", "aks"):
                #  Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
                return "22.22.22.22"

        except Exception as e:
            logger.error(e)
            # prompt for user-inputted IP address
            logger.warning("Cannot determine IP address")
            ip = click.prompt("Please input the host's external IP address")

        if click.confirm(f"Is this the correct external IP address: {ip}", default=True):
            return ip

        while True:
            ip = click.prompt("Please input the host's external IP address")
            try:
                ipaddress.ip_address(ip)
                return ip
            except ValueError as exc:
                # raised if IP is invalid
                logger.warning(f"Cannot determine IP address; reason={exc}")

    def prompt_redis(self):
        """Prompts for Redis
        """
        if not self.settings["REDIS_TYPE"]:
            logger.info("STANDALONE, CLUSTER")
            self.settings["REDIS_TYPE"] = click.prompt("Please enter redis type", default="CLUSTER")

        if not self.settings["INSTALL_REDIS"]:
            logger.info("For the following prompt if placed [N] the Redis is assumed to be"
                        " installed or remotely provisioned")
            self.settings["INSTALL_REDIS"] = confirm_yesno("Install Redis", default=True)

        if self.settings["INSTALL_REDIS"] == "Y":
            if not self.settings["REDIS_MASTER_NODES"]:
                self.settings["REDIS_MASTER_NODES"] = click.prompt("The number of master node. Minimum is 3", default=3)

            if not self.settings["REDIS_NODES_PER_MASTER"]:
                self.settings["REDIS_NODES_PER_MASTER"] = click.prompt("The number of nodes per master node", default=2)

            if not self.settings["REDIS_NAMESPACE"]:
                self.settings["REDIS_NAMESPACE"] = click.prompt("Please enter a namespace for Redis cluster",
                                                                default="gluu-redis-cluster")
        else:
            # Placing password in kubedb is currently not supported. # Todo: Remove else once supported
            if not self.settings["REDIS_PW"]:
                self.settings["REDIS_PW"] = prompt_password("Redis")

        if not self.settings["REDIS_URL"]:
            if self.settings["INSTALL_REDIS"] == "Y":
                redis_url_prompt = "redis-cluster.{}.svc.cluster.local:6379".format(
                    self.settings["REDIS_NAMESPACE"])
            else:
                logger.info(
                    "Redis URL can be : redis-cluster.gluu-redis-cluster.svc.cluster.local:6379 in a redis deployment")
                logger.info("Redis URL using AWS ElastiCach [Configuration Endpoint]: "
                            "clustercfg.testing-redis.icrbdv.euc1.cache.amazonaws.com:6379")
                logger.info("Redis URL using Google MemoryStore : <ip>:6379")
                redis_url_prompt = click.prompt(
                    "Please enter redis URL. If you are deploying redis",
                    default="redis-cluster.gluu-redis-cluster.svc.cluster.local:6379",
                )
            self.settings["REDIS_URL"] = redis_url_prompt
        update_settings_json_file(self.settings)

    def prompt_test_environment(self):
        """Prompts for test enviornment.
        """
        logger.info("A test environment means that the installer will strip all resource requirements, "
                    "and hence will use as much as needed only. The pods are subject to eviction. Please use "
                    " at least 8GB Ram , 4 CPU, and 50 GB disk.")
        self.settings["TEST_ENVIRONMENT"] = confirm_yesno("Is this a test environment.")
        update_settings_json_file(self.settings)

    def prompt_ssh_key(self):
        """Prompts for ssh key if
        """
        self.settings["NODE_SSH_KEY"] = click.prompt(
            "Please enter the ssh key path if exists to login into the nodes created. This ssh key will only"
            " be used to delete folders created on the nodes by the setup if the user uses local volumes",
            default="~/.ssh/id_rsa",
        )
        update_settings_json_file(self.settings)

    def prompt_aws(self):
        """Prompts for AWS Load balancer information
        """
        lb_map = {
            1: "clb",
            2: "nlb",
            3: "alb",
        }

        if self.settings["AWS_LB_TYPE"] not in lb_map.values():
            print("|-----------------------------------------------------------------|")
            print("|                     AWS Loadbalancer type                       |")
            print("|-----------------------------------------------------------------|")
            print("| [1] Classic Load Balancer (CLB) [default]                       |")
            print("| [2] Network Load Balancer (NLB - Alpha) -- Static IP            |")
            print("| [3] Application Load Balancer (ALB - Alpha) DEV_ONLY            |")
            print("|-----------------------------------------------------------------|")

            choice = click.prompt("Loadbalancer type", default=1)
            self.settings["AWS_LB_TYPE"] = lb_map.get(choice, "clb")
            if self.settings["AWS_LB_TYPE"] == "alb":
                logger.info("A prompt later during installation will appear to input the ALB DNS address")

        if not self.settings["USE_ARN"]:
            self.settings["USE_ARN"] = confirm_yesno(
                "Are you terminating SSL traffic at LB and using certificate from AWS")

        if not self.settings["ARN_AWS_IAM"] and self.settings["USE_ARN"] == "Y":
            # no default means it will try to prompt in loop until user inputs
            self.settings["ARN_AWS_IAM"] = click.prompt(
                "Enter aws-load-balancer-ssl-cert arn quoted ('arn:aws:acm:us-west-2:XXXXXXXX:"
                "certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX')"
            )
        update_settings_json_file(self.settings)

    def prompt_persistence_backend(self):
        """Prompts for persistence backend layer
        """
        persistence_map = {
            1: "ldap",
            2: "couchbase",
            3: "hybrid",
        }

        if self.settings["PERSISTENCE_BACKEND"] not in persistence_map.values():
            print("|------------------------------------------------------------------|")
            print("|                     Persistence layer                            |")
            print("|------------------------------------------------------------------|")
            print("| [1] WrenDS [default]                                             |")
            print("| [2] Couchbase [Testing Phase]                                    |")
            print("| [3] Hybrid(WrenDS + Couchbase)[Testing Phase]                    |")
            print("|------------------------------------------------------------------|")

            choice = click.prompt("Persistence layer", default=1)
            self.settings["PERSISTENCE_BACKEND"] = persistence_map.get(choice, "ldap")
        update_settings_json_file(self.settings)

    def prompt_hybrid_ldap_held_data(self):
        """Prompts for data held in ldap when hybrid mode is chosen in persistence
        """
        hybrid_ldap_map = {
            1: "default",
            2: "user",
            3: "site",
            4: "cache",
            5: "token",
        }

        if self.settings["HYBRID_LDAP_HELD_DATA"] not in hybrid_ldap_map.values():
            print("|------------------------------------------------------------------|")
            print("|                     Hybrid [WrendDS + Couchbase]                 |")
            print("|------------------------------------------------------------------|")
            print("| [1] Default                                                      |")
            print("| [2] User                                                         |")
            print("| [3] Site                                                         |")
            print("| [4] Cache                                                        |")
            print("| [5] Token                                                        |")
            print("|------------------------------------------------------------------|")

            choice = click.prompt("Cache layer", default=1)
            self.settings["HYBRID_LDAP_HELD_DATA"] = hybrid_ldap_map.get(choice, "default")
        update_settings_json_file(self.settings)

    def prompt_app_volume_type(self):
        """Prompts for volume type
        """
        vol_choice = 0
        if self.settings["DEPLOYMENT_ARCH"] == "eks":
            print("|------------------------------------------------------------------|")
            print("|Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)     |")
            print("|                    MultiAZ - Supported                           |")
            print("|------------------------------------------------------------------|")
            print("| [6]  volumes on host                                             |")
            print("| [7]  EBS volumes dynamically provisioned [default]               |")
            print("| [8]  EBS volumes statically provisioned                          |")
            vol_choice = click.prompt("What type of volume path", default=7)
        elif self.settings["DEPLOYMENT_ARCH"] == "gke":
            print("|------------------------------------------------------------------|")
            print("|Google Cloud Engine - Google Kubernetes Engine                    |")
            print("|------------------------------------------------------------------|")
            print("| [11]  volumes on host                                            |")
            print("| [12]  Persistent Disk  dynamically provisioned [default]         |")
            print("| [13]  Persistent Disk  statically provisioned                    |")
            vol_choice = click.prompt("What type of volume path", default=12)
        elif self.settings["DEPLOYMENT_ARCH"] == "aks":
            print("|------------------------------------------------------------------|")
            print("|Microsoft Azure                                                   |")
            print("|------------------------------------------------------------------|")
            print("| [16] volumes on host                                             |")
            print("| [17] Persistent Disk  dynamically provisioned                    |")
            print("| [18] Persistent Disk  statically provisioned                     |")
            vol_choice = click.prompt("What type of volume path", default=17)
        elif self.settings["DEPLOYMENT_ARCH"] == "do":
            print("|------------------------------------------------------------------|")
            print("|Digital Ocean                                                     |")
            print("|------------------------------------------------------------------|")
            print("| [21] volumes on host                                             |")
            print("| [22] Persistent Disk  dynamically provisioned                    |")
            print("| [23] Persistent Disk  statically provisioned                     |")
            vol_choice = click.prompt("What type of volume path", default=22)
        elif self.settings["DEPLOYMENT_ARCH"] == "local":
            print("|------------------------------------------------------------------|")
            print("|Local Deployment                                                  |")
            print("|------------------------------------------------------------------|")
            print("| [26] OpenEBS Local PV Hostpath                                   |")
            print("|------------------------------------------------------------------|")
            logger.info("OpenEBS must be installed before")
            vol_choice = click.prompt("What type of volume path", default=26)
        self.settings["APP_VOLUME_TYPE"] = vol_choice
        update_settings_json_file(self.settings)

    def prompt_volumes(self):
        """Prompts for all info needed for volume creation on cloud or onpremise
        """
        if self.settings["DEPLOYMENT_ARCH"] == "microk8s":
            self.settings["APP_VOLUME_TYPE"] = 1
        elif self.settings["DEPLOYMENT_ARCH"] == "minikube":
            self.settings["APP_VOLUME_TYPE"] = 2

        if not self.settings["APP_VOLUME_TYPE"]:
            self.prompt_app_volume_type()

        if self.settings["APP_VOLUME_TYPE"] in (8, 13):
            self.prompt_volumes_identifier()

        if self.settings["APP_VOLUME_TYPE"] == 18:
            self.prompt_disk_uris()

        if not self.settings["LDAP_JACKRABBIT_VOLUME"] and self.settings["DEPLOYMENT_ARCH"] in ("aks", "eks", "gke"):
            logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
            logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
            logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
            self.settings["LDAP_JACKRABBIT_VOLUME"] = click.prompt("Please enter the volume type.", default="io1")
        update_settings_json_file(self.settings)

    def prompt_cache_type(self):
        """Prompt cache type
        """
        gluu_cache_map = {
            1: "NATIVE_PERSISTENCE",
            2: "IN_MEMORY",
            3: "REDIS",
        }
        if self.settings["GLUU_CACHE_TYPE"] not in gluu_cache_map.values():
            print("|------------------------------------------------------------------|")
            print("|                     Cache layer                                  |")
            print("|------------------------------------------------------------------|")
            print("| [1] NATIVE_PERSISTENCE [default]                                 |")
            print("| [2] IN_MEMORY                                                    |")
            print("| [3] REDIS                                                        |")
            print("|------------------------------------------------------------------|")
            choice = click.prompt("Cache layer", default=1)
            self.settings["GLUU_CACHE_TYPE"] = gluu_cache_map.get(choice, "NATIVE_PERSISTENCE")
        if self.settings["GLUU_CACHE_TYPE"] == "REDIS":
            self.prompt_redis()
        update_settings_json_file(self.settings)

    @property
    def check_settings_and_prompt(self):
        """Main property: called to setup all prompts and returns prompts in settings file.

        :return:
        """
        self.prompt_arch()
        self.prompt_gluu_namespace()
        self.prompt_optional_services()
        self.prompt_gluu_gateway()
        self.prompt_jackrabbit()

        if not self.settings["TEST_ENVIRONMENT"] and \
                self.settings["DEPLOYMENT_ARCH"] == "microk8s" and \
                self.settings["DEPLOYMENT_ARCH"] == "minikube":
            self.prompt_test_environment()

        if self.settings["DEPLOYMENT_ARCH"] in ("eks", "gke", "do", "local", "aks"):
            if not self.settings["NODE_SSH_KEY"]:
                self.prompt_ssh_key()

        if not self.settings["HOST_EXT_IP"]:
            ip = self.gather_ip
            self.settings["HOST_EXT_IP"] = ip

            if self.settings["DEPLOYMENT_ARCH"] == "eks":
                self.prompt_aws()

        if self.settings["DEPLOYMENT_ARCH"] == "gke":
            self.prompt_gke()

        self.prompt_persistence_backend()

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid":
            self.prompt_hybrid_ldap_held_data()

        if self.settings["PERSISTENCE_BACKEND"] in ("hybrid", "ldap") or self.settings["INSTALL_JACKRABBIT"] == "Y":
            self.prompt_volumes()

        if not self.settings["DEPLOY_MULTI_CLUSTER"] and self.settings["PERSISTENCE_BACKEND"] in (
                "hybrid", "couchbase"):
            self.prompt_couchbase_multi_cluster()

        self.prompt_cache_type()
        if self.settings["PERSISTENCE_BACKEND"] in ("hybrid", "couchbase"):
            self.prompt_couchbase

        if self.settings["DEPLOYMENT_ARCH"] not in ("microk8s", "minikube"):
            self.prompt_backup()

        self.prompt_config()
        self.prompt_image_name_tag()
        self.prompt_replicas()
        self.prompt_storage()

        if self.settings["CONFIRM_PARAMS"] != "Y":
            self.confirm_params()

        update_settings_json_file(self.settings)
        return self.settings
