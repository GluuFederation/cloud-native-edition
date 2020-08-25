"""
pygluu.kubernetes.prompt
~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for terminal installations.

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
from .common import get_logger, exec_cmd, prompt_password, get_supported_versions
from .settings import SettingsHandler

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
        self.settings = SettingsHandler()
        self.kubernetes = Kubernetes()
        self.config_settings = {"hostname": "", "country_code": "", "state": "", "city": "", "admin_pw": "",
                                "ldap_pw": "", "email": "", "org_name": "", "redis_pw": ""}

        # Default list of enabled services
        self.enabled_services = ["config", "oxauth", "oxtrust", "persistence", "jackrabbit"]

        self.settings.set("ENABLED_SERVICES_LIST", self.enabled_services)

        if accept_license:
            self.settings.set("ACCEPT_GLUU_LICENSE", "Y")
        self.prompt_license()

        if not self.settings.get("GLUU_VERSION"):
            self.settings.set("GLUU_VERSION", version)
        self.prompt_version()

    def prompt_version(self):
        """Prompts for Gluu versions
        """
        versions, version_number = get_supported_versions()

        if not self.settings.get("GLUU_VERSION"):
            self.settings.set("GLUU_VERSION", click.prompt(
                "Please enter the current version of Gluu or the version to be installed",
                default=version_number,
            ))

        image_names_and_tags = versions.get(self.settings.get("GLUU_VERSION"), {})
        # override non-empty image name and tag
        self.settings.update({
            k: v for k, v in image_names_and_tags.items()
            if not self.settings.get(k)
        })

    def confirm_params(self):
        """Formats output of settings from prompts to the user. Passwords are not displayed.
        """
        hidden_settings = ["NODES_IPS", "NODES_ZONES", "NODES_NAMES",
                           "COUCHBASE_PASSWORD", "LDAP_PW", "ADMIN_PW", "REDIS_PW",
                           "COUCHBASE_SUBJECT_ALT_NAME", "KONG_PG_PASSWORD", "GLUU_GATEWAY_UI_PG_PASSWORD"]
        print("{:<1} {:<40} {:<10} {:<35} {:<1}".format('|', 'Setting', '|', 'Value', '|'))
        for k, v in self.settings.db.items():
            if k not in hidden_settings:
                if k == "ENABLED_SERVICES_LIST":
                    v = ", ".join(self.settings.get("ENABLED_SERVICES_LIST"))
                print("{:<1} {:<40} {:<10} {:<35} {:<1}".format('|', k, '|', v, '|'))

        if click.confirm("Please confirm the above settings"):
            self.settings.set("CONFIRM_PARAMS", "Y")
        else:
            self.settings.reset_data()
            self.check_settings_and_prompt()

    def prompt_helm(self):
        """Prompts for helm installation and returns updated settings.

        :return:
        """
        if not self.settings.get("GLUU_HELM_RELEASE_NAME"):
            self.settings.set("GLUU_HELM_RELEASE_NAME", click.prompt("Please enter Gluu helm name", default="gluu"))

        if not self.settings.get("NGINX_INGRESS_RELEASE_NAME"):
            self.settings.set("NGINX_INGRESS_RELEASE_NAME", click.prompt("Please enter nginx-ingress helm name",
                                                                         default="ningress"))

        if not self.settings.get("NGINX_INGRESS_NAMESPACE"):
            self.settings.set("NGINX_INGRESS_NAMESPACE", click.prompt("Please enter nginx-ingress helm namespace",
                                                                      default="ingress-nginx"))

        if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            if not self.settings.get("KONG_HELM_RELEASE_NAME"):
                self.settings.set("KONG_HELM_RELEASE_NAME", click.prompt("Please enter Gluu Gateway helm name",
                                                                         default="gluu-gateway"))

            if not self.settings.get("GLUU_GATEWAY_UI_HELM_RELEASE_NAME"):
                self.settings.set("GLUU_GATEWAY_UI_HELM_RELEASE_NAME", click.prompt(
                    "Please enter Gluu Gateway UI helm name", default="gluu-gateway-ui"))

    def prompt_upgrade(self):
        """Prompts for upgrade and returns updated settings.

        :return:
        """
        versions, version_number = get_supported_versions()
        self.enabled_services.append("upgrade")
        if not self.settings.get("GLUU_UPGRADE_TARGET_VERSION"):
            self.settings.set("GLUU_UPGRADE_TARGET_VERSION", click.prompt(
                "Please enter the version to upgrade Gluu to", default=version_number,
            ))

        image_names_and_tags = versions.get(self.settings.get("GLUU_UPGRADE_TARGET_VERSION"), {})
        self.settings.update(image_names_and_tags)
        self.settings.store_data()

    def prompt_image_name_tag(self):
        """Manual prompts for image names and tags if changed from default or at a different repository.
        """

        def prompt_and_set_setting(service, image_name_key, image_tag_key):
            self.settings.set(image_name_key,
                              click.prompt(f"{service} image name", default=self.settings.get(image_name_key)))
            self.settings.set(image_tag_key,
                              click.prompt(f"{service} image tag", default=self.settings.get(image_tag_key)))

        if not self.settings.get("EDIT_IMAGE_NAMES_TAGS"):
            self.settings.set("EDIT_IMAGE_NAMES_TAGS", confirm_yesno(
                "Would you like to manually edit the image source/name and tag"))

        if self.settings.get("EDIT_IMAGE_NAMES_TAGS") == "Y":
            # CASA
            if self.settings.get("ENABLE_CASA") == "Y":
                prompt_and_set_setting("Casa", "CASA_IMAGE_NAME", "CASA_IMAGE_TAG")
            # CONFIG
            prompt_and_set_setting("Config", "CONFIG_IMAGE_NAME", "CONFIG_IMAGE_TAG")
            # CACHE_REFRESH_ROTATE
            if self.settings.get("ENABLE_CACHE_REFRESH") == "Y":
                prompt_and_set_setting("CR-rotate", "CACHE_REFRESH_ROTATE_IMAGE_NAME", "CACHE_REFRESH_ROTATE_IMAGE_TAG")
            # KEY_ROTATE
            if self.settings.get("ENABLE_OXAUTH_KEY_ROTATE") == "Y":
                prompt_and_set_setting("Key rotate", "CERT_MANAGER_IMAGE_NAME", "CERT_MANAGER_IMAGE_TAG")
            # LDAP
            if self.settings.get("PERSISTENCE_BACKEND") == "hybrid" or \
                    self.settings.get("PERSISTENCE_BACKEND") == "ldap":
                prompt_and_set_setting("WrenDS", "LDAP_IMAGE_NAME", "LDAP_IMAGE_TAG")
            # Jackrabbit
            prompt_and_set_setting("jackrabbit", "JACKRABBIT_IMAGE_NAME", "JACKRABBIT_IMAGE_TAG")
            # OXAUTH
            prompt_and_set_setting("oxAuth", "OXAUTH_IMAGE_NAME", "OXAUTH_IMAGE_TAG")
            # OXD
            if self.settings.get("ENABLE_OXD") == "Y":
                prompt_and_set_setting("OXD server", "OXD_IMAGE_NAME", "OXD_IMAGE_TAG")
            # OXPASSPORT
            if self.settings.get("ENABLE_OXPASSPORT") == "Y":
                prompt_and_set_setting("oxPassport", "OXPASSPORT_IMAGE_NAME", "OXPASSPORT_IMAGE_TAG")
            # OXSHIBBBOLETH
            if self.settings.get("ENABLE_OXSHIBBOLETH") == "Y":
                prompt_and_set_setting("oxShibboleth", "OXSHIBBOLETH_IMAGE_NAME", "OXSHIBBOLETH_IMAGE_TAG")
            # OXTRUST
            prompt_and_set_setting("oxTrust", "OXTRUST_IMAGE_NAME", "OXTRUST_IMAGE_TAG")
            # PERSISTENCE
            prompt_and_set_setting("Persistence", "PERSISTENCE_IMAGE_NAME", "PERSISTENCE_IMAGE_TAG")
            # RADIUS
            if self.settings.get("ENABLE_RADIUS") == "Y":
                prompt_and_set_setting("Radius", "RADIUS_IMAGE_NAME", "RADIUS_IMAGE_TAG")
            # Gluu-Gateway
            if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
                prompt_and_set_setting("Gluu-Gateway", "GLUU_GATEWAY_IMAGE_NAME", "GLUU_GATEWAY_IMAGE_TAG")
                # Gluu-Gateway-UI
                prompt_and_set_setting("Gluu-Gateway-UI", "GLUU_GATEWAY_UI_IMAGE_NAME", "GLUU_GATEWAY_UI_IMAGE_TAG")
            self.settings.set("EDIT_IMAGE_NAMES_TAGS", "N")

    def prompt_volumes_identifier(self):
        """Prompts for Static volume IDs.
        """
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and \
                not self.settings.get("LDAP_STATIC_VOLUME_ID"):
            logger.info("EBS Volume ID example: vol-049df61146c4d7901")
            logger.info("Persistent Disk Name example: "
                        "gke-demoexamplegluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd")
            self.settings.set("LDAP_STATIC_VOLUME_ID", click.prompt(
                "Please enter Persistent Disk Name or EBS Volume ID for LDAP"))

    def prompt_disk_uris(self):
        """Prompts for static volume Disk URIs (AKS)
        """
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and not self.settings.get(
                "LDAP_STATIC_DISK_URI"):
            logger.info("DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                        "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk")
            self.settings.set("LDAP_STATIC_DISK_URI", click.prompt("Please enter the disk uri for LDAP"))

    def prompt_gke(self):
        """GKE prompts
        """
        if not self.settings.get("GMAIL_ACCOUNT"):
            self.settings.set("GMAIL_ACCOUNT", click.prompt("Please enter valid email for Google Cloud account"))

        if self.settings.get("APP_VOLUME_TYPE") == 11:
            for node_name in self.settings.get("NODES_NAMES"):
                for zone in self.settings.get("NODES_ZONES"):
                    response, error, retcode = exec_cmd("gcloud compute ssh user@{} --zone={} "
                                                        "--command='echo $HOME'".format(node_name, zone))
                    self.settings.set("GOOGLE_NODE_HOME_DIR", str(response, "utf-8"))
                    if self.settings.get("GOOGLE_NODE_HOME_DIR"):
                        break
                if self.settings.get("GOOGLE_NODE_HOME_DIR"):
                    break

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

            if self.settings.get("IS_GLUU_FQDN_REGISTERED") == "Y":
                self.enabled_services.append("update-lb-ip")

        logger.info("You can mount your FQDN certification and key by placing them inside "
                    "gluu.crt and gluu.key respectivley at the same location pygluu-kuberentest.pyz is at.")
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

    def prompt_jackrabbit(self):
        """Prompts for Jackrabbit content repository
        """
        if not self.settings.get("INSTALL_JACKRABBIT"):
            logger.info("Jackrabbit must be installed. If the following prompt is answered with N it is assumed "
                        "the jackrabbit content repository is either installed locally or remotely")
            self.settings.set("INSTALL_JACKRABBIT",
                              confirm_yesno("Install Jackrabbit content repository", default=True))

        jackrabbit_cluster_prompt = "Is"
        if self.settings.get("INSTALL_JACKRABBIT") == "Y":
            if not self.settings.get("JACKRABBIT_STORAGE_SIZE"):
                self.settings.set("JACKRABBIT_STORAGE_SIZE", click.prompt(
                    "Size of Jackrabbit content repository volume storage", default="4Gi"))
            self.settings.set("JACKRABBIT_URL", "http://jackrabbit:8080")
            jackrabbit_cluster_prompt = "Enable"

        if not self.settings.get("JACKRABBIT_URL"):
            self.settings.set("JACKRABBIT_URL", click.prompt("Please enter jackrabbit url.",
                                                             default="http://jackrabbit:8080"))
        if not self.settings.get("JACKRABBIT_ADMIN_ID"):
            self.settings.set("JACKRABBIT_ADMIN_ID",
                              click.prompt("Please enter Jackrabit admin user", default="admin"))

        if not self.settings.get("JACKRABBIT_ADMIN_PASSWORD"):
            self.settings.set("JACKRABBIT_ADMIN_PASSWORD", prompt_password("jackrabbit-admin", 24))

        if not self.settings.get("JACKRABBIT_CLUSTER"):
            self.settings.set("JACKRABBIT_CLUSTER", confirm_yesno("{} Jackrabbit in cluster mode[beta] "
                                                                  "Recommended in production"
                                                                  .format(jackrabbit_cluster_prompt), default=True))
        if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
            self.prompt_postgres()
            if not self.settings.get("JACKRABBIT_PG_USER"):
                self.settings.set("JACKRABBIT_PG_USER", click.prompt("Please enter a user for jackrabbit postgres "
                                                                     "database",
                                                                     default="jackrabbit"))

            if not self.settings.get("JACKRABBIT_PG_PASSWORD"):
                self.settings.set("JACKRABBIT_PG_PASSWORD", prompt_password("jackrabbit-postgres"))

            if not self.settings.get("JACKRABBIT_DATABASE"):
                self.settings.set("JACKRABBIT_DATABASE", click.prompt("Please enter jackrabbit postgres database name",
                                                                      default="jackrabbit"))

    def prompt_postgres(self):
        """Prompts for PostGres. Injected in a file postgres.yaml used with kubedb
        """
        if not self.settings.get("POSTGRES_NAMESPACE"):
            self.settings.set("POSTGRES_NAMESPACE", click.prompt("Please enter a namespace for postgres",
                                                                 default="postgres"))

        if not self.settings.get("POSTGRES_REPLICAS"):
            self.settings.set("POSTGRES_REPLICAS",
                              click.prompt("Please enter number of replicas for postgres", default=3))

        if not self.settings.get("POSTGRES_URL"):
            self.settings.set("POSTGRES_URL", click.prompt(
                "Please enter  postgres (remote or local) "
                "URL base name. If postgres is to be installed",
                default=f"postgres.{self.settings.get('POSTGRES_NAMESPACE')}.svc.cluster.local",
            ))

    def prompt_gluu_gateway(self):
        """Prompts for Gluu Gateway
        """
        if not self.settings.get("INSTALL_GLUU_GATEWAY"):
            self.settings.set("INSTALL_GLUU_GATEWAY", confirm_yesno("Install Gluu Gateway Database mode"))

        if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            self.enabled_services.append("gluu-gateway-ui")
            self.settings.set("ENABLE_OXD", "Y")
            self.prompt_postgres()
            if not self.settings.get("KONG_NAMESPACE"):
                self.settings.set("KONG_NAMESPACE", click.prompt("Please enter a namespace for Gluu Gateway",
                                                                 default="gluu-gateway"))

            if not self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"):
                self.settings.set("GLUU_GATEWAY_UI_NAMESPACE", click.prompt(
                    "Please enter a namespace for gluu gateway ui", default="gg-ui"))

            if not self.settings.get("KONG_PG_USER"):
                self.settings.set("KONG_PG_USER", click.prompt("Please enter a user for gluu-gateway postgres database",
                                                               default="kong"))

            if not self.settings.get("KONG_PG_PASSWORD"):
                self.settings.set("KONG_PG_PASSWORD", prompt_password("gluu-gateway-postgres"))

            if not self.settings.get("GLUU_GATEWAY_UI_PG_USER"):
                self.settings.set("GLUU_GATEWAY_UI_PG_USER", click.prompt(
                    "Please enter a user for gluu-gateway-ui postgres database", default="konga"))

            if not self.settings.get("GLUU_GATEWAY_UI_PG_PASSWORD"):
                self.settings.set("GLUU_GATEWAY_UI_PG_PASSWORD", prompt_password("gluu-gateway-ui-postgres"))

            if not self.settings.get("KONG_DATABASE"):
                self.settings.set("KONG_DATABASE", click.prompt("Please enter gluu-gateway postgres database name",
                                                                default="kong"))

            if not self.settings.get("GLUU_GATEWAY_UI_DATABASE"):
                self.settings.set("GLUU_GATEWAY_UI_DATABASE", click.prompt(
                    "Please enter gluu-gateway-ui postgres database name", default="konga"))

    def prompt_storage(self):
        """Prompt for LDAP storage size
        """
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and not self.settings.get(
                "LDAP_STORAGE_SIZE"):
            self.settings.set("LDAP_STORAGE_SIZE", click.prompt("Size of ldap volume storage", default="4Gi"))

    def prompt_istio(self):
        """Prompt for Istio
        """
        if not self.settings.get("USE_ISTIO_INGRESS") and self.settings.get("DEPLOYMENT_ARCH") not in (
                "microk8s", "minikube"):
            self.settings.set("USE_ISTIO_INGRESS", confirm_yesno("[Alpha] Would you like to use "
                                                                 "Istio Ingress with Gluu ?"))
        if self.settings.get("USE_ISTIO_INGRESS") == "Y":
            self.settings.set("USE_ISTIO", "Y")

        if not self.settings.get("USE_ISTIO"):
            logger.info("Please follow https://istio.io/latest/docs/ to learn more.")
            logger.info("Istio will auto inject side cars into all pods in Gluus namespace chosen. "
                        "The label istio-injection=enabled will be added to the namespace Gluu will be installed in "
                        "if the namespace does not exist. If it does please run "
                        "kubectl label namespace <namespace> istio-injection=enabled")
            self.settings.set("USE_ISTIO", confirm_yesno("[Alpha] Would you like to use Istio with Gluu ?"))

        if not self.settings.get("ISTIO_SYSTEM_NAMESPACE") and self.settings.get("USE_ISTIO") == "Y":
            self.settings.set("ISTIO_SYSTEM_NAMESPACE", click.prompt("Istio namespace",
                                                                     default="istio-system"))
        if self.settings.get("USE_ISTIO_INGRESS") == "Y":
            self.enabled_services.append("gluu-istio-ingress")

            if not self.settings.get("LB_ADD"):
                self.settings.set("LB_ADD", click.prompt("Istio loadbalancer adderss(eks) or "
                                                         "ip (gke, aks, digital ocean, local)", default=""))

    def prompt_backup(self):
        """Prompt for LDAP and or Couchbase backup strategies
        """
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            if not self.settings.get("COUCHBASE_INCR_BACKUP_SCHEDULE"):
                self.settings.set("COUCHBASE_INCR_BACKUP_SCHEDULE", click.prompt(
                    "Please input couchbase backup cron job schedule for incremental backups. "
                    "This will run backup job every 30 mins by default.",
                    default="*/30 * * * *",
                ))

            if not self.settings.get("COUCHBASE_FULL_BACKUP_SCHEDULE"):
                self.settings.set("COUCHBASE_FULL_BACKUP_SCHEDULE", click.prompt(
                    "Please input couchbase backup cron job schedule for full backups. "
                    "This will run backup job on Saturday at 2am",
                    default="0 2 * * 6",
                ))

            if not self.settings.get("COUCHBASE_BACKUP_RETENTION_TIME"):
                self.settings.set("COUCHBASE_BACKUP_RETENTION_TIME", click.prompt(
                    "Please enter the time period in which to retain existing backups. "
                    "Older backups outside this time frame are deleted",
                    default="168h",
                ))

            if not self.settings.get("COUCHBASE_BACKUP_STORAGE_SIZE"):
                self.settings.set("COUCHBASE_BACKUP_STORAGE_SIZE",
                                  click.prompt("Size of couchbase backup volume storage",
                                               default="20Gi"))

        elif self.settings.get("PERSISTENCE_BACKEND") == "ldap":
            if not self.settings.get("LDAP_BACKUP_SCHEDULE"):
                self.settings.set("LDAP_BACKUP_SCHEDULE", click.prompt(
                    "Please input ldap backup cron job schedule. "
                    "This will run backup job every 30 mins by default.",
                    default="*/30 * * * *",
                ))

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

        if self.settings.get("ENABLE_RADIUS") == "Y" and not self.settings.get("RADIUS_REPLICAS"):
            self.settings.set("RADIUS_REPLICAS", click.prompt("Number of Radius replicas", default=1))

    def prompt_couchbase(self):
        self.prompt_arch()
        self.prompt_gluu_namespace()

        if self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            self.prompt_backup()

        if not self.settings.get("HOST_EXT_IP"):
            ip = self.gather_ip
            self.settings.set("HOST_EXT_IP", ip)

        if not self.settings.get("INSTALL_COUCHBASE"):
            logger.info("For the following prompt  if placed [N] the couchbase is assumed to be"
                        " installed or remotely provisioned")
            self.settings.set("INSTALL_COUCHBASE", confirm_yesno("Install Couchbase", default=True))

        if self.settings.get("INSTALL_COUCHBASE") == "N":
            if not self.settings.get("COUCHBASE_CRT"):
                print("Place the Couchbase certificate authority certificate in a file called couchbase.crt at "
                      "the same location as the installation script.")
                print("This can also be found in your couchbase UI Security > Root Certificate")
                _ = input("Hit 'enter' or 'return' when ready.")
                with open(Path("./couchbase.crt")) as content_file:
                    ca_crt = content_file.read()
                    encoded_ca_crt_bytes = base64.b64encode(ca_crt.encode("utf-8"))
                    encoded_ca_crt_string = str(encoded_ca_crt_bytes, "utf-8")
                self.settings.set("COUCHBASE_CRT", encoded_ca_crt_string)
        else:
            self.settings.set("COUCHBASE_CRT", "")

        self.prompt_override_couchbase_files()

        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube"):
            self.settings.set("COUCHBASE_USE_LOW_RESOURCES", "Y")

        if not self.settings.get("COUCHBASE_USE_LOW_RESOURCES"):
            self.settings.set("COUCHBASE_USE_LOW_RESOURCES", confirm_yesno(
                "Setup CB nodes using low resources for demo purposes"))

        if self.settings.get("COUCHBASE_USE_LOW_RESOURCES") == "N" and \
                self.settings.get("COUCHBASE_CLUSTER_FILE_OVERRIDE") == "N" and \
                self.settings.get("INSTALL_COUCHBASE") == "Y":
            self.prompt_couchbase_calculator()

        if not self.settings.get("COUCHBASE_NAMESPACE"):
            self.settings.set("COUCHBASE_NAMESPACE", click.prompt("Please enter a namespace for CB objects.",
                                                                  default="cbns"))

        if not self.settings.get("COUCHBASE_CLUSTER_NAME"):
            self.settings.set("COUCHBASE_CLUSTER_NAME", click.prompt("Please enter a cluster name.", default="cbgluu"))

        if not self.settings.get("COUCHBASE_URL"):
            self.settings.set("COUCHBASE_URL", click.prompt(
                "Please enter  couchbase (remote or local) URL base name",
                default=f"{self.settings.get('COUCHBASE_CLUSTER_NAME')}.{self.settings.get('COUCHBASE_NAMESPACE')}.svc"
                        f".cluster.local",
            ))

        if not self.settings.get("COUCHBASE_USER"):
            self.settings.set("COUCHBASE_USER", click.prompt("Please enter couchbase username.", default="admin"))

        if not self.settings.get("COUCHBASE_PASSWORD"):
            self.settings.set("COUCHBASE_PASSWORD", prompt_password("Couchbase"))

        self.find_couchbase_certs_or_set_san_cn()

    def prompt_override_couchbase_files(self):
        if not self.settings.get("COUCHBASE_CLUSTER_FILE_OVERRIDE"):
            self.settings.set("COUCHBASE_CLUSTER_FILE_OVERRIDE", confirm_yesno(
                "Override couchbase-cluster.yaml with a custom couchbase-cluster.yaml",
            ))

        if self.settings.get("COUCHBASE_CLUSTER_FILE_OVERRIDE") == "Y":
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

    def find_couchbase_certs_or_set_san_cn(self):
        """Finds couchbase certs inside couchbase_crts-keys folder and if not existent sets couchbase SAN and prompts
        for couchbase common name.
        """
        custom_cb_ca_crt = Path("./couchbase_crts_keys/ca.crt")
        custom_cb_crt = Path("./couchbase_crts_keys/chain.pem")
        custom_cb_key = Path("./couchbase_crts_keys/pkey.key")
        if not custom_cb_ca_crt.exists() or not custom_cb_crt.exists() and not custom_cb_key.exists():
            if not self.settings.get('COUCHBASE_SUBJECT_ALT_NAME'):
                self.settings.set('COUCHBASE_SUBJECT_ALT_NAME', [
                    "*.{}".format(self.settings.get("COUCHBASE_CLUSTER_NAME")),
                    "*.{}.{}".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                     self.settings.get("COUCHBASE_NAMESPACE")),
                    "*.{}.{}.svc".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                         self.settings.get("COUCHBASE_NAMESPACE")),
                    "{}-srv".format(self.settings.get("COUCHBASE_CLUSTER_NAME")),
                    "{}-srv.{}".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                       self.settings.get("COUCHBASE_NAMESPACE")),
                    "{}-srv.{}.svc".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                           self.settings.get("COUCHBASE_NAMESPACE")),
                    "localhost"
                ])
            if not self.settings.get("COUCHBASE_CN"):
                self.settings.set("COUCHBASE_CN", click.prompt("Enter Couchbase certificate common name.",
                                                               default="Couchbase CA"))

    def prompt_couchbase_calculator(self):
        """Attempt to Calculate resources needed
        """
        if not self.settings.get("NUMBER_OF_EXPECTED_USERS"):
            self.settings.set("NUMBER_OF_EXPECTED_USERS", click.prompt("Please enter the number of expected users "
                                                                       "[alpha]", default="1000000"))

        if not self.settings.get("USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW"):
            self.settings.set("USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW", confirm_yesno(
                "Will you be using the resource owner password credential grant flow [alpha]", default=True,
            ))

        if not self.settings.get("USING_CODE_FLOW"):
            self.settings.set("USING_CODE_FLOW", confirm_yesno("Will you be using the code flow [alpha]", default=True))

        if not self.settings.get("USING_SCIM_FLOW"):
            self.settings.set("USING_SCIM_FLOW", confirm_yesno("Will you be using the SCIM flow [alpha]", default=True))

        if not self.settings.get("EXPECTED_TRANSACTIONS_PER_SEC"):
            self.settings.set("EXPECTED_TRANSACTIONS_PER_SEC", click.prompt("Expected transactions per second [alpha]",
                                                                            default=2000))

        # couchbase-cluster.yaml specs
        if not self.settings.get("COUCHBASE_DATA_NODES"):
            self.settings.set("COUCHBASE_DATA_NODES", click.prompt(
                "Please enter the number of data nodes. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_INDEX_NODES"):
            self.settings.set("COUCHBASE_INDEX_NODES", click.prompt(
                "Please enter the number of index nodes. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_QUERY_NODES"):
            self.settings.set("COUCHBASE_QUERY_NODES", click.prompt(
                "Please enter the number of query nodes. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"):
            self.settings.set("COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES", click.prompt(
                "Please enter the number of search, eventing and analytics nodes. [alpha] (auto-calculated)",
                default="",
            ))

        if not self.settings.get("COUCHBASE_GENERAL_STORAGE"):
            self.settings.set("COUCHBASE_GENERAL_STORAGE", click.prompt(
                "Please enter the general storage size used for couchbase. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_DATA_STORAGE"):
            self.settings.set("COUCHBASE_DATA_STORAGE", click.prompt(
                "Please enter the data node storage size used for couchbase. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_INDEX_STORAGE"):
            self.settings.set("COUCHBASE_INDEX_STORAGE", click.prompt(
                "Please enter the index node storage size used for couchbase. (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_QUERY_STORAGE"):
            self.settings.set("COUCHBASE_QUERY_STORAGE", click.prompt(
                "Please enter the query node storage size used for couchbase. (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_ANALYTICS_STORAGE"):
            self.settings.set("COUCHBASE_ANALYTICS_STORAGE", click.prompt(
                "Please enter the analytics node storage size used for couchbase. (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_VOLUME_TYPE"):
            logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
            logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
            logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
            self.settings.set("COUCHBASE_VOLUME_TYPE", click.prompt("Please enter the volume type.", default="io1"))

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
        self.settings.set("DEPLOY_MULTI_CLUSTER", confirm_yesno("Is this a multi-cloud/region setup"))

    def prompt_arch(self):
        """Prompts for the kubernetes infrastructure used.
        """
        # TODO: This should be auto-detected
        if not self.settings.get("DEPLOYMENT_ARCH"):
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
            self.settings.set("DEPLOYMENT_ARCH", arch_map.get(choice, "microk8s"))

    def prompt_license(self):
        """Prompts user to accept Apache 2.0 license
        """
        if self.settings.get("ACCEPT_GLUU_LICENSE") != "Y":
            with open("./LICENSE") as f:
                print(f.read())

            self.settings.set("ACCEPT_GLUU_LICENSE", confirm_yesno("Do you accept the Gluu license stated above"))
            if self.settings.get("ACCEPT_GLUU_LICENSE") != "Y":
                logger.info("License not accepted.")
                raise SystemExit(1)

    def prompt_gluu_namespace(self):
        """Prompt to enable optional services
        """
        if not self.settings.get("GLUU_NAMESPACE"):
            self.settings.set("GLUU_NAMESPACE", click.prompt("Namespace to deploy Gluu in", default="gluu"))

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

        if not self.settings.get("ENABLE_RADIUS"):
            self.settings.set("ENABLE_RADIUS", confirm_yesno("Deploy Radius"))
        if self.settings.get("ENABLE_RADIUS") == "Y":
            self.enabled_services.append("radius")
            self.settings.set("ENABLE_RADIUS_BOOLEAN", "true")

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
                if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube"):
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
                    if self.settings.get("DEPLOYMENT_ARCH") not in ("do", "local"):
                        node_zone = node.metadata.labels["failure-domain.beta.kubernetes.io/zone"]
                        node_zone_list.append(node_zone)
                    node_name_list.append(node_name)

            self.settings.set("NODES_NAMES", node_name_list)
            self.settings.set("NODES_ZONES", node_zone_list)
            self.settings.set("NODES_IPS", node_ip_list)

            if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "gke", "do", "local", "aks"):
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
        if not self.settings.get("REDIS_TYPE"):
            logger.info("STANDALONE, CLUSTER")
            self.settings.set("REDIS_TYPE", click.prompt("Please enter redis type", default="CLUSTER"))

        if not self.settings.get("INSTALL_REDIS"):
            logger.info("For the following prompt if placed [N] the Redis is assumed to be"
                        " installed or remotely provisioned")
            self.settings.set("INSTALL_REDIS", confirm_yesno("Install Redis", default=True))

        if self.settings.get("INSTALL_REDIS") == "Y":
            if not self.settings.get("REDIS_MASTER_NODES"):
                self.settings.set("REDIS_MASTER_NODES",
                                  click.prompt("The number of master node. Minimum is 3", default=3))

            if not self.settings.get("REDIS_NODES_PER_MASTER"):
                self.settings.set("REDIS_NODES_PER_MASTER", click.prompt("The number of nodes per master node",
                                                                         default=2))

            if not self.settings.get("REDIS_NAMESPACE"):
                self.settings.set("REDIS_NAMESPACE", click.prompt("Please enter a namespace for Redis cluster",
                                                                  default="gluu-redis-cluster"))
        else:
            # Placing password in kubedb is currently not supported. # Todo: Remove else once supported
            if not self.settings.get("REDIS_PW"):
                self.settings.set("REDIS_PW", prompt_password("Redis"))

        if not self.settings.get("REDIS_URL"):
            if self.settings.get("INSTALL_REDIS") == "Y":
                redis_url_prompt = "redis-cluster.{}.svc.cluster.local:6379".format(
                    self.settings.get("REDIS_NAMESPACE"))
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
            self.settings.set("REDIS_URL", redis_url_prompt)

    def prompt_test_environment(self):
        """Prompts for test enviornment.
        """
        logger.info("A test environment means that the installer will strip all resource requirements, "
                    "and hence will use as much as needed only. The pods are subject to eviction. Please use "
                    " at least 8GB Ram , 4 CPU, and 50 GB disk.")
        self.settings.set("TEST_ENVIRONMENT", confirm_yesno("Is this a test environment."))

    def prompt_ssh_key(self):
        """Prompts for ssh key if
        """
        self.settings.set("NODE_SSH_KEY", click.prompt(
            "Please enter the ssh key path if exists to login into the nodes created. This ssh key will only"
            " be used to delete folders created on the nodes by the setup if the user uses local volumes",
            default="~/.ssh/id_rsa",
        ))

    def prompt_aws(self):
        """Prompts for AWS Load balancer information
        """
        lb_map = {
            1: "clb",
            2: "nlb",
            3: "alb",
        }

        if self.settings.get("AWS_LB_TYPE") not in lb_map.values():
            print("|-----------------------------------------------------------------|")
            print("|                     AWS Loadbalancer type                       |")
            print("|-----------------------------------------------------------------|")
            print("| [1] Classic Load Balancer (CLB) [default]                       |")
            print("| [2] Network Load Balancer (NLB - Alpha) -- Static IP            |")
            print("| [3] Application Load Balancer (ALB - Alpha) DEV_ONLY            |")
            print("|-----------------------------------------------------------------|")

            choice = click.prompt("Loadbalancer type", default=1)
            self.settings.set("AWS_LB_TYPE", lb_map.get(choice, "clb"))
            if self.settings.get("AWS_LB_TYPE") == "alb":
                logger.info("A prompt later during installation will appear to input the ALB DNS address")

        if not self.settings.get("USE_ARN"):
            self.settings.set("USE_ARN", confirm_yesno(
                "Are you terminating SSL traffic at LB and using certificate from AWS"))

        if not self.settings.get("ARN_AWS_IAM") and self.settings.get("USE_ARN") == "Y":
            # no default means it will try to prompt in loop until user inputs
            self.settings.set("ARN_AWS_IAM", click.prompt(
                "Enter aws-load-balancer-ssl-cert arn quoted ('arn:aws:acm:us-west-2:XXXXXXXX:"
                "certificate/XXXXXX-XXXXXXX-XXXXXXX-XXXXXXXX')"
            ))

    def prompt_persistence_backend(self):
        """Prompts for persistence backend layer
        """
        persistence_map = {
            1: "ldap",
            2: "couchbase",
            3: "hybrid",
        }

        if self.settings.get("PERSISTENCE_BACKEND") not in persistence_map.values():
            print("|------------------------------------------------------------------|")
            print("|                     Persistence layer                            |")
            print("|------------------------------------------------------------------|")
            print("| [1] WrenDS [default]                                             |")
            print("| [2] Couchbase [Testing Phase]                                    |")
            print("| [3] Hybrid(WrenDS + Couchbase)[Testing Phase]                    |")
            print("|------------------------------------------------------------------|")

            choice = click.prompt("Persistence layer", default=1)
            self.settings.set("PERSISTENCE_BACKEND", persistence_map.get(choice, "ldap"))

        if self.settings.get("PERSISTENCE_BACKEND") == "ldap":
            self.enabled_services.append("ldap")

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

        if self.settings.get("HYBRID_LDAP_HELD_DATA") not in hybrid_ldap_map.values():
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
            self.settings.set("HYBRID_LDAP_HELD_DATA", hybrid_ldap_map.get(choice, "default"))

    def prompt_app_volume_type(self):
        """Prompts for volume type
        """
        vol_choice = 0
        if self.settings.get("DEPLOYMENT_ARCH") == "eks":
            print("|------------------------------------------------------------------|")
            print("|Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)     |")
            print("|                    MultiAZ - Supported                           |")
            print("|------------------------------------------------------------------|")
            print("| [6]  volumes on host                                             |")
            print("| [7]  EBS volumes dynamically provisioned [default]               |")
            print("| [8]  EBS volumes statically provisioned                          |")
            vol_choice = click.prompt("What type of volume path", default=7)
        elif self.settings.get("DEPLOYMENT_ARCH") == "gke":
            print("|------------------------------------------------------------------|")
            print("|Google Cloud Engine - Google Kubernetes Engine                    |")
            print("|------------------------------------------------------------------|")
            print("| [11]  volumes on host                                            |")
            print("| [12]  Persistent Disk  dynamically provisioned [default]         |")
            print("| [13]  Persistent Disk  statically provisioned                    |")
            vol_choice = click.prompt("What type of volume path", default=12)
        elif self.settings.get("DEPLOYMENT_ARCH") == "aks":
            print("|------------------------------------------------------------------|")
            print("|Microsoft Azure                                                   |")
            print("|------------------------------------------------------------------|")
            print("| [16] volumes on host                                             |")
            print("| [17] Persistent Disk  dynamically provisioned                    |")
            print("| [18] Persistent Disk  statically provisioned                     |")
            vol_choice = click.prompt("What type of volume path", default=17)
        elif self.settings.get("DEPLOYMENT_ARCH") == "do":
            print("|------------------------------------------------------------------|")
            print("|Digital Ocean                                                     |")
            print("|------------------------------------------------------------------|")
            print("| [21] volumes on host                                             |")
            print("| [22] Persistent Disk  dynamically provisioned                    |")
            print("| [23] Persistent Disk  statically provisioned                     |")
            vol_choice = click.prompt("What type of volume path", default=22)
        elif self.settings.get("DEPLOYMENT_ARCH") == "local":
            print("|------------------------------------------------------------------|")
            print("|Local Deployment                                                  |")
            print("|------------------------------------------------------------------|")
            print("| [26] OpenEBS Local PV Hostpath                                   |")
            print("|------------------------------------------------------------------|")
            logger.info("OpenEBS must be installed before")
            vol_choice = click.prompt("What type of volume path", default=26)
        self.settings.set("APP_VOLUME_TYPE", vol_choice)

    def prompt_volumes(self):
        """Prompts for all info needed for volume creation on cloud or onpremise
        """
        if self.settings.get("DEPLOYMENT_ARCH") == "microk8s":
            self.settings.set("APP_VOLUME_TYPE", 1)

        elif self.settings.get("DEPLOYMENT_ARCH") == "minikube":
            self.settings.set("APP_VOLUME_TYPE", 2)

        if not self.settings.get("APP_VOLUME_TYPE"):
            self.prompt_app_volume_type()

        if self.settings.get("APP_VOLUME_TYPE") in (8, 13):
            self.prompt_volumes_identifier()

        if self.settings.get("APP_VOLUME_TYPE") == 18:
            self.prompt_disk_uris()

        if not self.settings.get("LDAP_JACKRABBIT_VOLUME") and \
                self.settings.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke"):
            logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
            logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
            logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
            self.settings.set("LDAP_JACKRABBIT_VOLUME", click.prompt("Please enter the volume type.", default="io1"))

    def prompt_cache_type(self):
        """Prompt cache type
        """
        gluu_cache_map = {
            1: "NATIVE_PERSISTENCE",
            2: "IN_MEMORY",
            3: "REDIS",
        }
        if self.settings.get("GLUU_CACHE_TYPE") not in gluu_cache_map.values():
            print("|------------------------------------------------------------------|")
            print("|                     Cache layer                                  |")
            print("|------------------------------------------------------------------|")
            print("| [1] NATIVE_PERSISTENCE [default]                                 |")
            print("| [2] IN_MEMORY                                                    |")
            print("| [3] REDIS                                                        |")
            print("|------------------------------------------------------------------|")
            choice = click.prompt("Cache layer", default=1)
            self.settings.set("GLUU_CACHE_TYPE", gluu_cache_map.get(choice, "NATIVE_PERSISTENCE"))
        if self.settings.get("GLUU_CACHE_TYPE") == "REDIS":
            self.prompt_redis()

    def check_settings_and_prompt(self):
        """Main property: called to setup all prompts and returns prompts in settings file.

        :return:
        """
        self.prompt_arch()
        self.prompt_gluu_namespace()
        self.prompt_optional_services()
        self.prompt_gluu_gateway()
        self.prompt_jackrabbit()
        self.prompt_istio()

        if not self.settings.get("TEST_ENVIRONMENT") and \
                self.settings.get("DEPLOYMENT_ARCH") == "microk8s" and \
                self.settings.get("DEPLOYMENT_ARCH") == "minikube":
            self.prompt_test_environment()

        if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "gke", "do", "local", "aks"):
            if not self.settings.get("NODE_SSH_KEY"):
                self.prompt_ssh_key()

        if not self.settings.get("HOST_EXT_IP"):
            ip = self.gather_ip
            self.settings.set("HOST_EXT_IP", ip)

            if self.settings.get("DEPLOYMENT_ARCH") == "eks":
                self.prompt_aws()

        if self.settings.get("DEPLOYMENT_ARCH") == "gke":
            self.prompt_gke()

        self.prompt_persistence_backend()

        if self.settings.get("PERSISTENCE_BACKEND") == "hybrid":
            self.prompt_hybrid_ldap_held_data()

        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") or \
                self.settings.get("INSTALL_JACKRABBIT") == "Y":
            self.prompt_volumes()

        if not self.settings.get("DEPLOY_MULTI_CLUSTER") and self.settings.get("PERSISTENCE_BACKEND") in (
                "hybrid", "couchbase"):
            self.prompt_couchbase_multi_cluster()

        self.prompt_cache_type()
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            self.prompt_couchbase()

        if self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            self.prompt_backup()

        self.prompt_config()
        self.prompt_image_name_tag()
        self.prompt_replicas()
        self.prompt_storage()

        if self.settings.get("CONFIRM_PARAMS") != "Y":
            self.confirm_params()

        self.settings.set("ENABLED_SERVICES_LIST", self.enabled_services)
