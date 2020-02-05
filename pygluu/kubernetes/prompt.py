#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 License terms and conditions:
 https://www.gluu.org/license/enterprise-edition/
"""

from pathlib import Path
import subprocess
import ipaddress
import re
import string
import shutil
import random
import json
import base64
from getpass import getpass
from .kubeapi import Kubernetes, get_logger

logger = get_logger("gluu-prompt        ")


def subprocess_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout


class Prompt(object):
    def __init__(self):
        self.settings = self.default_settings
        self.kubernetes = Kubernetes()
        self.get_settings()
        self.config_settings = {"hostname": "", "country_code": "", "state": "", "city": "", "admin_pw": "",
                                "ldap_pw": "", "email": "", "org_name": ""}

    @property
    def default_settings(self):
        default_settings = dict(ACCEPT_GLUU_LICENSE="",
                                GLUU_HELM_RELEASE_NAME="",
                                NGINX_INGRESS_RELEASE_NAME="",
                                NGINX_INGRESS_NAMESPACE="",
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
                                NUMBER_OF_EXPECTED_USERS="",
                                EXPECTED_TRANSACTIONS_PER_SEC="",
                                USING_CODE_FLOW="",
                                USING_SCIM_FLOW="",
                                USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW="",
                                DEPLOY_MULTI_CLUSTER="",
                                HYBRID_LDAP_HELD_DATA="",
                                LDAP_VOLUME="",
                                LDAP_VOLUME_TYPE="",
                                LDAP_STATIC_VOLUME_ID="",
                                LDAP_STATIC_DISK_URI="",
                                OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE="",
                                ACCEPT_EFS_NOTES="",
                                EFS_FILE_SYSTEM_ID="",
                                EFS_AWS_REGION="",
                                EFS_DNS="",
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
                                OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE="",
                                NFS_STORAGE_SIZE="",
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
                                CASA_IMAGE_NAME="gluufederation/casa",
                                CASA_IMAGE_TAG="4.2.0_dev",
                                CONFIG_IMAGE_NAME="gluufederation/config-init",
                                CONFIG_IMAGE_TAG="4.1.0_dev",
                                CACHE_REFRESH_ROTATE_IMAGE_NAME="gluufederation/cr-rotate",
                                CACHE_REFRESH_ROTATE_IMAGE_TAG="4.1.0_dev",
                                KEY_ROTATE_IMAGE_NAME="gluufederation/key-rotation",
                                KEY_ROTATE_IMAGE_TAG="4.1.0_dev",
                                LDAP_IMAGE_NAME="gluufederation/wrends",
                                LDAP_IMAGE_TAG="4.1.0_dev",
                                OXAUTH_IMAGE_NAME="gluufederation/oxauth",
                                OXAUTH_IMAGE_TAG="4.1.0_dev",
                                OXD_IMAGE_NAME="gluufederation/oxd-server",
                                OXD_IMAGE_TAG="4.1.0_dev",
                                OXPASSPORT_IMAGE_NAME="gluufederation/oxpassport",
                                OXPASSPORT_IMAGE_TAG="4.1.0_dev",
                                OXSHIBBOLETH_IMAGE_NAME="gluufederation/oxshibboleth",
                                OXSHIBBOLETH_IMAGE_TAG="4.1.0_dev",
                                OXTRUST_IMAGE_NAME="gluufederation/oxtrust",
                                OXTRUST_IMAGE_TAG="4.1.0_dev",
                                PERSISTENCE_IMAGE_NAME="gluufederation/persistence",
                                PERSISTENCE_IMAGE_TAG="4.1.0_dev",
                                RADIUS_IMAGE_NAME="gluufederation/radius",
                                RADIUS_IMAGE_TAG="4.1.0_dev",
                                CONFIRM_PARAMS="N",
                                )
        return default_settings

    def write_variables_to_file(self):
        """Write settings out toa file
        """
        with open(Path('./settings.json'), 'w+') as file:
            json.dump(self.settings, file, indent=2)

    def get_settings(self):
        """Get merged settings (default and custom settings from local Python file).
        """
        filename = Path("./settings.json")
        try:
            with open(filename) as f:
                custom_settings = json.load(f)
            self.settings.update(custom_settings)
        except FileNotFoundError:
            pass

    def confirm_params(self):
        hidden_settings = ["NODES_IPS", "NODES_ZONES", "NODES_NAMES",
                           "COUCHBASE_PASSWORD", "LDAP_PW", "ADMIN_PW", "OXD_SERVER_PW"]
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
        self.write_variables_to_file()
        return self.settings

    def prompt_image_name_tag(self):
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
        self.write_variables_to_file()

    def prompt_volumes_identitfier(self):
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            if not self.settings["LDAP_STATIC_VOLUME_ID"]:
                logger.info("EBS Volume ID example: vol-049df61146c4d7901")
                logger.info("Persistent Disk Name example: "
                            "gke-demoexamplegluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd")
                prompt = input("Please enter Persistent Disk Name or EBS Volume ID for LDAP:")
                self.settings["LDAP_STATIC_VOLUME_ID"] = prompt
        self.write_variables_to_file()

    def prompt_disk_uris(self):
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            if not self.settings["LDAP_STATIC_DISK_URI"]:
                logger.info("DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                            "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk")
                prompt = input("Please enter the disk uri for LDAP:")
                self.settings["LDAP_STATIC_DISK_URI"] = prompt
        self.write_variables_to_file()

    def prompt_gke(self):
        if not self.settings["GMAIL_ACCOUNT"]:
            prompt = input("Please enter valid email for Google Cloud account:")
            self.settings["GMAIL_ACCOUNT"] = prompt

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
        self.write_variables_to_file()

    def prompt_config(self):
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
            self.settings["ADMIN_PW"] = self.prompt_password("oxTrust")

        if not self.settings["LDAP_PW"]:
            if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                    self.settings["PERSISTENCE_BACKEND"] == "ldap":
                self.settings["LDAP_PW"] = self.prompt_password("LDAP")
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
                    "ingress.crt and ingress.key respectivley")
        # Prepare generate.json and output it
        self.config_settings["hostname"] = self.settings["GLUU_FQDN"]
        self.config_settings["country_code"] = self.settings["COUNTRY_CODE"]
        self.config_settings["state"] = self.settings["STATE"]
        self.config_settings["city"] = self.settings["CITY"]
        self.config_settings["admin_pw"] = self.settings["ADMIN_PW"]
        self.config_settings["ldap_pw"] = self.settings["LDAP_PW"]
        if self.settings["PERSISTENCE_BACKEND"] == "couchbase":
            self.config_settings["ldap_pw"] = self.settings["COUCHBASE_PASSWORD"]
        self.config_settings["email"] = self.settings["EMAIL"]
        self.config_settings["org_name"] = self.settings["ORG_NAME"]
        with open(Path('./config/base/generate.json'), 'w+') as file:
            json.dump(self.config_settings, file)
        self.write_variables_to_file()

    def prompt_storage(self):
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            if not self.settings["LDAP_STORAGE_SIZE"]:
                prompt = input("Size of ldap volume storage [4Gi]:")
                if not prompt:
                    prompt = "4Gi"
                self.settings["LDAP_STORAGE_SIZE"] = prompt

        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            if not self.settings["OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE"]:
                prompt = input("Size of Shared-Shib volume storage [4Gi]:")
                if not prompt:
                    prompt = "4Gi"
                self.settings["OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE"] = prompt
        else:
            self.settings["OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE"] = "4Gi"
        self.write_variables_to_file()

    def prompt_replicas(self):
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
        self.write_variables_to_file()

    def prompt_password(self, password):
        chars = string.ascii_letters + string.digits + string.punctuation + string.punctuation
        keystore_chars = string.ascii_letters + string.digits
        chars = chars.replace('"', '')
        while True:
            while True:
                random_password = ''.join(random.choice(chars) for _ in range(6))
                regex_bool = re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z0-9\S]{6,}$', random_password)
                if regex_bool:
                    break
            if password == "OXD-server":
                random_password = ''.join(random.choice(keystore_chars) for _ in range(12))

            string_random_password = random_password[:1] + "***" + random_password[4:]
            pw_prompt = getpass(prompt='{} password [{}]: '.format(password, string_random_password), stream=None)
            if not pw_prompt:
                pw_prompt = random_password
                confirm_pw_prompt = random_password
            else:
                confirm_pw_prompt = getpass(prompt='Confirm password: ', stream=None)
                regex_bool = True
                if not password == "OXD-server":
                    regex_bool = re.match('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z0-9\S]{6,}$', pw_prompt)

            if confirm_pw_prompt != pw_prompt:
                logger.error("Passwords do not match")
            elif not regex_bool:
                logger.error("Password does not meet requirements. The password must container one digit, one uppercase"
                             " letter, one lower case letter and one symbol")
            else:
                logger.info("Success! {} password was set.".format(password))
                return pw_prompt

    def prompt_couchbase(self):
        self.prompt_arch()
        self.prompt_gluu_namespace()
        if self.settings["INSTALL_COUCHBASE"] == "N":
            if not self.settings["COUCHBASE_CRT"]:
                prompt = input("Place the Couchbase certificate authority certificate in a file called couchbase.crt at "
                               "the same location as the installation script. Continue?"
                               "This can also be found in your couchbase UI Security > Root Certificate: ")
                with open(Path("./couchbase.crt")) as content_file:
                    ca_crt = content_file.read()
                    encoded_ca_crt_bytes = base64.b64encode(ca_crt_content.encode("utf-8"))
                    encoded_ca_crt_string = str(encoded_ca_crt_bytes, "utf-8")
                self.settings["COUCHBASE_CRT"] = encoded_ca_crt_string

        if not self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"]:
            prompt = input("Override couchbase-cluster.yaml with a custom couchbase-cluster.yaml [N][Y/N]: ")
            if prompt == "Y" or prompt == "y":
                prompt = "Y"
                try:
                    shutil.copy(Path("./couchbase-cluster.yaml"), Path("./couchbase/couchbase-cluster.yaml"))
                except FileNotFoundError:
                    logger.error("An override option has been chosen but couchbase-cluster.yaml file "
                                 "could not be found at the current path. Please place the override file under the name"
                                 " couchbase-cluster.yaml in the same directory pygluu-kubernetes.pyz exists ")
                    raise SystemExit(1)
            else:
                prompt = "N"
            self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"] = prompt

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
            default_cb_url_prompt = "{}.{}.svc.cluster.local".format(cb_cluster_name_prompt,
                                                                     cb_cluster_namespace_prompt)

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
            self.settings["COUCHBASE_PASSWORD"] = self.prompt_password("Couchbase")

        if not self.settings['COUCHBASE_SUBJECT_ALT_NAME']:
            self.settings['COUCHBASE_SUBJECT_ALT_NAME'] = "DNS:*.{}.{}.svc,DNS:*.{}.svc,DNS:*.{}.{}" \
                .format(self.settings["COUCHBASE_CLUSTER_NAME"], self.settings["COUCHBASE_NAMESPACE"],
                        self.settings["COUCHBASE_NAMESPACE"], self.settings["COUCHBASE_CLUSTER_NAME"],
                        self.settings["COUCHBASE_FQDN"])
        self.write_variables_to_file()
        return self.settings

    def prompt_arch(self):
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

    def prompt_gluu_namespace(self):
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
            if not self.settings["OXD_APPLICATION_KEYSTORE_CN"]:
                prompt = input("oxd server application keystore name [oxd_server]?")
                if not prompt:
                    prompt = "oxd_server"
                self.settings["OXD_APPLICATION_KEYSTORE_CN"] = prompt
            if not self.settings["OXD_ADMIN_KEYSTORE_CN"]:
                prompt = input("oxd server admin keystore name [oxd_server]?")
                if not prompt:
                    prompt = "oxd_server"
                self.settings["OXD_ADMIN_KEYSTORE_CN"] = prompt
            if not self.settings["OXD_SERVER_PW"]:
                self.settings["OXD_SERVER_PW"] = self.prompt_password("OXD-server")

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
            logger.warning("[W] Cannot determine IP address")
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

    @property
    def check_settings_and_prompt(self):
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

        self.prompt_arch()
        self.prompt_gluu_namespace()
        self.prompt_optional_services()
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
            if not self.settings["OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE"] and \
                    self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
                print("|------------------------------------------------------------------|")
                print("|                     Shared Shibboleth Volume                     |")
                print("|------------------------------------------------------------------|")
                print("| [1] local storage [default]                                      |")
                print("| [2] EFS - Required for production on AWS                         |")
                print("|------------------------------------------------------------------|")
                prompt = input("Type of Shibboleth volume[1]")
                if prompt == "2":
                    prompt = "efs"
                else:
                    prompt = "local_storage"
                self.settings["OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE"] = prompt
            if not self.settings["ACCEPT_EFS_NOTES"] and \
                    self.settings["OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE"] == "efs":
                prompt = input("Make sure EFS is created, EFS must be inside the same region as the EKS cluster, "
                               "VPC of EKS and EFS are the same, and security group of EFS allows all connections "
                               "from EKS nodes[Y/N].[Y]")
                if not prompt:
                    prompt = "Y"
                self.settings["ACCEPT_EFS_NOTES"] = prompt

                if not self.settings["EFS_FILE_SYSTEM_ID"]:
                    prompt = input("Enter FileSystemID (fs-xxx):")
                    self.settings["EFS_FILE_SYSTEM_ID"] = prompt

                if not self.settings["EFS_AWS_REGION"]:
                    prompt = input("Enter AWS region (us-west-2):")
                    self.settings["EFS_AWS_REGION"] = prompt

                if not self.settings["EFS_DNS"]:
                    prompt = input("Enter EFS dns name (fs-xxx.us-west-2.amazonaws.com):")
                    self.settings["EFS_DNS"] = prompt

            aws_lb_type = ["nlb", "clb"]
            if self.settings["AWS_LB_TYPE"] not in aws_lb_type:
                print("|-----------------------------------------------------------------|")
                print("|                     AWS Loadbalancer type                       |")
                print("|-----------------------------------------------------------------|")
                print("| [1] Classic Load Balancer (CLB) [default]                       |")
                print("| [2] Network Load Balancer (NLB - Alpha) -- Static IP            |")
                print("|-----------------------------------------------------------------|")
                prompt = input("Loadbalancer type?[1]")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                if prompt == 2:
                    self.settings["AWS_LB_TYPE"] = "nlb"
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
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            self.settings["COUCHBASE_USER"] = "admin"
            self.settings["COUCHBASE_URL"] = "couchbase"
            if not self.settings["LDAP_VOLUME_TYPE"]:
                print("|------------------------------------------------------------------|")
                print("|                     Local Deployments                            |")
                print("|------------------------------------------------------------------|")
                print("| [1]  Microk8s | LDAP volumes on host [default]                   |")
                print("| [2]  Minikube | LDAP volumes on host                             |")
                print("|------------------------------------------------------------------|")
                print("|                     Cloud Deployments                            |")
                print("|------------------------------------------------------------------|")
                print("|Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)     |")
                print("|                    MultiAZ - Supported                           |")
                print("|------------------------------------------------------------------|")
                print("| [6]  EKS      | LDAP volumes on host                             |")
                print("| [7]  EKS      | LDAP EBS volumes dynamically provisioned         |")
                print("| [8]  EKS      | LDAP EBS volumes statically provisioned          |")
                print("| [9]  EKS      | LDAP EFS volume                                  |")
                print("|------------------------------------------------------------------|")
                print("|Google Cloud Engine - Google Kubernetes Engine                    |")
                print("|------------------------------------------------------------------|")
                print("| [11]  GKE     | LDAP volumes on host                             |")
                print("| [12]  GKE     | LDAP Persistent Disk  dynamically provisioned    |")
                print("| [13]  GKE     | LDAP Persistent Disk  statically provisioned     |")
                print("|------------------------------------------------------------------|")
                print("|Microsoft Azure                                                   |")
                print("|------------------------------------------------------------------|")
                print("| [16] Azure    | LDAP volumes on host                             |")
                print("| [17] Azure    | LDAP Persistent Disk  dynamically provisioned    |")
                print("| [18] Azure    | LDAP Persistent Disk  statically provisioned     |")
                print("|------------------------------------------------------------------|")
                print("|                             Notes                                |")
                print("|------------------------------------------------------------------|")
                print("|             Any other option will default to choice 1            |")
                print("|------------------------------------------------------------------|")
                prompt = input("What type of LDAP deployment[1]")
                if not prompt:
                    prompt = 1
                prompt = int(prompt)
                self.settings["LDAP_VOLUME_TYPE"] = prompt

            if self.settings["LDAP_VOLUME_TYPE"] == 8 or self.settings["LDAP_VOLUME_TYPE"] == 13:
                self.prompt_volumes_identitfier()

            if self.settings["LDAP_VOLUME_TYPE"] == 18:
                self.prompt_disk_uris()

            if self.settings["LDAP_VOLUME_TYPE"] > 2 and not self.settings["LDAP_VOLUME"]:
                logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
                logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
                logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
                prompt = input("Please enter the volume type.[io1]")
                if not prompt:
                    prompt = "io1"
                self.settings["LDAP_VOLUME"] = prompt

            if not self.settings["ACCEPT_EFS_NOTES"] and self.settings["LDAP_VOLUME"] == 3:
                prompt = input("Make sure EFS is created, EFS must be inside the same region as the EKS cluster, "
                               "VPC of EKS and EFS are the same, and security group of EFS allows all connections "
                               "from EKS nodes[Y] ")
                if not prompt:
                    prompt = "Y"
                self.settings["ACCEPT_EFS_NOTES"] = prompt

        if not self.settings["DEPLOY_MULTI_CLUSTER"]:
            if self.settings["PERSISTENCE_BACKEND"] == "hybrid" \
                    or self.settings["PERSISTENCE_BACKEND"] == "couchbase":
                print("|------------------------------------------------------------------|")
                print("|         Is this a multi-cloud/region setup[N] ?[Y/N]             |")
                print("|------------------------------------------------------------------|")
                print("|                             Notes                                |")
                print("|------------------------------------------------------------------|")
                print("If you are planning for a multi-cloud/region setup and this is the first cluster answer N or"
                      "leave blank. You will answer Y for the second and more cluster setup   ")
                print("|------------------------------------------------------------------|")
                prompt = input("Is this a multi-cloud/region setup[N]")
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

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "couchbase":
            if not self.settings["INSTALL_COUCHBASE"]:
                logger.info("For the following prompt  if placed [N] the couchbase is assumed to be"
                            " installed or remotely provisioned")
                prompt = input("Install Couchbase[Y/N]?[Y]")
                if not prompt:
                    prompt = "Y"
                self.settings["INSTALL_COUCHBASE"] = prompt
            self.prompt_couchbase()

        self.prompt_config()
        self.prompt_image_name_tag()
        self.prompt_replicas()
        self.prompt_storage()
        self.settings["NFS_STORAGE_SIZE"] = self.settings["OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE"]
        if self.settings["CONFIRM_PARAMS"] != "Y":
            self.confirm_params()
        self.write_variables_to_file()

        return self.settings
