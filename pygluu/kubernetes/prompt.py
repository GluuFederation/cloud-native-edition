"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Prompt is used for prompting users for input used in deploying Gluu.
"""

from pathlib import Path
import ipaddress
import re
import shutil
import json
import base64
from .kubeapi import Kubernetes
from .common import update_settings_json_file, get_logger, subprocess_cmd, prompt_password

logger = get_logger("gluu-prompt        ")


class Prompt(object):
    def __init__(self):
        self.settings = self.default_settings
        self.kubernetes = Kubernetes()
        self.get_settings()
        self.config_settings = {"hostname": "", "country_code": "", "state": "", "city": "", "admin_pw": "",
                                "ldap_pw": "", "email": "", "org_name": "", "redis_pw": ""}
        self.prompt_license()
        self.prompt_version()

    @property
    def default_settings(self):
        default_settings = dict(ACCEPT_GLUU_LICENSE="",
                                GLUU_VERSION="",
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
                                GG_UI_HELM_RELEASE_NAME="",
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
                                COUCHBASE_FQDN="",
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
                                COUCHBASE_BACKUP_SCHEDULE="",
                                COUCHBASE_BACKUP_RESTORE_POINTS="",
                                LDAP_BACKUP_SCHEDULE="",
                                NUMBER_OF_EXPECTED_USERS="",
                                EXPECTED_TRANSACTIONS_PER_SEC="",
                                USING_CODE_FLOW="",
                                USING_SCIM_FLOW="",
                                USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW="",
                                DEPLOY_MULTI_CLUSTER="",
                                HYBRID_LDAP_HELD_DATA="",
                                LDAP_VOLUME="",
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
                                OXD_SERVER_PW="",
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
                                ENABLE_OXTRUST_API="",
                                ENABLE_OXTRUST_TEST_MODE="",
                                ENABLE_CACHE_REFRESH="",
                                ENABLE_OXD="",
                                ENABLE_RADIUS="",
                                ENABLE_OXPASSPORT="",
                                ENABLE_OXSHIBBOLETH="",
                                ENABLE_CASA="",
                                ENABLE_KEY_ROTATE="",
                                ENABLE_OXTRUST_API_BOOLEAN="false",
                                ENABLE_OXTRUST_TEST_MODE_BOOLEAN="false",
                                ENABLE_RADIUS_BOOLEAN="false",
                                ENABLE_OXPASSPORT_BOOLEAN="false",
                                ENABLE_CASA_BOOLEAN="false",
                                ENABLE_SAML_BOOLEAN="false",
                                EDIT_IMAGE_NAMES_TAGS="",
                                CASA_IMAGE_NAME="",
                                CASA_IMAGE_TAG="",
                                CONFIG_IMAGE_NAME="",
                                CONFIG_IMAGE_TAG="",
                                CACHE_REFRESH_ROTATE_IMAGE_NAME="",
                                CACHE_REFRESH_ROTATE_IMAGE_TAG="",
                                KEY_ROTATE_IMAGE_NAME="",
                                KEY_ROTATE_IMAGE_TAG="",
                                LDAP_IMAGE_NAME="",
                                LDAP_IMAGE_TAG="",
                                JACKRABBIT_IMAGE_NAME="",
                                JACKRABBIT_IMAGE_TAG="",
                                OXAUTH_IMAGE_NAME="",
                                OXAUTH_IMAGE_TAG="",
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
        filename = Path("./settings.json")
        try:
            with open(filename) as f:
                custom_settings = json.load(f)
            self.settings.update(custom_settings)
        except FileNotFoundError:
            pass

    @property
    def get_supported_versions(self):
        """Get Gluu versions from gluu_versions.json
        """
        filename = Path("./gluu_versions.json")
        try:
            with open(filename) as f:
                versions = json.load(f)
            logger.info("Currently supported versions are : ")
            version_number = 0
            for k, v in versions.items():
                logger.info(k)
                if "_dev" in k:
                    logger.info("DEV VERSION : {}".format(k))
                else:
                    if float(k) > version_number:
                        version_number = float(k)
            version_number = str(version_number)
            return versions, version_number
        except FileNotFoundError:
            pass

    def prompt_version(self):
        """
        Prompts for Gluu versions
        """
        versions, version_number = self.get_supported_versions
        if not self.settings["GLUU_VERSION"]:
            prompt = input("Please enter the current version of Gluu or the version to be installed [{}]"
                           .format(version_number))
            if not prompt:
                prompt = version_number
            self.settings["GLUU_VERSION"] = prompt
        image_names_and_tags = versions[self.settings["GLUU_VERSION"]]
        self.settings.update(image_names_and_tags)

    def confirm_params(self):
        """
        Formats output of settings from prompts to the user. Passwords are not displayed.
        """
        hidden_settings = ["NODES_IPS", "NODES_ZONES", "NODES_NAMES",
                           "COUCHBASE_PASSWORD", "LDAP_PW", "ADMIN_PW", "OXD_SERVER_PW", "REDIS_PW",
                           "COUCHBASE_SUBJECT_ALT_NAME", "KONG_PG_PASSWORD", "GLUU_GATEWAY_UI_PG_PASSWORD"]
        print("{:<1} {:<40} {:<10} {:<35} {:<1}".format('|', 'Setting', '|', 'Value', '|'))
        for k, v in self.settings.items():
            if k not in hidden_settings:
                print("{:<1} {:<40} {:<10} {:<35} {:<1}".format('|', k, '|', v, '|'))

        prompt = input("Please confirm the above settings [N][Y/N]:")
        if prompt == "Y" or prompt == "y":
            self.settings["CONFIRM_PARAMS"] = "Y"
        else:
            self.settings = self.default_settings
            self.check_settings_and_prompt

    @property
    def prompt_helm(self):
        """
        Prompts for helm installation and returns updated settings.
        :return:
        """
        if not self.settings["GLUU_HELM_RELEASE_NAME"]:
            prompt = input("Please enter Gluu helm name[gluu]")
            if not prompt:
                prompt = "gluu"
            self.settings["GLUU_HELM_RELEASE_NAME"] = prompt

        if not self.settings["NGINX_INGRESS_RELEASE_NAME"]:
            prompt = input("Please enter nginx-ingress helm name[ningress]")
            if not prompt:
                prompt = "ningress"
            self.settings["NGINX_INGRESS_RELEASE_NAME"] = prompt

        if not self.settings["NGINX_INGRESS_NAMESPACE"]:
            prompt = input("Please enter nginx-ingress helm namespace[ingress-nginx]")
            if not prompt:
                prompt = "ingress-nginx"
            self.settings["NGINX_INGRESS_NAMESPACE"] = prompt

        if self.settings["INSTALL_GLUU_GATEWAY"] == "Y":
            if not self.settings["KONG_HELM_RELEASE_NAME"]:
                prompt = input("Please enter Gluu Gateway helm name[gluu-gateway]")
                if not prompt:
                    prompt = "gluu-gateway"
                self.settings["KONG_HELM_RELEASE_NAME"] = prompt

            if not self.settings["GG_UI_HELM_RELEASE_NAME"]:
                prompt = input("Please enter Gluu Gateway UI helm name[gluu-gateway-ui]")
                if not prompt:
                    prompt = "gluu-gateway-ui"
                self.settings["GG_UI_HELM_RELEASE_NAME"] = prompt

        update_settings_json_file(self.settings)
        return self.settings

    @property
    def prompt_upgrade(self):
        """
        Prompts for upgrade and returns updated settings.
        :return:
        """
        versions, version_number = self.get_supported_versions
        if not self.settings["GLUU_UPGRADE_TARGET_VERSION"]:
            prompt = input("Please enter the version to upgrade Gluu to [{}]"
                           .format(version_number))
            if not prompt:
                prompt = version_number
            self.settings["GLUU_UPGRADE_TARGET_VERSION"] = prompt
        image_names_and_tags = versions[self.settings["GLUU_UPGRADE_TARGET_VERSION"]]
        self.settings.update(image_names_and_tags)
        update_settings_json_file(self.settings)
        return self.settings

    def prompt_image_name_tag(self):
        """
        Manual prompts for image names and tags if changed from default or at a different repository.
        """
        def prompt_and_set_setting(service, image_name_key, image_tag_key):
            name_prompt = input(service + " image name [{}]".format(self.settings[image_name_key]))
            tag_prompt = input(service + " image tag [{}]".format(self.settings[image_tag_key]))
            if name_prompt:
                self.settings[image_name_key] = name_prompt
            if tag_prompt:
                self.settings[image_tag_key] = tag_prompt

        if not self.settings["EDIT_IMAGE_NAMES_TAGS"]:
            prompt = input("Would you like to manually edit the image source/name and tag[N][Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["EDIT_IMAGE_NAMES_TAGS"] = prompt
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
            if self.settings["ENABLE_KEY_ROTATE"] == "Y":
                prompt_and_set_setting("Key rotate", "KEY_ROTATE_IMAGE_NAME", "KEY_ROTATE_IMAGE_TAG")
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
            self.settings["EDIT_IMAGE_NAMES_TAGS"] = "N"
        update_settings_json_file(self.settings)

    def prompt_volumes_identifier(self):
        """
        Prompts for Static volume IDs.
        """
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            if not self.settings["LDAP_STATIC_VOLUME_ID"]:
                logger.info("EBS Volume ID example: vol-049df61146c4d7901")
                logger.info("Persistent Disk Name example: "
                            "gke-demoexamplegluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd")
                prompt = input("Please enter Persistent Disk Name or EBS Volume ID for LDAP:")
                self.settings["LDAP_STATIC_VOLUME_ID"] = prompt
        update_settings_json_file(self.settings)

    def prompt_disk_uris(self):
        """
        Prompts for static volume Disk URIs (AKS)
        """
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            if not self.settings["LDAP_STATIC_DISK_URI"]:
                logger.info("DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                            "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk")
                prompt = input("Please enter the disk uri for LDAP:")
                self.settings["LDAP_STATIC_DISK_URI"] = prompt
        update_settings_json_file(self.settings)

    def prompt_gke(self):
        """
        GKE prompts
        """
        if not self.settings["GMAIL_ACCOUNT"]:
            prompt = input("Please enter valid email for Google Cloud account:")
            self.settings["GMAIL_ACCOUNT"] = prompt

        if self.settings["APP_VOLUME_TYPE"] == 11:
            for node_name in self.settings["NODES_NAMES"]:
                for zone in self.settings["NODES_ZONES"]:
                    response = subprocess_cmd("gcloud compute ssh user@{} --zone={} "
                                              "--command='echo $HOME'".format(node_name,
                                                                              zone))
                    self.settings["GOOGLE_NODE_HOME_DIR"] = str(response, "utf-8")
                    if self.settings["GOOGLE_NODE_HOME_DIR"]:
                        break
                if self.settings["GOOGLE_NODE_HOME_DIR"]:
                    break
        update_settings_json_file(self.settings)

    def prompt_config(self):
        """
        Prompts for generation of configuration layer
        """
        check_fqdn_provided = False
        while True:
            if not self.settings["GLUU_FQDN"] or check_fqdn_provided:
                prompt = input("Enter Hostname [demoexample.gluu.org]:")
                if not prompt:
                    prompt = "demoexample.gluu.org"
                self.settings["GLUU_FQDN"] = prompt
            regex_bool = re.match(
                '^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.){2,}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]){2,}$',
                self.settings["GLUU_FQDN"])
            if regex_bool:
                break
            else:
                check_fqdn_provided = True
                logger.error("Input not FQDN structred. Please enter a FQDN with the format demoexample.gluu.org")

        if not self.settings["COUNTRY_CODE"]:
            prompt = input("Enter Country Code [US]:")
            if not prompt:
                prompt = "US"
            self.settings["COUNTRY_CODE"] = prompt

        if not self.settings["STATE"]:
            prompt = input("Enter State [TX]:")
            if not prompt:
                prompt = "TX"
            self.settings["STATE"] = prompt

        if not self.settings["CITY"]:
            prompt = input("Enter City [Austin]:")
            if not prompt:
                prompt = "Austin"
            self.settings["CITY"] = prompt

        if not self.settings["EMAIL"]:
            prompt = input("Enter email [support@gluu.org]:")
            if not prompt:
                prompt = "support@gluu.org"
            self.settings["EMAIL"] = prompt

        if not self.settings["ORG_NAME"]:
            prompt = input("Enter Organization [Gluu]:")
            if not prompt:
                prompt = "Gluu"
            self.settings["ORG_NAME"] = prompt

        if not self.settings["ADMIN_PW"]:
            self.settings["ADMIN_PW"] = prompt_password("oxTrust")

        if not self.settings["LDAP_PW"]:
            if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                    self.settings["PERSISTENCE_BACKEND"] == "ldap":
                self.settings["LDAP_PW"] = prompt_password("LDAP")
            else:
                self.settings["LDAP_PW"] = self.settings["COUCHBASE_PASSWORD"]

        if self.settings["DEPLOYMENT_ARCH"] == "microk8s" or self.settings["DEPLOYMENT_ARCH"] == "minikube":
            self.settings["IS_GLUU_FQDN_REGISTERED"] = "N"
        if not self.settings["IS_GLUU_FQDN_REGISTERED"]:
            prompt = input("Are you using a globally resolvable FQDN [N] [Y/N]:")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["IS_GLUU_FQDN_REGISTERED"] = prompt

        logger.info("You can mount your FQDN certification and key by placing them inside "
                    "gluu.crt and gluu.key respectivley at the same location pygluu-kuberentest.pyz is at.")
        # Prepare generate.json and output it
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
            json.dump(self.config_settings, file)
        update_settings_json_file(self.settings)

    def prompt_jackrabbit(self):
        """
        Prompts for Jackrabbit content repository
        """
        if not self.settings["INSTALL_JACKRABBIT"]:
            logger.info("Jackrabbit must be installed. If the following prompt is answered with N it is assumed "
                        "the jackrabbit content repository is either installed locally or remotely")
            prompt = input("Install Jackrabbit content repository[Y/N]?[Y]")
            if prompt == "N" or prompt == "n":
                prompt = "N"
            else:
                prompt = "Y"
            self.settings["INSTALL_JACKRABBIT"] = prompt
        if self.settings["INSTALL_JACKRABBIT"] == "N":
            if not self.settings["JACKRABBIT_URL"]:
                prompt = input("Please enter jackrabbit url [http://jackrabbit:8080]")
                if not prompt:
                    prompt = "http://jackrabbit:8080"
                self.settings["JACKRABBIT_URL"] = prompt
            if not self.settings["JACKRABBIT_USER"]:
                prompt = input("Please enter jackrabbit user [admin]")
                if not prompt:
                    prompt = "admin"
                self.settings["JACKRABBIT_USER"] = prompt
            logger.info("Jackrabbit password if exits must be mounted at /etc/gluu/conf/jca_password inside each pod")
        else:
            if not self.settings["JACKRABBIT_STORAGE_SIZE"]:
                prompt = input("Size of Jackrabbit content repository volume storage [4Gi]:")
                if not prompt:
                    prompt = "4Gi"
                self.settings["JACKRABBIT_STORAGE_SIZE"] = prompt
            self.settings["JACKRABBIT_USER"] = "admin"
            self.settings["JACKRABBIT_URL"] = "http://jackrabbit:8080"

    def prompt_postgres(self):
        """
        Prompts for PostGres. Injected in a file postgres.yaml used with kubedb
        """
        if not self.settings["POSTGRES_NAMESPACE"]:
            prompt = input("Please enter a namespace for postgres.[postgres]")
            if not prompt:
                prompt = "postgres"
            self.settings["POSTGRES_NAMESPACE"] = prompt

        if not self.settings["POSTGRES_REPLICAS"]:
            prompt = input("Please enter number of replicas for postgres.[3]")
            if not prompt:
                prompt = 3
            prompt = int(prompt)
            self.settings["POSTGRES_REPLICAS"] = prompt

        if not self.settings["POSTGRES_URL"]:
            default_postgres_url_prompt = "postgres.{}.svc.cluster.local".format(self.settings["POSTGRES_NAMESPACE"])

            prompt = input("Please enter  postgres (remote or local) URL base name. If postgres is to be installed"
                           " automatically please press enter to accept the default correct value[{}]"
                           .format(default_postgres_url_prompt))
            if not prompt:
                prompt = default_postgres_url_prompt
            self.settings["POSTGRES_URL"] = prompt

    def prompt_gluu_gateway(self):
        """
        Prompts for Gluu Gateway
        """
        if not self.settings["INSTALL_GLUU_GATEWAY"]:
            prompt = input("Install Gluu Gateway (alpha) [Y/N]?[Y]")
            if prompt == "N" or prompt == "n":
                prompt = "N"
            else:
                prompt = "Y"
            self.settings["INSTALL_GLUU_GATEWAY"] = prompt
        if self.settings["INSTALL_GLUU_GATEWAY"] == "Y":
            self.settings["ENABLE_OXD"] = "Y"
            self.prompt_postgres()
            if not self.settings["KONG_NAMESPACE"]:
                prompt = input("Please enter a namespace for Gluu Gateway.[gluu-gateway]")
                if not prompt:
                    prompt = "gluu-gateway"
                self.settings["KONG_NAMESPACE"] = prompt

            if not self.settings["GLUU_GATEWAY_UI_NAMESPACE"]:
                prompt = input("Please enter a namespace for gluu gateway ui.[gg-ui]")
                if not prompt:
                    prompt = "gg-ui"
                self.settings["GLUU_GATEWAY_UI_NAMESPACE"] = prompt

            if not self.settings["KONG_PG_USER"]:
                prompt = input("Please enter a user for gluu-gateway postgres database.[kong]")
                if not prompt:
                    prompt = "kong"
                self.settings["KONG_PG_USER"] = prompt

            if not self.settings["KONG_PG_PASSWORD"]:
                self.settings["KONG_PG_PASSWORD"] = prompt_password("gluu-gateway-postgres")

            if not self.settings["GLUU_GATEWAY_UI_PG_USER"]:
                prompt = input("Please enter a user for gluu-gateway-ui postgres database.[konga]")
                if not prompt:
                    prompt = "konga"
                self.settings["GLUU_GATEWAY_UI_PG_USER"] = prompt

            if not self.settings["GLUU_GATEWAY_UI_PG_PASSWORD"]:
                self.settings["GLUU_GATEWAY_UI_PG_PASSWORD"] = prompt_password("gluu-gateway-ui-postgres")

            if not self.settings["KONG_DATABASE"]:
                prompt = input("Please enter  gluu-gateway postgres database name.[kong]")
                if not prompt:
                    prompt = "kong"
                self.settings["KONG_DATABASE"] = prompt

            if not self.settings["GLUU_GATEWAY_UI_DATABASE"]:
                prompt = input("Please enter  gluu-gateway-ui postgres database name.[konga]")
                if not prompt:
                    prompt = "konga"
                self.settings["GLUU_GATEWAY_UI_DATABASE"] = prompt

    def prompt_storage(self):
        """
        Prompt for LDAP storage size
        """
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            if not self.settings["LDAP_STORAGE_SIZE"]:
                prompt = input("Size of ldap volume storage [4Gi]:")
                if not prompt:
                    prompt = "4Gi"
                self.settings["LDAP_STORAGE_SIZE"] = prompt
        update_settings_json_file(self.settings)

    def prompt_backup(self):
        """
        Prompt for LDAP and or Couchbase backup strategies
        """
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "couchbase":

            if not self.settings["COUCHBASE_BACKUP_SCHEDULE"]:
                prompt = input("Please input couchbase backup cron job schedule. This will run backup job every "
                               "30 mins by default.[*/30 * * * *]: ")
                if not prompt:
                    prompt = "*/30 * * * *"
                self.settings["COUCHBASE_BACKUP_SCHEDULE"] = prompt

            if not self.settings["COUCHBASE_BACKUP_RESTORE_POINTS"]:
                prompt = input("Please input number of restore points to save in the persistent volume. "
                               "[3]: ")
                if not prompt:
                    prompt = 3
                self.settings["COUCHBASE_BACKUP_RESTORE_POINTS"] = prompt

        elif self.settings["PERSISTENCE_BACKEND"] == "ldap":

            if not self.settings["LDAP_BACKUP_SCHEDULE"]:
                prompt = input("Please input ldap backup cron job schedule. This will run backup job every "
                               "30 mins by default.[*/30 * * * *]: ")
                if not prompt:
                    prompt = "*/30 * * * *"
                self.settings["LDAP_BACKUP_SCHEDULE"] = prompt

    def prompt_replicas(self):
        """
        Prompt number of replicas for Gluu apps
        """
        if not self.settings["OXAUTH_REPLICAS"]:
            prompt = input("Number of oxAuth replicas [1]:")
            if not prompt:
                prompt = 1
            prompt = int(prompt)
            self.settings["OXAUTH_REPLICAS"] = prompt

        if not self.settings["OXTRUST_REPLICAS"]:
            prompt = input("Number of oxTrust replicas [1]:")
            if not prompt:
                prompt = 1
            prompt = int(prompt)
            self.settings["OXTRUST_REPLICAS"] = prompt

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            if not self.settings["LDAP_REPLICAS"]:
                prompt = input("Number of LDAP replicas [1]:")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                self.settings["LDAP_REPLICAS"] = prompt

        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            if not self.settings["OXSHIBBOLETH_REPLICAS"]:
                prompt = input("Number of oxShibboleth replicas [1]:")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                self.settings["OXSHIBBOLETH_REPLICAS"] = prompt

        if self.settings["ENABLE_OXPASSPORT"] == "Y":
            if not self.settings["OXPASSPORT_REPLICAS"]:
                prompt = input("Number of oxPassport replicas [1]:")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                self.settings["OXPASSPORT_REPLICAS"] = prompt

        if self.settings["ENABLE_OXD"] == "Y":
            if not self.settings["OXD_SERVER_REPLICAS"]:
                prompt = input("Number of oxd-server replicas [1]:")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                self.settings["OXD_SERVER_REPLICAS"] = prompt

        if self.settings["ENABLE_CASA"] == "Y":
            if not self.settings["CASA_REPLICAS"]:
                prompt = input("Number of Casa replicas [1]:")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                self.settings["CASA_REPLICAS"] = prompt

        if self.settings["ENABLE_RADIUS"] == "Y":
            if not self.settings["RADIUS_REPLICAS"]:
                prompt = input("Number of Radius replicas [1]:")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                self.settings["RADIUS_REPLICAS"] = prompt
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
            prompt = input("Install Couchbase[Y/N]?[Y]")
            if prompt == "N" or prompt == "n":
                prompt = "N"
            else:
                prompt = "Y"
            self.settings["INSTALL_COUCHBASE"] = prompt

        if self.settings["INSTALL_COUCHBASE"] == "N":
            if not self.settings["COUCHBASE_CRT"]:
                print("Place the Couchbase certificate authority certificate in a file called couchbase.crt at "
                      "the same location as the installation script.")
                print("This can also be found in your couchbase UI Security > Root Certificate")
                prompt = input("Hit 'enter' or 'return' when ready.")
                with open(Path("./couchbase.crt")) as content_file:
                    ca_crt = content_file.read()
                    encoded_ca_crt_bytes = base64.b64encode(ca_crt.encode("utf-8"))
                    encoded_ca_crt_string = str(encoded_ca_crt_bytes, "utf-8")
                self.settings["COUCHBASE_CRT"] = encoded_ca_crt_string
        else:
            self.settings["COUCHBASE_CRT"] = ""

        if not self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"]:
            prompt = input("Override couchbase-cluster.yaml with a custom couchbase-cluster.yaml [N][Y/N]: ")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"] = prompt
        if self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"] == "Y":
            try:
                shutil.copy(Path("./couchbase-cluster.yaml"), Path("./couchbase/couchbase-cluster.yaml"))
            except FileNotFoundError:
                logger.error("An override option has been chosen but couchbase-cluster.yaml file "
                             "could not be found at the current path. Please place the override file under the name"
                             " couchbase-cluster.yaml in the same directory pygluu-kubernetes.pyz exists ")
                raise SystemExit(1)

        if self.settings["DEPLOYMENT_ARCH"] == "microk8s" or self.settings["DEPLOYMENT_ARCH"] == "minikube":
            self.settings["COUCHBASE_USE_LOW_RESOURCES"] = "Y"
        if not self.settings["COUCHBASE_USE_LOW_RESOURCES"]:
            prompt = input("Setup CB nodes using low resources. For demo purposes[N][Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["COUCHBASE_USE_LOW_RESOURCES"] = prompt
        if self.settings["COUCHBASE_USE_LOW_RESOURCES"] == "N" and \
                self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"] == "N" and \
                self.settings["INSTALL_COUCHBASE"] == "Y":
            # Attempt to Calculate resources needed
            if not self.settings["NUMBER_OF_EXPECTED_USERS"]:
                prompt = input("Please enter the number of expected users [1000000]")
                if not prompt:
                    prompt = "1000000"
                self.settings["NUMBER_OF_EXPECTED_USERS"] = prompt

            if not self.settings["USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW"]:
                prompt = input("Will you be using the resource owner password credential grant flow?[Y][Y/N]")
                if prompt == "Y" or prompt == "y":
                    prompt = "Y"
                else:
                    prompt = "N"
                self.settings["USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW"] = prompt

            if not self.settings["USING_CODE_FLOW"]:
                prompt = input("Will you be using the code flow?[Y][Y/N]")
                if prompt == "Y" or prompt == "y":
                    prompt = "Y"
                else:
                    prompt = "N"
                self.settings["USING_CODE_FLOW"] = prompt

            if not self.settings["USING_SCIM_FLOW"]:
                prompt = input("Will you be using the SCIM flow?[Y][Y/N]")
                if prompt == "Y" or prompt == "y":
                    prompt = "Y"
                else:
                    prompt = "N"
                self.settings["USING_SCIM_FLOW"] = prompt

            if not self.settings["EXPECTED_TRANSACTIONS_PER_SEC"]:
                prompt = input("Expected transactions per second?[2000]")
                if not prompt:
                    prompt = 2000
                prompt = int(prompt)
                self.settings["EXPECTED_TRANSACTIONS_PER_SEC"] = prompt

            # couchbase-cluster.yaml specs
            if not self.settings["COUCHBASE_DATA_NODES"]:
                prompt = input("Please enter the number of data nodes.[auto-calculated]")
                self.settings["COUCHBASE_DATA_NODES"] = prompt

            if not self.settings["COUCHBASE_INDEX_NODES"]:
                prompt = input("Please enter the number of index nodes.[auto-calculated]")
                self.settings["COUCHBASE_INDEX_NODES"] = prompt

            if not self.settings["COUCHBASE_QUERY_NODES"]:
                prompt = input("Please enter the number of query nodes.[auto-calculated]")
                self.settings["COUCHBASE_QUERY_NODES"] = prompt

            if not self.settings["COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"]:
                prompt = input("Please enter the number of search, eventing and analytics nodes.[auto-calculated]")
                self.settings["COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"] = prompt

            if not self.settings["COUCHBASE_GENERAL_STORAGE"]:
                prompt = input("Please enter the general storage size used for couchbase .[auto-calculated]")
                self.settings["COUCHBASE_GENERAL_STORAGE"] = prompt

            if not self.settings["COUCHBASE_DATA_STORAGE"]:
                prompt = input("Please enter the data node storage size used for couchbase .[auto-calculated]")
                self.settings["COUCHBASE_DATA_STORAGE"] = prompt

            if not self.settings["COUCHBASE_INDEX_STORAGE"]:
                prompt = input("Please enter the index node storage size used for couchbase .[auto-calculated]")
                self.settings["COUCHBASE_INDEX_STORAGE"] = prompt

            if not self.settings["COUCHBASE_QUERY_STORAGE"]:
                prompt = input("Please enter the query node storage size used for couchbase .[auto-calculated]")
                self.settings["COUCHBASE_QUERY_STORAGE"] = prompt

            if not self.settings["COUCHBASE_ANALYTICS_STORAGE"]:
                prompt = input("Please enter the analytics node storage size used for couchbase .[auto-calculated]")
                self.settings["COUCHBASE_ANALYTICS_STORAGE"] = prompt

            if not self.settings["COUCHBASE_VOLUME_TYPE"]:
                logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
                logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
                logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
                prompt = input("Please enter the volume type.[io1]")
                if not prompt:
                    prompt = "io1"
                self.settings["COUCHBASE_VOLUME_TYPE"] = prompt

        if not self.settings["COUCHBASE_NAMESPACE"]:
            cb_cluster_namespace_prompt = input("Please enter a namespace for CB objects.[cbns]")
            if not cb_cluster_namespace_prompt:
                cb_cluster_namespace_prompt = "cbns"
            self.settings["COUCHBASE_NAMESPACE"] = cb_cluster_namespace_prompt

        if not self.settings["COUCHBASE_CLUSTER_NAME"]:
            cb_cluster_name_prompt = input("Please enter a cluster name.[cbgluu]")
            if not cb_cluster_name_prompt:
                cb_cluster_name_prompt = "cbgluu"
            self.settings["COUCHBASE_CLUSTER_NAME"] = cb_cluster_name_prompt

        if not self.settings["COUCHBASE_URL"]:
            default_cb_url_prompt = "{}.{}.svc.cluster.local".format(self.settings["COUCHBASE_CLUSTER_NAME"],
                                                                     self.settings["COUCHBASE_NAMESPACE"])

            prompt = input("Please enter  couchbase (remote or local) URL base name[{}]"
                           .format(default_cb_url_prompt))
            if not prompt:
                prompt = default_cb_url_prompt
            self.settings["COUCHBASE_URL"] = prompt

        if not self.settings["COUCHBASE_FQDN"]:
            prompt = input("Please enter a couchbase domain for SAN.[<blank>]")
            self.settings["COUCHBASE_FQDN"] = prompt

        if not self.settings["COUCHBASE_USER"]:
            prompt = input("Please enter couchbase username.[admin]")
            if not prompt:
                prompt = "admin"
            self.settings["COUCHBASE_USER"] = prompt

        if not self.settings["COUCHBASE_PASSWORD"]:
            self.settings["COUCHBASE_PASSWORD"] = prompt_password("Couchbase")

        custom_cb_ca_crt = Path("./ca.crt")
        custom_cb_crt = Path("./chain.pem")
        custom_cb_key = Path("./pkey.key")
        if not custom_cb_ca_crt.exists() or not custom_cb_crt.exists() and not custom_cb_key.exists():
            if not self.settings['COUCHBASE_SUBJECT_ALT_NAME']:
                self.settings['COUCHBASE_SUBJECT_ALT_NAME'] = ["*.{}.{}.svc".format(
                    self.settings["COUCHBASE_CLUSTER_NAME"], self.settings["COUCHBASE_NAMESPACE"]),
                    "*.{}.svc".format(self.settings["COUCHBASE_NAMESPACE"]),
                    "*.{}.{}".format(self.settings["COUCHBASE_CLUSTER_NAME"],
                                     self.settings["COUCHBASE_FQDN"])]
            if not self.settings["COUCHBASE_CN"]:
                prompt = input("Enter Couchbase certificate common name.[Couchbase CA]")
                if not prompt:
                    prompt = "Couchbase CA"
                self.settings["COUCHBASE_CN"] = prompt
        update_settings_json_file(self.settings)
        return self.settings

    def prompt_arch(self):
        """
        Prompts for the kubernetes infrastructure used.
        # TODO: This should be auto-detected
        """
        if not self.settings["DEPLOYMENT_ARCH"]:
            print("|------------------------------------------------------------------|")
            print("|                     Local Deployments                            |")
            print("|------------------------------------------------------------------|")
            print("| [1]  Microk8s [default]                                          |")
            print("| [2]  Minikube                                                    |")
            print("|------------------------------------------------------------------|")
            print("|                     Cloud Deployments                            |")
            print("|------------------------------------------------------------------|")
            print("| [3] Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)|")
            print("| [4] Google Cloud Engine - Google Kubernetes Engine (GKE)         |")
            print("| [5] Microsoft Azure (AKS)                                        |")
            print("|------------------------------------------------------------------|")
            prompt = input("Deploy on ?[1]")
            if prompt == "2":
                prompt = "minikube"
            elif prompt == "3":
                prompt = "eks"
            elif prompt == "4":
                prompt = "gke"
            elif prompt == "5":
                prompt = "aks"
            else:
                prompt = "microk8s"
            self.settings["DEPLOYMENT_ARCH"] = prompt

    def prompt_license(self):
        """
        Prompts user to accept Apache 2.0 license
        """
        if not self.settings["ACCEPT_GLUU_LICENSE"]:
            with open("./LICENSE") as f:
                print(f.read())
            prompt = input("Do you accept the Gluu license stated above[Y/N].[N]")
            if not prompt:
                prompt = "N"
            self.settings["ACCEPT_GLUU_LICENSE"] = prompt
            if self.settings["ACCEPT_GLUU_LICENSE"] != "Y":
                logger.info("License not accepted.")
                raise SystemExit(1)
        update_settings_json_file(self.settings)

    def prompt_gluu_namespace(self):
        """
        Prompt to enable optional services
        """
        if not self.settings["GLUU_NAMESPACE"]:
            prompt = input("Namespace to deploy Gluu in [gluu]:")
            if not prompt:
                prompt = "gluu"
            self.settings["GLUU_NAMESPACE"] = prompt

    def prompt_optional_services(self):
        if not self.settings["ENABLE_CACHE_REFRESH"]:
            prompt = input("Deploy Cr-Rotate[N]?[Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["ENABLE_CACHE_REFRESH"] = prompt

        if not self.settings["ENABLE_KEY_ROTATE"]:
            prompt = input("Deploy Key-Rotation[N]?[Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["ENABLE_KEY_ROTATE"] = prompt

        if not self.settings["ENABLE_RADIUS"]:
            prompt = input("Deploy Radius[N]?[Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["ENABLE_RADIUS"] = prompt
        if self.settings["ENABLE_RADIUS"] == "Y":
            self.settings["ENABLE_RADIUS_BOOLEAN"] = "true"

        if not self.settings["ENABLE_OXPASSPORT"]:
            prompt = input("Deploy Passport[N]?[Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["ENABLE_OXPASSPORT"] = prompt
        if self.settings["ENABLE_OXPASSPORT"] == "Y":
            self.settings["ENABLE_OXPASSPORT_BOOLEAN"] = "true"

        if not self.settings["ENABLE_OXSHIBBOLETH"]:
            prompt = input("Deploy Shibboleth SAML IDP[N]?[Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["ENABLE_OXSHIBBOLETH"] = prompt
        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            self.settings["ENABLE_SAML_BOOLEAN"] = "true"

        if not self.settings["ENABLE_CASA"]:
            prompt = input("[Testing Phase] Deploy Casa[N]?[Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["ENABLE_CASA"] = prompt
        if self.settings["ENABLE_CASA"] == "Y":
            self.settings["ENABLE_CASA_BOOLEAN"] = "true"
            self.settings["ENABLE_OXD"] = "Y"

        if self.settings["ENABLE_OXD"] == "Y":
            if not self.settings["OXD_APPLICATION_KEYSTORE_CN"]:
                prompt = input("oxd server application keystore name [oxd-server]?")
                if not prompt:
                    prompt = "oxd-server"
                self.settings["OXD_APPLICATION_KEYSTORE_CN"] = prompt
            if not self.settings["OXD_ADMIN_KEYSTORE_CN"]:
                prompt = input("oxd server admin keystore name [oxd-server]?")
                if not prompt:
                    prompt = "oxd-server"
                self.settings["OXD_ADMIN_KEYSTORE_CN"] = prompt
            if not self.settings["OXD_SERVER_PW"]:
                self.settings["OXD_SERVER_PW"] = prompt_password("OXD-server")

        if not self.settings["ENABLE_OXTRUST_API"]:
            prompt = input("Enable oxTrust Api [N]?[Y/N]")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
            else:
                prompt = "N"
            self.settings["ENABLE_OXTRUST_API"] = prompt

        if self.settings["ENABLE_OXTRUST_API"]:
            self.settings["ENABLE_OXTRUST_API_BOOLEAN"] = "true"
            if not self.settings["ENABLE_OXTRUST_TEST_MODE"]:
                prompt = input("Enable oxTrust Test Mode [N]?[Y/N]")
                if prompt == "Y" or prompt == "y":
                    prompt = "Y"
                else:
                    prompt = "N"
                self.settings["ENABLE_OXTRUST_TEST_MODE"] = prompt
        if self.settings["ENABLE_OXTRUST_TEST_MODE"] == "Y":
            self.settings["ENABLE_OXTRUST_TEST_MODE_BOOLEAN"] = "true"

    @property
    def gather_ip(self):
        """
        Attempts to detect and return ip automatically. Also set node names, zones, and addresses in a cloud deployment.
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
                if self.settings["DEPLOYMENT_ARCH"] == "microk8s" or self.settings["DEPLOYMENT_ARCH"] == "minikube":
                    for add in node_addresses:
                        if add.type == "InternalIP":
                            ip = add.address
                            node_ip_list.append(ip)
                else:
                    for add in node_addresses:
                        if add.type == "ExternalIP":
                            ip = add.address
                            node_ip_list.append(ip)
                    node_zone = node.metadata.labels["failure-domain.beta.kubernetes.io/zone"]
                    node_zone_list.append(node_zone)
                    node_name_list.append(node_name)
            self.settings["NODES_NAMES"] = node_name_list
            self.settings["NODES_ZONES"] = node_zone_list
            self.settings["NODES_IPS"] = node_ip_list
            if self.settings["DEPLOYMENT_ARCH"] == "eks" \
                    or self.settings["DEPLOYMENT_ARCH"] == "gke" \
                    or self.settings["DEPLOYMENT_ARCH"] == "aks":
                #  Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
                return "22.22.22.22"

        except Exception as e:
            logger.error(e)
            # prompt for user-inputted IP address
            logger.warning("Cannot determine IP address")
            ip = input("Please input the host's external IP address: ")

        opt = input("Is this the correct external IP address: {} [Y/n]? ".format(ip))
        if opt.lower() in ("y", ""):
            return ip

        while True:
            ip = input("Please input the host's external IP address: ")
            try:
                ipaddress.ip_address(ip)
                return ip
            except ValueError as exc:
                # raised if IP is invalid
                logger.warning("Cannot determine IP address {}".format(exc))

    def prompt_redis(self):
        """
        Prompts for Redis
        """
        if not self.settings["REDIS_TYPE"]:
            logger.info("STANDALONE, CLUSTER")
            redis_type_prompt = input("Please enter redis type.[CLUSTER]")
            if not redis_type_prompt:
                redis_type_prompt = "CLUSTER"
            self.settings["REDIS_TYPE"] = redis_type_prompt

        if not self.settings["INSTALL_REDIS"]:
            logger.info("For the following prompt  if placed [N] the Redis is assumed to be"
                        " installed or remotely provisioned")
            redis_install_prompt = input("Install Redis[Y/N]?[Y]")
            if redis_install_prompt == "N" or redis_install_prompt == "n":
                redis_install_prompt = "N"
            else:
                redis_install_prompt = "Y"
            self.settings["INSTALL_REDIS"] = redis_install_prompt

        if self.settings["INSTALL_REDIS"] == "Y":

            if not self.settings["REDIS_MASTER_NODES"]:
                redis_master_prompt = input("The number of  master node. Minimum is 3.[3]")
                if not redis_master_prompt:
                    redis_master_prompt = 3
                redis_master_prompt = int(redis_master_prompt)
                self.settings["REDIS_MASTER_NODES"] = redis_master_prompt

            if not self.settings["REDIS_NODES_PER_MASTER"]:
                redis_node_prompt = input("The number of nodes per master node.[2]")
                if not redis_node_prompt:
                    redis_node_prompt = 2
                redis_node_prompt = int(redis_node_prompt)
                self.settings["REDIS_NODES_PER_MASTER"] = redis_node_prompt

            if not self.settings["REDIS_NAMESPACE"]:
                redis_namespace = input("Please enter a namespace for Redis cluster.[gluu-redis-cluster]")
                if not redis_namespace:
                    redis_namespace = "gluu-redis-cluster"
                self.settings["REDIS_NAMESPACE"] = redis_namespace

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
                redis_url_prompt = input("Please enter redis URL. If you are deploying redis ."
                                         "[redis-cluster.gluu-redis-cluster.svc.cluster.local:6379]")
            self.settings["REDIS_URL"] = redis_url_prompt

    @property
    def check_settings_and_prompt(self):
        """
        Main property: called to setup all prompts and returns prompts in settings file.
        :return:
        """
        self.prompt_arch()
        self.prompt_gluu_namespace()
        self.prompt_optional_services()
        self.prompt_gluu_gateway()
        self.prompt_jackrabbit()

        if self.settings["DEPLOYMENT_ARCH"] == "eks" \
                or self.settings["DEPLOYMENT_ARCH"] == "gke" \
                or self.settings["DEPLOYMENT_ARCH"] == "aks":
            if not self.settings["NODE_SSH_KEY"]:
                self.settings["NODE_SSH_KEY"] = input(
                    "Please enter the ssh key path if exists to login into the nodes created[~/.ssh/id_rsa]:")
                if not self.settings["NODE_SSH_KEY"]:
                    self.settings["NODE_SSH_KEY"] = "~/.ssh/id_rsa"

        if self.settings["DEPLOYMENT_ARCH"] == "microk8s":
            subprocess_cmd("microk8s.enable {} {} {}".format("dns", "ingress", "storage"))

        if not self.settings["HOST_EXT_IP"]:
            ip = self.gather_ip
            self.settings["HOST_EXT_IP"] = ip
            if self.settings["DEPLOYMENT_ARCH"] == "eks":
                aws_lb_type = ["nlb", "clb", "alb"]
                if self.settings["AWS_LB_TYPE"] not in aws_lb_type:
                    print("|-----------------------------------------------------------------|")
                    print("|                     AWS Loadbalancer type                       |")
                    print("|-----------------------------------------------------------------|")
                    print("| [1] Classic Load Balancer (CLB) [default]                       |")
                    print("| [2] Network Load Balancer (NLB - Alpha) -- Static IP            |")
                    print("| [3] Application Load Balancer (ALB - Alpha) DEV_ONLY            |")
                    print("|-----------------------------------------------------------------|")
                    prompt = input("Loadbalancer type?[1]")
                    if not prompt:
                        prompt = 1
                    prompt = int(prompt)
                    if prompt == 2:
                        self.settings["AWS_LB_TYPE"] = "nlb"
                    elif prompt == 3:
                        self.settings["AWS_LB_TYPE"] = "alb"
                        logger.info("A prompt later during installation will appear to input the ALB DNS address")
                    else:
                        self.settings["AWS_LB_TYPE"] = "clb"

                if not self.settings["USE_ARN"]:
                    prompt = input("Are you terminating SSL traffic at LB and using certificate from AWS [N][Y/N]")
                    if prompt == "Y" or prompt == "y":
                        prompt = "Y"
                    else:
                        prompt = "N"
                    self.settings["USE_ARN"] = prompt

                if not self.settings["ARN_AWS_IAM"] and self.settings["USE_ARN"] == "Y":
                    prompt = ""
                    while not prompt:
                        prompt = input("Enter aws-load-balancer-ssl-cert arn quoted "
                                       "('arn:aws:acm:us-west-2:XXXXXXXX:certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX'): ")
                    self.settings["ARN_AWS_IAM"] = prompt

        if self.settings["DEPLOYMENT_ARCH"] == "gke":
            self.prompt_gke()
        persistence_backend = ["couchbase", "hybrid", "ldap"]
        if self.settings["PERSISTENCE_BACKEND"] not in persistence_backend:
            print("|------------------------------------------------------------------|")
            print("|                     Persistence layer                            |")
            print("|------------------------------------------------------------------|")
            print("| [1] WrenDS [default]                                             |")
            print("| [2] Couchbase [Testing Phase]                                    |")
            print("| [3] Hybrid(WrenDS + Couchbase)[Testing Phase]                    |")
            print("|------------------------------------------------------------------|")
            prompt = input("Persistence layer?[1]")
            if not prompt:
                prompt = 1
            prompt = int(prompt)
            if prompt == 2:
                self.settings["PERSISTENCE_BACKEND"] = "couchbase"
            elif prompt == 3:
                self.settings["PERSISTENCE_BACKEND"] = "hybrid"
            else:
                self.settings["PERSISTENCE_BACKEND"] = "ldap"

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid":
            hybrid_ldap_held_data = ["default", "user", "site", "cache", "token"]
            if self.settings["HYBRID_LDAP_HELD_DATA"] not in hybrid_ldap_held_data:
                print("|------------------------------------------------------------------|")
                print("|                     Hybrid [WrendDS + Couchbase]                 |")
                print("|------------------------------------------------------------------|")
                print("| [1] Default                                                      |")
                print("| [2] User                                                         |")
                print("| [3] Site                                                         |")
                print("| [4] Cache                                                        |")
                print("| [5] Token                                                        |")
                print("|------------------------------------------------------------------|")
                prompt = input("Cache layer?[1]")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                if prompt == 2:
                    self.settings["HYBRID_LDAP_HELD_DATA"] = "user"
                elif prompt == 3:
                    self.settings["HYBRID_LDAP_HELD_DATA"] = "site"
                elif prompt == 4:
                    self.settings["HYBRID_LDAP_HELD_DATA"] = "cache"
                elif prompt == 5:
                    self.settings["HYBRID_LDAP_HELD_DATA"] = "token"
                else:
                    self.settings["HYBRID_LDAP_HELD_DATA"] = "default"

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap" or \
                self.settings["INSTALL_JACKRABBIT"] == "Y":
            if self.settings["DEPLOYMENT_ARCH"] == "microk8s":
                self.settings["APP_VOLUME_TYPE"] = 1
            elif self.settings["DEPLOYMENT_ARCH"] == "minikube":
                self.settings["APP_VOLUME_TYPE"] = 2
            if not self.settings["APP_VOLUME_TYPE"]:
                if self.settings["DEPLOYMENT_ARCH"] == "eks":
                    print("|------------------------------------------------------------------|")
                    print("|Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)     |")
                    print("|                    MultiAZ - Supported                           |")
                    print("|------------------------------------------------------------------|")
                    print("| [6]  volumes on host                                             |")
                    print("| [7]  EBS volumes dynamically provisioned [default]               |")
                    print("| [8]  EBS volumes statically provisioned                          |")
                    prompt = input("What type of volume path [7]")
                    if not prompt:
                        prompt = 7
                elif self.settings["DEPLOYMENT_ARCH"] == "gke":
                    print("|------------------------------------------------------------------|")
                    print("|Google Cloud Engine - Google Kubernetes Engine                    |")
                    print("|------------------------------------------------------------------|")
                    print("| [11]  volumes on host                                            |")
                    print("| [12]  Persistent Disk  dynamically provisioned [default]         |")
                    print("| [13]  Persistent Disk  statically provisioned                    |")
                    prompt = input("What type of volume path [12]")
                    if not prompt:
                        prompt = 12
                elif self.settings["DEPLOYMENT_ARCH"] == "aks":
                    print("|------------------------------------------------------------------|")
                    print("|Microsoft Azure                                                   |")
                    print("|------------------------------------------------------------------|")
                    print("| [16] volumes on host                                             |")
                    print("| [17] Persistent Disk  dynamically provisioned                    |")
                    print("| [18] Persistent Disk  statically provisioned                     |")
                    prompt = input("What type of volume path [17]")
                    if not prompt:
                        prompt = 17
                prompt = int(prompt)
                self.settings["APP_VOLUME_TYPE"] = prompt

            if self.settings["APP_VOLUME_TYPE"] == 8 or self.settings["APP_VOLUME_TYPE"] == 13:
                self.prompt_volumes_identifier()

            if self.settings["APP_VOLUME_TYPE"] == 18:
                self.prompt_disk_uris()

            if self.settings["APP_VOLUME_TYPE"] > 2 and not self.settings["LDAP_VOLUME"]:
                logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
                logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
                logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
                prompt = input("Please enter the volume type.[io1]")
                if not prompt:
                    prompt = "io1"
                self.settings["LDAP_VOLUME"] = prompt

        if not self.settings["DEPLOY_MULTI_CLUSTER"]:
            if self.settings["PERSISTENCE_BACKEND"] == "hybrid" \
                    or self.settings["PERSISTENCE_BACKEND"] == "couchbase":
                print("|------------------------------------------------------------------|")
                print("|         Is this a multi-cloud/region setup[N] ? [Y/N]            |")
                print("|------------------------------------------------------------------|")
                print("|                             Notes                                |")
                print("|------------------------------------------------------------------|")
                print("If you are planning for a multi-cloud/region setup and this is the first cluster answer N or"
                      " leave blank. You will answer Y for the second and more cluster setup   ")
                print("|------------------------------------------------------------------|")
                prompt = input("Is this a multi-cloud/region setup[Y/N]?[N]")
                if prompt == "Y" or prompt == "y":
                    prompt = "Y"
                else:
                    prompt = "N"
                self.settings["DEPLOY_MULTI_CLUSTER"] = prompt

        gluu_cache_type_options = ["IN_MEMORY", "REDIS", "NATIVE_PERSISTENCE"]
        if self.settings["GLUU_CACHE_TYPE"] not in gluu_cache_type_options:
            print("|------------------------------------------------------------------|")
            print("|                     Cache layer                                  |")
            print("|------------------------------------------------------------------|")
            print("| [1] NATIVE_PERSISTENCE [default]                                 |")
            print("| [2] IN_MEMORY                                                    |")
            print("| [3] REDIS                                                        |")
            print("|------------------------------------------------------------------|")
            prompt = input("Cache layer?[1]")
            if not prompt:
                prompt = 1
            prompt = int(prompt)
            if prompt == 2:
                self.settings["GLUU_CACHE_TYPE"] = "IN_MEMORY"
            elif prompt == 3:
                self.settings["GLUU_CACHE_TYPE"] = "REDIS"
            else:
                self.settings["GLUU_CACHE_TYPE"] = "NATIVE_PERSISTENCE"

        if self.settings["GLUU_CACHE_TYPE"] == "REDIS":
            self.prompt_redis()

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "couchbase":
            self.prompt_couchbase
        if self.settings["DEPLOYMENT_ARCH"] != "microk8s" and self.settings["DEPLOYMENT_ARCH"] != "minikube":
            self.prompt_backup()
        self.prompt_config()
        self.prompt_image_name_tag()
        self.prompt_replicas()
        self.prompt_storage()
        if self.settings["CONFIRM_PARAMS"] != "Y":
            self.confirm_params()
        update_settings_json_file(self.settings)

        return self.settings
