"""
pygluu.kubernetes.kustomize
~~~~~~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
"""
import base64
import contextlib
import os
import shutil
import socket
import time
from ast import literal_eval
from pathlib import Path

from pygluu.kubernetes.helpers import get_logger, copy, exec_cmd, ssh_and_remove
from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.pycert import check_cert_with_private_key
from pygluu.kubernetes.yamlparser import Parser
from pygluu.kubernetes.settings import SettingsHandler

logger = get_logger("gluu-kustomize     ")

# TEST ENVIORNMENT DEPLOYMENTS
local_ldap_minikube_folder = Path("./ldap/overlays/minikube/local-storage/")
local_jcr_minikube_folder = Path("./jackrabbit/overlays/minikube/local-storage/")
local_ldap_microk8s_folder = Path("./ldap/overlays/microk8s/local-storage/")
local_jcr_microk8s_folder = Path("./jackrabbit/overlays/microk8s/local-storage/")
# AWS
local_ldap_eks_folder = Path("./ldap/overlays/eks/local-storage/")
local_jcr_eks_folder = Path("./jackrabbit/overlays/eks/local-storage/")
dynamic_ldap_eks_folder = Path("./ldap/overlays/eks/dynamic-ebs/")
dynamic_jcr_eks_folder = Path("./jackrabbit/overlays/eks/dynamic-ebs/")
static_ldap_eks_folder = Path("./ldap/overlays/eks/static-ebs/")
static_jcr_eks_folder = Path("./jackrabbit/overlays/eks/static-ebs/")
# GCE
local_ldap_gke_folder = Path("./ldap/overlays/gke/local-storage/")
local_jcr_gke_folder = Path("./jackrabbit/overlays/gke/local-storage/")
dynamic_ldap_gke_folder = Path("./ldap/overlays/gke/dynamic-pd/")
dynamic_jcr_gke_folder = Path("./jackrabbit/overlays/gke/dynamic-pd/")
static_ldap_gke_folder = Path("./ldap/overlays/gke/static-pd/")
static_jcr_gke_folder = Path("./jackrabbit/overlays/gke/static-pd/")
# AZURE
local_ldap_azure_folder = Path("./ldap/overlays/azure/local-storage/")
local_jcr_azure_folder = Path("./jackrabbit/overlays/azure/local-storage/")
dynamic_ldap_azure_folder = Path("./ldap/overlays/azure/dynamic-dn/")
dynamic_jcr_azure_folder = Path("./jackrabbit/overlays/azure/dynamic-dn/")
static_ldap_azure_folder = Path("./ldap/overlays/azure/static-dn/")
static_jcr_azure_folder = Path("./jackrabbit/overlays/azure/static-dn/")
# DIGITAL OCEAN
local_ldap_do_folder = Path("./ldap/overlays/do/local-storage/")
local_jcr_do_folder = Path("./jackrabbit/overlays/do/local-storage/")
dynamic_ldap_do_folder = Path("./ldap/overlays/do/dynamic-dn/")
dynamic_jcr_do_folder = Path("./jackrabbit/overlays/do/dynamic-dn/")
static_ldap_do_folder = Path("./ldap/overlays/do/static-dn/")
static_jcr_do_folder = Path("./jackrabbit/overlays/do/static-dn/")
# LOCAL DEPLOYMENTS
hostpath_ldap_local_folder = Path("./ldap/overlays/local/hostpath/")
hostpath_jcr_local_folder = Path("./jackrabbit/overlays/local/hostpath/")


def register_op_client(namespace, client_name, op_host, oxd_url):
    """Registers an op client using oxd.

    :param namespace:
    :param client_name:
    :param op_host:
    :param oxd_url:
    :return:
    """
    kubernetes = Kubernetes()
    logger.info("Registering a client : {}".format(client_name))
    oxd_id, client_id, client_secret = "", "", ""

    data = '{"redirect_uris": ["https://' + op_host + '/gg-ui/"], "op_host": "' + op_host + \
           '", "post_logout_redirect_uris": ["https://' + op_host + \
           '/gg-ui/"], "scope": ["openid", "oxd", "permission", "username"], ' \
           '"grant_types": ["authorization_code", "client_credentials"], "client_name": "' + client_name + '"}'

    exec_curl_command = ["curl", "-k", "-s", "--location", "--request", "POST",
                         "{}/register-site".format(oxd_url), "--header",
                         "Content-Type: application/json", "--data-raw",
                         data]
    try:
        client_registration_response = \
            kubernetes.connect_get_namespaced_pod_exec(exec_command=exec_curl_command,
                                                       app_label="app=oxauth",
                                                       container="oxauth",
                                                       namespace=namespace,
                                                       stdout=False)

        client_registration_response_dict = literal_eval(client_registration_response)
        oxd_id = client_registration_response_dict["oxd_id"]
        client_id = client_registration_response_dict["client_id"]
        client_secret = client_registration_response_dict["client_secret"]
    except (IndexError, Exception):
        manual_curl_command = " ".join(exec_curl_command)
        logger.error("Registration of client : {} failed. Please do so manually by calling\n{}".format(
            client_name, manual_curl_command))
    return oxd_id, client_id, client_secret


class Kustomize(object):
    def __init__(self, timeout=300):

        self.settings = SettingsHandler()
        self.all_apps = self.settings.get("ENABLED_SERVICES_LIST")
        self.kubernetes = Kubernetes()
        self.timeout = timeout
        self.kubectl = self.detect_kubectl
        self.output_yaml_directory, self.ldap_kustomize_yaml_directory, self.jcr_kustomize_yaml_directory \
            = self.set_output_yaml_directory
        self.config_yaml = str(self.output_yaml_directory.joinpath("config.yaml").resolve())
        self.ldap_yaml = str(self.output_yaml_directory.joinpath("ldap.yaml").resolve())
        self.jackrabbit_yaml = str(self.output_yaml_directory.joinpath("jackrabbit.yaml").resolve())
        self.persistence_yaml = str(self.output_yaml_directory.joinpath("persistence.yaml").resolve())
        self.oxauth_yaml = str(self.output_yaml_directory.joinpath("oxauth.yaml").resolve())
        self.fido2_yaml = str(self.output_yaml_directory.joinpath("fido2.yaml").resolve())
        self.scim_yaml = str(self.output_yaml_directory.joinpath("scim.yaml").resolve())
        self.oxtrust_yaml = str(self.output_yaml_directory.joinpath("oxtrust.yaml").resolve())
        self.gluu_upgrade_yaml = str(self.output_yaml_directory.joinpath("upgrade.yaml").resolve())
        self.oxshibboleth_yaml = str(self.output_yaml_directory.joinpath("oxshibboleth.yaml").resolve())
        self.oxpassport_yaml = str(self.output_yaml_directory.joinpath("oxpassport.yaml").resolve())
        self.oxauth_key_rotate_yaml = str(self.output_yaml_directory.joinpath("oxauth-key-rotation.yaml").resolve())
        self.cr_rotate_yaml = str(self.output_yaml_directory.joinpath("cr-rotate.yaml").resolve())
        self.oxd_server_yaml = str(self.output_yaml_directory.joinpath("oxd-server.yaml").resolve())
        self.casa_yaml = str(self.output_yaml_directory.joinpath("casa.yaml").resolve())
        self.radius_yaml = str(self.output_yaml_directory.joinpath("radius.yaml").resolve())
        self.update_lb_ip_yaml = str(self.output_yaml_directory.joinpath("update-lb-ip.yaml").resolve())
        self.gg_ui_yaml = str(self.output_yaml_directory.joinpath("gluu-gateway-ui.yaml").resolve())
        self.gluu_istio_ingress_yaml = str(self.output_yaml_directory.joinpath("gluu-istio-ingress.yaml").resolve())
        self.adjust_yamls_for_fqdn_status = dict()
        self.gluu_secret = ""
        self.gluu_config = ""
        if self.settings.get("DEPLOYMENT_ARCH") == "gke":
            # Clusterrolebinding needs to be created for gke with CB or kubeDB installed
            if self.settings.get("INSTALL_REDIS") == "Y" or \
                    self.settings.get("INSTALL_GLUU_GATEWAY") == "Y" or \
                    self.settings.get("INSTALL_COUCHBASE") == "Y":
                user_account, stderr, retcode = exec_cmd("gcloud config get-value core/account")
                user_account = str(user_account, "utf-8").strip()

                user, stderr, retcode = exec_cmd("whoami")
                user = str(user, "utf-8").strip()
                cluster_role_binding_name = "cluster-admin-{}".format(user)
                self.kubernetes.create_cluster_role_binding(cluster_role_binding_name=cluster_role_binding_name,
                                                            user_name=user_account,
                                                            cluster_role_name="cluster-admin")

    @property
    def detect_kubectl(self):
        """Detect kubectl command"""

        if self.settings.get("DEPLOYMENT_ARCH") == "microk8s":
            kubectl = "microk8s.kubectl"
            # Check if running in container and settings.json mounted
            if Path("./installer-settings.json").exists():
                kubectl = "kubectl"
        else:
            kubectl = "kubectl"
        return kubectl

    def analyze_storage_class(self, storageclass):
        parser = Parser(storageclass, "StorageClass")
        if self.settings.get("DEPLOYMENT_ARCH") == "eks":
            parser["provisioner"] = "kubernetes.io/aws-ebs"
            parser["parameters"]["encrypted"] = "true"
            parser["parameters"]["type"] = self.settings.get("LDAP_JACKRABBIT_VOLUME")
            unique_zones = list(dict.fromkeys(self.settings.get("NODES_ZONES")))
            parser["allowedTopologies"][0]["matchLabelExpressions"][0]["values"] = unique_zones
            parser.dump_it()
        elif self.settings.get("DEPLOYMENT_ARCH") == "gke":
            parser["provisioner"] = "kubernetes.io/gce-pd"
            try:
                del parser["parameters"]["encrypted"]
            except KeyError:
                logger.info("Key not deleted as it does not exist inside yaml.")
            parser["parameters"]["type"] = self.settings.get("LDAP_JACKRABBIT_VOLUME")
            unique_zones = list(dict.fromkeys(self.settings.get("NODES_ZONES")))
            parser["allowedTopologies"][0]["matchLabelExpressions"][0]["values"] = unique_zones
            parser.dump_it()
        elif self.settings.get("DEPLOYMENT_ARCH") == "aks":
            parser["provisioner"] = "kubernetes.io/azure-disk"
            try:
                del parser["parameters"]["encrypted"]
                del parser["parameters"]["type"]
            except KeyError:
                logger.info("Key not deleted as it does not exist inside yaml.")
            parser["parameters"]["storageaccounttype"] = self.settings.get("LDAP_JACKRABBIT_VOLUME")
            unique_zones = list(dict.fromkeys(self.settings.get("NODES_ZONES")))
            parser["allowedTopologies"][0]["matchLabelExpressions"][0]["values"] = unique_zones
            parser.dump_it()
        elif self.settings.get("DEPLOYMENT_ARCH") == "do":
            parser["provisioner"] = "dobs.csi.digitalocean.com"
            try:
                del parser["parameters"]
                del parser["allowedTopologies"]
            except KeyError:
                logger.info("Key not deleted as it does not exist inside yaml.")
            parser.dump_it()
        elif self.settings.get('DEPLOYMENT_ARCH') == "microk8s":
            try:
                parser["provisioner"] = "microk8s.io/hostpath"
                del parser["allowedTopologies"]
                del parser["allowVolumeExpansion"]
                del parser["parameters"]
            except KeyError:
                logger.info("Key not deleted as it does not exist inside yaml.")
            parser.dump_it()
        elif self.settings.get('DEPLOYMENT_ARCH') == "minikube":
            try:
                parser["provisioner"] = "k8s.io/minikube-hostpath"
                del parser["allowedTopologies"]
                del parser["allowVolumeExpansion"]
                del parser["parameters"]
            except KeyError:
                logger.info("Key not deleted as it does not exist inside yaml.")
            parser.dump_it()

    @property
    def set_output_yaml_directory(self):

        output_yamls_folder = Path("gluu_microk8s_yamls")
        ldap_kustomize_yaml_directory = local_ldap_microk8s_folder
        jcr_kustomize_yaml_directory = local_jcr_microk8s_folder

        if self.settings.get("DEPLOYMENT_ARCH") == "minikube":
            copy(local_ldap_microk8s_folder, local_ldap_minikube_folder)
            copy(local_jcr_microk8s_folder, local_jcr_minikube_folder)
            output_yamls_folder = Path("gluu_minikube_yamls")
            ldap_kustomize_yaml_directory = local_ldap_minikube_folder
            jcr_kustomize_yaml_directory = local_jcr_minikube_folder

        elif self.settings.get("DEPLOYMENT_ARCH") == "eks":
            output_yamls_folder = Path("gluu_eks_yamls")
            if self.settings.get("APP_VOLUME_TYPE") == 7:
                self.analyze_storage_class(dynamic_ldap_eks_folder.joinpath("storageclasses.yaml"))
                self.analyze_storage_class(dynamic_jcr_eks_folder.joinpath("storageclasses.yaml"))
                ldap_kustomize_yaml_directory = dynamic_ldap_eks_folder
                jcr_kustomize_yaml_directory = dynamic_jcr_eks_folder

            elif self.settings.get("APP_VOLUME_TYPE") == 8:
                ldap_kustomize_yaml_directory = static_ldap_eks_folder
                jcr_kustomize_yaml_directory = static_jcr_eks_folder

            else:
                ldap_kustomize_yaml_directory = local_ldap_eks_folder
                jcr_kustomize_yaml_directory = local_jcr_eks_folder

        elif self.settings.get("DEPLOYMENT_ARCH") == "gke":
            output_yamls_folder = Path("gluu_gke_yamls")
            if self.settings.get("APP_VOLUME_TYPE") == 12:
                try:
                    shutil.rmtree(dynamic_ldap_gke_folder)
                except FileNotFoundError:
                    logger.info("Directory not found. Copying...")
                try:
                    shutil.rmtree(dynamic_jcr_gke_folder)
                except FileNotFoundError:
                    logger.info("Directory not found. Copying...")

                copy(dynamic_ldap_eks_folder, dynamic_ldap_gke_folder)
                copy(dynamic_jcr_eks_folder, dynamic_jcr_gke_folder)
                self.analyze_storage_class(dynamic_ldap_eks_folder.joinpath("storageclasses.yaml"))
                self.analyze_storage_class(dynamic_jcr_eks_folder.joinpath("storageclasses.yaml"))

                ldap_kustomize_yaml_directory = dynamic_ldap_eks_folder
                jcr_kustomize_yaml_directory = dynamic_jcr_eks_folder
            elif self.settings.get("APP_VOLUME_TYPE") == 13:
                ldap_kustomize_yaml_directory = static_ldap_gke_folder
                jcr_kustomize_yaml_directory = static_jcr_gke_folder

            else:
                ldap_kustomize_yaml_directory = local_ldap_gke_folder
                jcr_kustomize_yaml_directory = local_jcr_gke_folder

        elif self.settings.get("DEPLOYMENT_ARCH") == "aks":
            output_yamls_folder = Path("gluu_aks_yamls")
            if self.settings.get("APP_VOLUME_TYPE") == 17:
                copy(dynamic_ldap_eks_folder, dynamic_ldap_azure_folder)
                copy(dynamic_jcr_eks_folder, dynamic_jcr_azure_folder)

                self.analyze_storage_class(dynamic_ldap_azure_folder.joinpath("storageclasses.yaml"))
                self.analyze_storage_class(dynamic_jcr_azure_folder.joinpath("storageclasses.yaml"))

                ldap_kustomize_yaml_directory = dynamic_ldap_azure_folder
                jcr_kustomize_yaml_directory = dynamic_ldap_azure_folder

            elif self.settings.get("APP_VOLUME_TYPE") == 18:
                ldap_kustomize_yaml_directory = static_ldap_azure_folder
                jcr_kustomize_yaml_directory = static_jcr_azure_folder

            else:
                ldap_kustomize_yaml_directory = local_ldap_azure_folder
                jcr_kustomize_yaml_directory = local_jcr_azure_folder

        elif self.settings.get("DEPLOYMENT_ARCH") == "local":
            output_yamls_folder = Path("gluu_local_yamls")
            if self.settings.get("APP_VOLUME_TYPE") == 26:
                ldap_kustomize_yaml_directory = hostpath_ldap_local_folder
                jcr_kustomize_yaml_directory = hostpath_jcr_local_folder

        elif self.settings.get("DEPLOYMENT_ARCH") == "do":
            output_yamls_folder = Path("gluu_do_yamls")
            if self.settings.get("APP_VOLUME_TYPE") == 22:
                copy(dynamic_ldap_eks_folder, dynamic_ldap_do_folder)
                copy(dynamic_jcr_eks_folder, dynamic_jcr_do_folder)

                self.analyze_storage_class(dynamic_ldap_do_folder.joinpath("storageclasses.yaml"))
                self.analyze_storage_class(dynamic_jcr_do_folder.joinpath("storageclasses.yaml"))

                ldap_kustomize_yaml_directory = dynamic_ldap_do_folder
                jcr_kustomize_yaml_directory = dynamic_jcr_do_folder

            elif self.settings.get("APP_VOLUME_TYPE") == 23:
                ldap_kustomize_yaml_directory = static_ldap_do_folder
                jcr_kustomize_yaml_directory = static_jcr_do_folder

        if not output_yamls_folder.exists():
            os.mkdir(output_yamls_folder)
        return output_yamls_folder, ldap_kustomize_yaml_directory, jcr_kustomize_yaml_directory

    def adjust_fqdn_yaml_entries(self):
        if self.settings.get("IS_GLUU_FQDN_REGISTERED") == "Y" or \
                self.settings.get("DEPLOYMENT_ARCH") == "microk8s" or \
                self.settings.get("DEPLOYMENT_ARCH") == "minikube" or \
                self.settings.get("DEPLOYMENT_ARCH") == "gke" or \
                self.settings.get("DEPLOYMENT_ARCH") == "aks" or \
                self.settings.get("DEPLOYMENT_ARCH") == "do":
            for k, v in self.adjust_yamls_for_fqdn_status.items():
                parser = Parser(k, v)
                volume_mount_list = parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
                volume_list = parser["spec"]["template"]["spec"]["volumes"]

                if k != self.cr_rotate_yaml and k != self.gluu_upgrade_yaml:
                    if self.settings.get("DEPLOYMENT_ARCH") == "microk8s" or \
                            self.settings.get("DEPLOYMENT_ARCH") == "minikube" or \
                            self.settings.get("DEPLOYMENT_ARCH") == "gke" or \
                            self.settings.get("DEPLOYMENT_ARCH") == "aks" or \
                            self.settings.get("DEPLOYMENT_ARCH") == "do":
                        parser["spec"]["template"]["spec"]["hostAliases"][0]["hostnames"] = \
                            [self.settings.get("GLUU_FQDN")]
                        parser["spec"]["template"]["spec"]["hostAliases"][0]["ip"] = self.settings.get("HOST_EXT_IP")
                    else:
                        try:
                            del parser["spec"]["template"]["spec"]["hostAliases"]
                        except KeyError:
                            logger.info("Key not deleted as it does not exist inside yaml.")
                    try:
                        del parser["spec"]["template"]["spec"]["containers"][0]["command"]
                    except KeyError:
                        logger.info("Key not deleted as it does not exist inside yaml.")

                    update_lb_ip_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "update-lb-ip"), None)
                    if update_lb_ip_vm_index is not None:
                        del volume_mount_list[update_lb_ip_vm_index]
                    volume_list = parser["spec"]["template"]["spec"]["volumes"]
                    update_lb_ip_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "update-lb-ip"), None)
                    if update_lb_ip_v_index is not None:
                        del volume_list[update_lb_ip_v_index]
                if self.settings.get("PERSISTENCE_BACKEND") == "ldap":
                    couchbase_password_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "cb-pass"), None)
                    if couchbase_password_v_index is not None:
                        del volume_list[couchbase_password_v_index]
                    couchbase_crt_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "cb-crt"), None)
                    if couchbase_crt_v_index is not None:
                        del volume_list[couchbase_crt_v_index]
                    couchbase_password_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "cb-pass"), None)
                    if couchbase_password_vm_index is not None:
                        del volume_mount_list[couchbase_password_vm_index]
                    couchbase_crt_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "cb-crt"), None)
                    if couchbase_crt_vm_index is not None:
                        del volume_mount_list[couchbase_crt_vm_index]
                parser.dump_it()

        else:
            for k, v in self.adjust_yamls_for_fqdn_status.items():
                parser = Parser(k, v)
                # Check Couchbase entries
                if self.settings.get("PERSISTENCE_BACKEND") == "ldap":
                    volume_mount_list = parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
                    volume_list = parser["spec"]["template"]["spec"]["volumes"]

                    couchbase_password_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "cb-pass"), None)
                    if couchbase_password_v_index is not None:
                        del volume_list[couchbase_password_v_index]
                    couchbase_crt_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "cb-crt"), None)
                    if couchbase_crt_v_index is not None:
                        del volume_list[couchbase_crt_v_index]

                    couchbase_password_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "cb-pass"), None)
                    if couchbase_password_vm_index is not None:
                        del volume_mount_list[couchbase_password_vm_index]
                    couchbase_crt_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "cb-crt"), None)
                    if couchbase_crt_vm_index is not None:
                        del volume_mount_list[couchbase_crt_vm_index]

                if k != self.cr_rotate_yaml and k != self.gluu_upgrade_yaml:
                    parser["spec"]["template"]["spec"]["containers"][0]["command"] = \
                        ['/bin/sh', '-c', '/usr/bin/python3 /scripts/update-lb-ip.py & \n/app/scripts/entrypoint.sh\n']
                    volume_mount_list = parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
                    if {"mountPath": "/scripts", "name": "update-lb-ip"} not in volume_mount_list:
                        parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
                            {"mountPath": "/scripts", "name": "update-lb-ip"})
                    parser["spec"]["template"]["spec"]["hostAliases"][0]["hostnames"] = [self.settings.get("GLUU_FQDN")]
                    parser["spec"]["template"]["spec"]["hostAliases"][0]["ip"] = self.settings.get("HOST_EXT_IP")
                parser.dump_it()

    def setup_config_kustomization(self):
        config_kustmoization_yaml = Path("./config/base/kustomization.yaml")
        parser = Parser(config_kustmoization_yaml, "Kustomization")
        list_of_config_resource_files = parser["resources"]
        if self.settings.get("DEPLOYMENT_ARCH") == "gke":
            if "cluster-role-bindings.yaml" not in list_of_config_resource_files:
                list_of_config_resource_files.append("cluster-role-bindings.yaml")
        else:
            if "cluster-role-bindings.yaml" in list_of_config_resource_files:
                list_of_config_resource_files.remove("cluster-role-bindings.yaml")

        if self.settings.get("USE_ISTIO") == "Y":
            if "service.yaml" not in list_of_config_resource_files:
                list_of_config_resource_files.append("service.yaml")
            jobs_parser = Parser("./config/base/jobs.yaml", "Job")
            jobs_parser["spec"]["template"]["spec"]["containers"][0]["command"] = \
                ["tini", "-g", "--", "/bin/sh", "-c", "\n/app/scripts/entrypoint.sh load\n"
                                                      "curl -X POST http://localhost:15020/quitquitquit"]
            jobs_parser.dump_it()

        parser["resources"] = list_of_config_resource_files
        # if gluu crt and key were provided by user
        custom_gluu_crt = Path("./gluu.crt")
        custom_gluu_key = Path("./gluu.key")
        if custom_gluu_crt.exists() and custom_gluu_key.exists():
            cert = open(custom_gluu_crt).read()
            key = open(custom_gluu_key).read()
            if not check_cert_with_private_key(cert, key):
                logger.error("Custom crt and key were provided but were incorrect")
                raise SystemExit(1)
            shutil.copy(custom_gluu_crt, Path("./config/base"))
            shutil.copy(custom_gluu_key, Path("./config/base"))
            parser.update({"secretGenerator": [{"name": "gluu-cert-key-override", "files": ["gluu.crt", "gluu.key"]}]})
            jobs_parser = Parser("./config/base/jobs.yaml", "Job")
            # Add volume mount
            jobs_parser["spec"]["template"]["spec"]["volumes"].append({"name": "gluu-cert-override", "secret": {
                "secretName": "gluu-cert-key-override", "items": [{"key": "gluu.crt", "path": "gluu_https.crt"}]}})
            jobs_parser["spec"]["template"]["spec"]["volumes"].append({"name": "gluu-key-override", "secret": {
                "secretName": "gluu-cert-key-override", "items": [{"key": "gluu.key", "path": "gluu_https.key"}]}})
            # Add volumeMounts
            jobs_parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
                {"name": "gluu-cert-override", "mountPath": "/etc/certs/gluu_https.crt", "subPath": "gluu_https.crt"})
            jobs_parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
                {"name": "gluu-key-override", "mountPath": "/etc/certs/gluu_https.key", "subPath": "gluu_https.key"})
            jobs_parser.dump_it()
        parser.dump_it()

    def setup_jackrabbit_volumes(self, app_file, type):
        parser = Parser(app_file, type)
        volume_mount_list = parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
        if {"mountPath": "/etc/gluu/conf/jackrabbit_admin_password", "name": "gluu-jackrabbit-admin-pass"} \
                not in volume_mount_list:
            logger.info("Adding jackrabbbit admin pass secret volume and volume mount to {}.".format(app_file))
            parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
                {"mountPath": "/etc/gluu/conf/jackrabbit_admin_password",
                 "name": "gluu-jackrabbit-admin-pass", "subPath": "jackrabbit_admin_password"})
            parser["spec"]["template"]["spec"]["volumes"].append({"name": "gluu-jackrabbit-admin-pass",
                                                                  "secret": {
                                                                      "secretName": "gluu-jackrabbit-admin-pass"}})
        parser.dump_it()

    def adjust_istio_virtual_services_destination_rules(self, app, virtual_service):
        app_internal_addresss = app + "." + self.settings.get("GLUU_NAMESPACE") + "." + "svc.cluster.local"
        destination_rule_name = "gluu-" + app + "-mtls"
        if self.settings.get("USE_ISTIO_INGRESS") == "Y":
            # Adjust virtual services
            virtual_service_path = Path("./gluu-istio/base/gluu-virtual-services.yaml")
            virtual_service_parser = Parser(virtual_service_path, "VirtualService", virtual_service)
            virtual_service_parser["spec"]["hosts"] = [self.settings.get("GLUU_FQDN")]
            http_entries = virtual_service_parser["spec"]["http"]
            for i, http in enumerate(http_entries):
                virtual_service_parser["spec"]["http"][i]["route"][0]["destination"]["host"] = app_internal_addresss
            virtual_service_parser.dump_it()
            # Adjust destination rules
            destination_rule_path = Path("./gluu-istio/base/gluu-destination-rules.yaml")
            destination_rule_parser = Parser(destination_rule_path, "DestinationRule", destination_rule_name)
            destination_rule_parser["spec"]["host"] = app_internal_addresss
            destination_rule_parser.dump_it()

    def parse_configmap(self, app_file):
        if "config" in app_file:
            configmap_parser = Parser(app_file, "ConfigMap", "gluu-config-cm")
        else:
            configmap_parser = Parser(app_file, "ConfigMap")
        if self.settings.get("IS_GLUU_FQDN_REGISTERED") == "Y" or \
                self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube", "gke", "aks", "do"):
            try:
                del configmap_parser["data"]["LB_ADDR"]
            except KeyError:
                logger.info("Key not deleted as it does not exist inside yaml.")

        configmap_parser["data"]["GLUU_CACHE_TYPE"] = self.settings.get("GLUU_CACHE_TYPE")
        configmap_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings.get("GLUU_NAMESPACE")
        configmap_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings.get("GLUU_NAMESPACE")
        configmap_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings.get("HYBRID_LDAP_HELD_DATA")
        configmap_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings.get("PERSISTENCE_BACKEND")
        configmap_parser["data"]["DOMAIN"] = self.settings.get("GLUU_FQDN")
        configmap_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings.get("COUCHBASE_URL")
        configmap_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings.get("COUCHBASE_USER")
        configmap_parser["data"]["GLUU_COUCHBASE_SUPERUSER"] = self.settings.get("COUCHBASE_SUPERUSER")
        configmap_parser["data"]["GLUU_JACKRABBIT_URL"] = self.settings.get("JACKRABBIT_URL")
        # Persistence keys
        if self.settings.get("GLUU_CACHE_TYPE") == "REDIS":
            configmap_parser["data"]["GLUU_REDIS_URL"] = self.settings.get("REDIS_URL")
            configmap_parser["data"]["GLUU_REDIS_TYPE"] = self.settings.get("REDIS_TYPE")
            configmap_parser["data"]["GLUU_REDIS_USE_SSL"] = self.settings.get("REDIS_USE_SSL")
            configmap_parser["data"]["GLUU_REDIS_SSL_TRUSTSTORE"] = self.settings.get("REDIS_SSL_TRUSTSTORE")
            configmap_parser["data"]["GLUU_REDIS_SENTINEL_GROUP"] = self.settings.get("REDIS_SENTINEL_GROUP")
        configmap_parser["data"]["GLUU_CASA_ENABLED"] = self.settings.get("ENABLE_CASA_BOOLEAN")
        configmap_parser["data"]["GLUU_OXTRUST_API_ENABLED"] = self.settings.get("ENABLE_OXTRUST_API_BOOLEAN")
        configmap_parser["data"]["GLUU_OXTRUST_API_TEST_MODE"] = self.settings.get("ENABLE_OXTRUST_TEST_MODE_BOOLEAN")
        configmap_parser["data"]["GLUU_PASSPORT_ENABLED"] = self.settings.get("ENABLE_OXPASSPORT_BOOLEAN")
        configmap_parser["data"]["GLUU_RADIUS_ENABLED"] = self.settings.get("ENABLE_RADIUS_BOOLEAN")
        configmap_parser["data"]["GLUU_SAML_ENABLED"] = self.settings.get("ENABLE_SAML_BOOLEAN")
        configmap_parser["data"]["GLUU_JACKRABBIT_ADMIN_ID"] = self.settings.get("JACKRABBIT_ADMIN_ID")
        if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
            configmap_parser["data"]["GLUU_JACKRABBIT_CLUSTER"] = "true"
            configmap_parser["data"]["GLUU_JACKRABBIT_POSTGRES_USER"] = self.settings.get("JACKRABBIT_PG_USER")
            configmap_parser["data"]["GLUU_JACKRABBIT_POSTGRES_PASSWORD_FILE"] = "/etc/gluu/conf/postgres_password"
            configmap_parser["data"]["GLUU_JACKRABBIT_POSTGRES_HOST"] = self.settings.get("POSTGRES_URL")
            configmap_parser["data"]["GLUU_JACKRABBIT_POSTGRES_PORT"] = "5432"
            configmap_parser["data"]["GLUU_JACKRABBIT_POSTGRES_DATABASE"] = self.settings.get("JACKRABBIT_DATABASE")

        # oxAuth
        if self.settings.get("ENABLE_CASA_BOOLEAN") == "true":
            configmap_parser["data"]["GLUU_SYNC_CASA_MANIFESTS"] = "true"
        # oxTrust
        if self.settings.get("ENABLE_OXSHIBBOLETH") == "Y":
            configmap_parser["data"]["GLUU_SYNC_SHIB_MANIFESTS"] = "true"
        # oxdserver
        if self.settings.get("ENABLE_OXD") == "Y":
            configmap_parser["data"]["GLUU_OXD_APPLICATION_CERT_CN"] = self.settings.get("OXD_APPLICATION_KEYSTORE_CN")
            configmap_parser["data"]["GLUU_OXD_ADMIN_CERT_CN"] = self.settings.get("OXD_ADMIN_KEYSTORE_CN")
        # casa
        configmap_parser["data"]["GLUU_OXD_SERVER_URL"] = self.settings.get("OXD_APPLICATION_KEYSTORE_CN") + ":8443"
        configmap_parser.dump_it()

    def kustomize_it(self):
        logger.info("Building manifests...")
        self.setup_config_kustomization()
        for app in self.all_apps:
            app_filename = app + ".yaml"
            kustomization_file = "./{}/base/kustomization.yaml".format(app)
            app_file = str(self.output_yaml_directory.joinpath(app_filename).resolve())
            command = self.kubectl + " kustomize ./{}/base".format(app)
            if app == "config":
                self.build_manifest(app, kustomization_file, command,
                                    "CONFIG_IMAGE_NAME", "CONFIG_IMAGE_TAG", app_file)
                self.parse_configmap(app_file)

            if app == "ldap":
                if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
                    command = self.kubectl + " kustomize " + str(
                        self.ldap_kustomize_yaml_directory.resolve())
                    self.build_manifest(app, kustomization_file, command,
                                        "LDAP_IMAGE_NAME", "LDAP_IMAGE_TAG", app_file)
                    self.adjust_ldap_jackrabbit(app_file)
                    self.remove_resources(app_file, "StatefulSet")

            if app == "jackrabbit" and self.settings.get("INSTALL_JACKRABBIT") == "Y":
                command = self.kubectl + " kustomize " + str(
                    self.jcr_kustomize_yaml_directory.resolve())
                self.build_manifest(app, kustomization_file, command,
                                    "JACKRABBIT_IMAGE_NAME", "JACKRABBIT_IMAGE_TAG", app_file)
                self.adjust_ldap_jackrabbit(app_file)
                self.remove_resources(app_file, "StatefulSet")
                self.setup_jackrabbit_volumes(app_file, "StatefulSet")

            if app == "persistence":
                parser = Parser(kustomization_file, "Kustomization")
                list_of_config_resource_files = parser["resources"]
                if self.settings.get("USE_ISTIO") == "Y":
                    if "service.yaml" not in list_of_config_resource_files:
                        list_of_config_resource_files.append("service.yaml")
                    jobs_parser = Parser("./persistence/base/jobs.yaml", "Job")
                    jobs_parser["spec"]["template"]["spec"]["containers"][0]["command"] = \
                        ["tini", "-g", "--", "/bin/sh", "-c", "\n/app/scripts/entrypoint.sh\n"
                                                              "curl -X POST http://localhost:15020/quitquitquit"]
                    jobs_parser.dump_it()
                parser.dump_it()

                self.build_manifest(app, kustomization_file, command,
                                    "PERSISTENCE_IMAGE_NAME", "PERSISTENCE_IMAGE_TAG", app_file)
                if self.settings.get("PERSISTENCE_BACKEND") == "ldap":
                    persistence_job_parser = Parser(app_file, "Job")
                    del persistence_job_parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
                    del persistence_job_parser["spec"]["template"]["spec"]["volumes"]
                    persistence_job_parser.dump_it()

            if app == "oxauth":
                self.adjust_istio_virtual_services_destination_rules(app, "gluu-istio-oxauth")
                self.build_manifest(app, kustomization_file, command,
                                    "OXAUTH_IMAGE_NAME", "OXAUTH_IMAGE_TAG", app_file)
                self.remove_resources(app_file, "Deployment")
                self.setup_jackrabbit_volumes(app_file, "Deployment")
                self.adjust_yamls_for_fqdn_status[app_file] = "Deployment"

            if app == "fido2" and self.settings.get("ENABLE_FIDO2") == "Y":
                self.adjust_istio_virtual_services_destination_rules(app, "gluu-istio-fido2-configuration")
                self.build_manifest(app, kustomization_file, command,
                                    "FIDO2_IMAGE_NAME", "FIDO2_IMAGE_TAG", app_file)
                self.remove_resources(app_file, "Deployment")
                self.adjust_yamls_for_fqdn_status[app_file] = "Deployment"

            if app == "scim" and self.settings.get("ENABLE_SCIM") == "Y":
                self.adjust_istio_virtual_services_destination_rules(app, "gluu-istio-scim-config")
                self.build_manifest(app, kustomization_file, command,
                                    "SCIM_IMAGE_NAME", "SCIM_IMAGE_TAG", app_file)
                self.remove_resources(app_file, "Deployment")
                self.adjust_yamls_for_fqdn_status[app_file] = "Deployment"

            if app == "oxtrust":
                self.adjust_istio_virtual_services_destination_rules(app, "gluu-istio-base")
                self.build_manifest(app, kustomization_file, command,
                                    "OXTRUST_IMAGE_NAME", "OXTRUST_IMAGE_TAG", app_file)
                self.remove_resources(app_file, "StatefulSet")
                self.setup_jackrabbit_volumes(app_file, "StatefulSet")
                self.adjust_yamls_for_fqdn_status[app_file] = "StatefulSet"

            if app == "oxshibboleth" and self.settings.get("ENABLE_OXSHIBBOLETH") == "Y":
                self.adjust_istio_virtual_services_destination_rules(app, "gluu-istio-oxshibbioleth")
                self.build_manifest(app, kustomization_file, command,
                                    "OXSHIBBOLETH_IMAGE_NAME", "OXSHIBBOLETH_IMAGE_TAG", app_file)
                self.remove_resources(app_file, "StatefulSet")
                self.setup_jackrabbit_volumes(app_file, "StatefulSet")
                self.adjust_yamls_for_fqdn_status[app_file] = "StatefulSet"

            if app == "oxpassport" and self.settings.get("ENABLE_OXPASSPORT") == "Y":
                self.adjust_istio_virtual_services_destination_rules(app, "gluu-istio-passport")
                self.build_manifest(app, kustomization_file, command,
                                    "OXPASSPORT_IMAGE_NAME", "OXPASSPORT_IMAGE_TAG", app_file)
                self.remove_resources(app_file, "Deployment")
                self.adjust_yamls_for_fqdn_status[app_file] = "Deployment"

            if app == "oxauth-key-rotation" and self.settings.get("ENABLE_OXAUTH_KEY_ROTATE") == "Y":
                parser = Parser(kustomization_file, "Kustomization")
                list_of_config_resource_files = parser["resources"]
                cron_job_parser = Parser("./oxauth-key-rotation/base/cronjobs.yaml", "CronJob")
                cron_job_parser["spec"]["schedule"] = "0 */{} * * *".format(self.settings.get("OXAUTH_KEYS_LIFE"))
                cron_job_parser["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]["args"] = \
                    ["patch", "oxauth", "--opts", "interval:{}".format(self.settings.get("OXAUTH_KEYS_LIFE"))]
                if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
                    cron_job_parser["spec"]["jobTemplate"]["spec"]["template"]["spec"]["volumes"] = \
                        [{"name": "cb-pass", "secret": {"secretName": "cb-pass"}},
                         {"name": "cb-crt", "secret": {"secretName": "cb-crt"}}]
                    cron_job_parser["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]\
                        = [{"name": "cb-pass", "mountPath":
                            "/etc/gluu/conf/couchbase_password",
                            "subPath": "couchbase_password"},
                           {"name": "cb-crt", "mountPath":
                            "/etc/certs/couchbase.crt",
                            "subPath": "couchbase.crt"}]
                if self.settings.get("USE_ISTIO") == "Y":
                    if "service.yaml" not in list_of_config_resource_files:
                        list_of_config_resource_files.append("service.yaml")
                    cron_job_parser["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]["command"] = \
                        ["tini", "-g", "--", "/bin/sh", "-c", "\n/app/scripts/entrypoint.sh patch oxauth --opts "
                                                              "interval:{}\ncurl -X POST "
                                                              "http://localhost:15020/quitquitquit"
                            .format(self.settings.get("OXAUTH_KEYS_LIFE"))]
                    try:
                        del cron_job_parser["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]["args"]
                    except KeyError:
                        logger.warning("Key arg not found")
                cron_job_parser.dump_it()
                parser.dump_it()
                self.build_manifest(app, kustomization_file, command,
                                    "CERT_MANAGER_IMAGE_NAME", "CERT_MANAGER_IMAGE_TAG", app_file)
                self.remove_resources(app_file, "CronJob")

            if app == "cr-rotate" and self.settings.get("ENABLE_CACHE_REFRESH") == "Y":
                logger.info("Building {} manifests".format(app))
                self.update_kustomization_yaml(kustomization_yaml=kustomization_file,
                                               namespace=self.settings.get("GLUU_NAMESPACE"),
                                               image_name_key="CACHE_REFRESH_ROTATE_IMAGE_NAME",
                                               image_tag_key="CACHE_REFRESH_ROTATE_IMAGE_TAG")
                exec_cmd(command, output_file=app_file)
                self.remove_resources(app_file, "DaemonSet")
                self.adjust_yamls_for_fqdn_status[app_file] = "DaemonSet"

            if app == "oxd-server" and self.settings.get("ENABLE_OXD") == "Y":
                logger.info("Building {} manifests".format(app))
                self.update_kustomization_yaml(kustomization_yaml=kustomization_file,
                                               namespace=self.settings.get("GLUU_NAMESPACE"),
                                               image_name_key="OXD_IMAGE_NAME",
                                               image_tag_key="OXD_IMAGE_TAG")
                exec_cmd(command, output_file=app_file)
                self.remove_resources(app_file, "Deployment")
                oxd_server_service_parser = Parser(app_file, "Service")
                oxd_server_service_parser["metadata"]["name"] = self.settings.get("OXD_APPLICATION_KEYSTORE_CN")
                oxd_server_service_parser.dump_it()
                self.adjust_yamls_for_fqdn_status[app_file] = "Deployment"

            if app == "casa" and self.settings.get("ENABLE_CASA") == "Y":
                self.adjust_istio_virtual_services_destination_rules(app, "gluu-istio-casa")
                logger.info("Building {} manifests".format(app))
                self.update_kustomization_yaml(kustomization_yaml=kustomization_file,
                                               namespace=self.settings.get("GLUU_NAMESPACE"),
                                               image_name_key="CASA_IMAGE_NAME",
                                               image_tag_key="CASA_IMAGE_TAG")
                exec_cmd(command, output_file=app_file)
                self.remove_resources(app_file, "Deployment")
                self.setup_jackrabbit_volumes(app_file, "Deployment")
                self.adjust_yamls_for_fqdn_status[app_file] = "Deployment"

            if app == "radius" and self.settings.get("ENABLE_RADIUS") == "Y":
                logger.info("Building {} manifests".format(app))
                self.update_kustomization_yaml(kustomization_yaml=kustomization_file,
                                               namespace=self.settings.get("GLUU_NAMESPACE"),
                                               image_name_key="RADIUS_IMAGE_NAME",
                                               image_tag_key="RADIUS_IMAGE_TAG")
                exec_cmd(command, output_file=app_file)
                self.remove_resources(app_file, "Deployment")
                self.adjust_yamls_for_fqdn_status[app_file] = "Deployment"

            if app == "update-lb-ip" and self.settings.get("IS_GLUU_FQDN_REGISTERED") == "N":
                if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "local"):
                    logger.info("Building {} manifests".format(app))
                    parser = Parser(kustomization_file, "Kustomization")
                    parser["namespace"] = self.settings.get("GLUU_NAMESPACE")
                    parser.dump_it()
                    exec_cmd(command, output_file=app_file)

            if self.settings.get("USE_ISTIO_INGRESS") == "Y" and app == "gluu-istio-ingress":
                command = self.kubectl + " kustomize ./gluu-istio/base"
                exec_cmd(command, output_file=app_file)

    def build_manifest(self, app, kustomization_file, command, image_name_key, image_tag_key, app_file):
        logger.info("Building {} manifests".format(app))
        self.update_kustomization_yaml(kustomization_yaml=kustomization_file,
                                       namespace=self.settings.get("GLUU_NAMESPACE"),
                                       image_name_key=image_name_key,
                                       image_tag_key=image_tag_key)
        exec_cmd(command, output_file=app_file)

    def kustomize_gluu_upgrade(self):
        self.update_kustomization_yaml(kustomization_yaml="upgrade/base/kustomization.yaml",
                                       namespace=self.settings.get("GLUU_NAMESPACE"),
                                       image_name_key="UPGRADE_IMAGE_NAME",
                                       image_tag_key="UPGRADE_IMAGE_TAG")
        command = self.kubectl + " kustomize upgrade/base"
        exec_cmd(command, output_file=self.gluu_upgrade_yaml)
        upgrade_cm_parser = Parser(self.gluu_upgrade_yaml, "ConfigMap")
        upgrade_cm_parser["data"]["DOMAIN"] = self.settings.get("GLUU_FQDN")
        upgrade_cm_parser["data"]["GLUU_CACHE_TYPE"] = self.settings.get("GLUU_CACHE_TYPE")
        upgrade_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings.get("COUCHBASE_URL")
        upgrade_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings.get("COUCHBASE_USER")
        upgrade_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings.get("HYBRID_LDAP_HELD_DATA")
        upgrade_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings.get("PERSISTENCE_BACKEND")
        upgrade_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings.get("GLUU_NAMESPACE")
        upgrade_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings.get("GLUU_NAMESPACE")
        upgrade_cm_parser.dump_it()

        upgrade_job_parser = Parser(self.gluu_upgrade_yaml, "Job")
        upgrade_job_parser["spec"]["template"]["spec"]["containers"][0]["args"] = \
            ["--source", self.settings.get("GLUU_VERSION"),
             "--target", self.settings.get("GLUU_UPGRADE_TARGET_VERSION")]
        upgrade_job_parser.dump_it()

        self.adjust_yamls_for_fqdn_status[self.gluu_upgrade_yaml] = "Job"

    def kustomize_gluu_gateway_ui(self):
        if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            command = self.kubectl + " kustomize gluu-gateway-ui/base"
            kustomization_file = "./gluu-gateway-ui/base/kustomization.yaml"
            self.update_kustomization_yaml(kustomization_yaml=kustomization_file,
                                           namespace=self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"),
                                           image_name_key="GLUU_GATEWAY_UI_IMAGE_NAME",
                                           image_tag_key="GLUU_GATEWAY_UI_IMAGE_TAG")
            exec_cmd(command, output_file=self.gg_ui_yaml)
            self.parse_gluu_gateway_ui_configmap()
            postgres_full_add = "'postgresql://" + self.settings.get("GLUU_GATEWAY_UI_PG_USER") + ":" + \
                                self.settings.get("GLUU_GATEWAY_UI_PG_PASSWORD") + "@" + \
                                self.settings.get("POSTGRES_URL") + \
                                ":5432/" + self.settings.get("GLUU_GATEWAY_UI_DATABASE") + "'"
            gg_ui_job_parser = Parser(self.gg_ui_yaml, "Job")
            gg_ui_job_parser["spec"]["template"]["spec"]["containers"][0]["command"] = \
                ["/bin/sh", "-c", "./entrypoint.sh -c prepare -a postgres -u " + postgres_full_add]
            gg_ui_job_parser.dump_it()

            gg_ui_ingress_parser = Parser(self.gg_ui_yaml, "Ingress")
            gg_ui_ingress_parser["spec"]["tls"][0]["hosts"][0] = self.settings.get("GLUU_FQDN")
            gg_ui_ingress_parser["spec"]["rules"][0]["host"] = self.settings.get("GLUU_FQDN")
            gg_ui_ingress_parser.dump_it()
            self.remove_resources(self.gg_ui_yaml, "Deployment")
            self.adjust_yamls_for_fqdn_status[self.gg_ui_yaml] = "Deployment"

    def prepare_alb(self):
        services = [self.oxauth_yaml, self.oxtrust_yaml, self.casa_yaml,
                    self.oxpassport_yaml, self.oxshibboleth_yaml, self.fido2_yaml, self.scim_yaml]
        for service in services:
            if Path(service).is_file():
                service_parser = Parser(service, "Service")
                service_parser["spec"].update({"type": "NodePort"})
                service_parser["spec"]["ports"][0].update({"protocol": "TCP"})
                service_parser["spec"]["ports"][0].update({"targetPort": 8080})
                if service == self.oxpassport_yaml:
                    service_parser["spec"]["ports"][0]["targetPort"] = 8090
                service_parser.dump_it()
        ingress_parser = Parser("./alb/ingress.yaml", "Ingress")
        ingress_parser["spec"]["rules"][0]["host"] = self.settings.get("GLUU_FQDN")
        ingress_parser["metadata"]["annotations"]["alb.ingress.kubernetes.io/certificate-arn"] = \
            self.settings.get("ARN_AWS_IAM")
        if not self.settings.get("ARN_AWS_IAM"):
            del ingress_parser["metadata"]["annotations"]["alb.ingress.kubernetes.io/certificate-arn"]

        for path in ingress_parser["spec"]["rules"][0]["http"]["paths"]:
            service_name = path["backend"]["serviceName"]
            if self.settings.get("ENABLE_CASA") != "Y" and service_name == "casa":
                path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
                del ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index]

            if self.settings.get("ENABLE_OXSHIBBOLETH") != "Y" and service_name == "oxshibboleth":
                path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
                del ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index]

            if self.settings.get("ENABLE_OXPASSPORT") != "Y" and service_name == "oxpassport":
                path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
                del ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index]

            if self.settings.get("INSTALL_GLUU_GATEWAY") != "Y" and service_name == "gg-kong-ui":
                path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
                del ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index]
        ingress_parser.dump_it()

    def update_kustomization_yaml(self, kustomization_yaml, namespace, image_name_key, image_tag_key):
        parser = Parser(kustomization_yaml, "Kustomization")
        parser["namespace"] = namespace
        parser["images"][0]["name"] = self.settings.get(image_name_key)
        parser["images"][0]["newTag"] = self.settings.get(image_tag_key)
        parser.dump_it()

    def setup_tls(self, namespace):
        starting_time = time.time()
        while True:
            try:
                ssl_cert = self.kubernetes.read_namespaced_secret("gluu",
                                                                  self.settings.get("GLUU_NAMESPACE")).data["ssl_cert"]
                ssl_key = self.kubernetes.read_namespaced_secret("gluu",
                                                                 self.settings.get("GLUU_NAMESPACE")).data["ssl_key"]
                break
            except (KeyError, Exception):
                logger.info("Waiting for Gluu secret...")
                time.sleep(10)
                end_time = time.time()
                running_time = end_time - starting_time
                if running_time > 600:
                    logger.error("Could not read Gluu secret. Please check config job pod logs.")
                    if namespace != self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"):
                        raise SystemExit(1)

        self.kubernetes.patch_or_create_namespaced_secret(name="tls-certificate",
                                                          namespace=namespace,
                                                          literal="tls.crt",
                                                          value_of_literal=ssl_cert,
                                                          secret_type="kubernetes.io/tls",
                                                          second_literal="tls.key",
                                                          value_of_second_literal=ssl_key)

    def deploy_alb(self):
        shutil.copy(Path("./alb/ingress.yaml"), self.output_yaml_directory.joinpath("ingress.yaml"))
        self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("ingress.yaml"),
                                                 self.settings.get("GLUU_NAMESPACE"))
        if self.settings.get("IS_GLUU_FQDN_REGISTERED") != "Y":
            prompt = input("Please input the DNS of the Application load balancer  created found on AWS UI: ")
            lb_hostname = prompt
            while True:
                try:
                    if lb_hostname:
                        break
                    lb_hostname = self.kubernetes.read_namespaced_ingress(
                        name="gluu", namespace="gluu").status.load_balancer.ingress[0].hostname
                except TypeError:
                    logger.info("Waiting for loadbalancer address..")
                    time.sleep(10)
            self.settings.set("LB_ADD", lb_hostname)

    def parse_gluu_gateway_ui_configmap(self):
        oxd_server_url = "https://{}.{}.svc.cluster.local:8443".format(
            self.settings.get("OXD_APPLICATION_KEYSTORE_CN"), self.settings.get("GLUU_NAMESPACE"))
        gg_ui_cm_parser = Parser(self.gg_ui_yaml, "ConfigMap")
        gg_ui_cm_parser["data"]["DB_USER"] = self.settings.get("GLUU_GATEWAY_UI_PG_USER")
        gg_ui_cm_parser["data"]["KONG_ADMIN_URL"] = "https://kong-admin.{}.svc.cluster.local:8444".format(
            self.settings.get("KONG_NAMESPACE"))
        gg_ui_cm_parser["data"]["DB_HOST"] = self.settings.get("POSTGRES_URL")
        gg_ui_cm_parser["data"]["DB_DATABASE"] = self.settings.get("GLUU_GATEWAY_UI_DATABASE")
        gg_ui_cm_parser["data"]["OXD_SERVER_URL"] = oxd_server_url
        # Register new client if one was not provided
        if not gg_ui_cm_parser["data"]["CLIENT_ID"] or \
                not gg_ui_cm_parser["data"]["OXD_ID"] or \
                not gg_ui_cm_parser["data"]["CLIENT_SECRET"]:
            oxd_id, client_id, client_secret = register_op_client(self.settings.get("GLUU_NAMESPACE"),
                                                                  "konga-client",
                                                                  self.settings.get("GLUU_FQDN"),
                                                                  oxd_server_url)
            gg_ui_cm_parser["data"]["OXD_ID"] = oxd_id
            gg_ui_cm_parser["data"]["CLIENT_ID"] = client_id
            gg_ui_cm_parser["data"]["CLIENT_SECRET"] = client_secret
        gg_ui_cm_parser["data"]["OP_SERVER_URL"] = "https://" + self.settings.get("GLUU_FQDN")

        gg_ui_cm_parser["data"]["GG_HOST"] = self.settings.get("GLUU_FQDN") + "/gg-ui/"
        gg_ui_cm_parser["data"]["GG_UI_REDIRECT_URL_HOST"] = self.settings.get("GLUU_FQDN") + "/gg-ui/"

        gg_ui_cm_parser.dump_it()

    def adjust_ldap_jackrabbit(self, app_file):
        statefulset_parser = Parser(app_file, "StatefulSet")
        statefulset_parser["spec"]["volumeClaimTemplates"][0]["spec"]["resources"]["requests"]["storage"] \
            = self.settings.get("JACKRABBIT_STORAGE_SIZE")
        if "ldap" in app_file:
            statefulset_parser["spec"]["volumeClaimTemplates"][0]["spec"]["resources"]["requests"]["storage"] \
                = self.settings.get("LDAP_STORAGE_SIZE")
        statefulset_parser.dump_it()
        if self.settings.get("APP_VOLUME_TYPE") not in (7, 12, 17, 22, 26):
            pv_parser = Parser(app_file, "PersistentVolume")
            pv_parser["spec"]["capacity"]["storage"] = self.settings.get("JACKRABBIT_STORAGE_SIZE")
            if "ldap" in app_file:
                pv_parser["spec"]["capacity"]["storage"] = self.settings.get("LDAP_STORAGE_SIZE")
            if self.settings.get("APP_VOLUME_TYPE") == 11:
                pv_parser["spec"]["hostPath"]["path"] = self.settings.get("GOOGLE_NODE_HOME_DIR") + "/opendj"
                if "ldap" in app_file:
                    pv_parser["spec"]["hostPath"]["path"] = self.settings.get("GOOGLE_NODE_HOME_DIR") + "/jackrabbit"

            pv_parser.dump_it()

    def remove_resources(self, app_file, kind):
        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube") \
                or self.settings.get("TEST_ENVIRONMENT") == "Y":
            parser = Parser(app_file, kind)
            try:
                logger.info("Removing resources limits and requests from {}".format(app_file))
                del parser["spec"]["template"]["spec"]["containers"][0]["resources"]
            except KeyError:
                logger.info("Key not deleted as it does not exist inside yaml.")
            parser.dump_it()

    def set_lb_address(self):
        """
        Sets LB address in configMap
        :return:
        """
        if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "local"):
            cm_parser = Parser(self.config_yaml, "ConfigMap", "gluu-config-cm")
            cm_parser["data"]["LB_ADDR"] = self.settings.get("LB_ADD")
            cm_parser.dump_it()

    def wait_for_nginx_add(self):
        hostname_ip = None
        while True:
            try:
                if hostname_ip:
                    break
                if self.settings.get("DEPLOYMENT_ARCH") == "eks":
                    hostname_ip = self.kubernetes.read_namespaced_service(
                        name="ingress-nginx", namespace="ingress-nginx").status.load_balancer.ingress[0].hostname
                    self.settings.set("LB_ADD", hostname_ip)
                    if self.settings.get("AWS_LB_TYPE") == "nlb":
                        ip_static = socket.gethostbyname(str(hostname_ip))
                        if ip_static:
                            break
                elif self.settings.get("DEPLOYMENT_ARCH") == "local":
                    self.settings.set("LB_ADD", "ingress-nginx.ingress-nginx.svc.cluster.local")
                    break
                else:
                    hostname_ip = self.kubernetes.read_namespaced_service(
                        name="ingress-nginx", namespace="ingress-nginx").status.load_balancer.ingress[0].ip
                    self.settings.set("HOST_EXT_IP", hostname_ip)
            except (TypeError, AttributeError):
                logger.info("Waiting for address..")
                time.sleep(10)

    def deploy_nginx(self):
        copy(Path("./nginx"), self.output_yaml_directory.joinpath("nginx"))
        self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("nginx/mandatory.yaml"))
        if self.settings.get("DEPLOYMENT_ARCH") == "eks":
            if self.settings.get("AWS_LB_TYPE") == "nlb":
                if self.settings.get("USE_ARN") == "Y":
                    svc_nlb_yaml = self.output_yaml_directory.joinpath("nginx/nlb-service.yaml")
                    svc_nlb_yaml_parser = Parser(svc_nlb_yaml, "Service")
                    svc_nlb_yaml_parser["metadata"]["annotations"].update(
                        {"service.beta.kubernetes.io/aws-load-balancer-ssl-cert": self.settings.get("ARN_AWS_IAM")})
                    svc_nlb_yaml_parser["metadata"]["annotations"].update(
                        {"service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled": '"true"'})
                    svc_nlb_yaml_parser["metadata"]["annotations"].update({
                        "service.beta.kubernetes.io/aws-load-balancer-ssl-negotiation-policy":
                            "ELBSecurityPolicy-TLS-1-1-2017-01"})
                    svc_nlb_yaml_parser["metadata"]["annotations"].update(
                        {"service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "http"})
                    svc_nlb_yaml_parser["metadata"]["annotations"].update(
                        {"service.beta.kubernetes.io/aws-load-balancer-ssl-ports": "https"})
                    svc_nlb_yaml_parser.dump_it()
                self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("nginx/nlb-service.yaml"))
            else:
                if self.settings.get("USE_ARN") == "Y":
                    svc_l7_yaml = self.output_yaml_directory.joinpath("nginx/service-l7.yaml")
                    svc_l7_yaml_parser = Parser(svc_l7_yaml, "Service")
                    svc_l7_yaml_parser["metadata"]["annotations"][
                        "service.beta.kubernetes.io/aws-load-balancer-ssl-cert"] = self.settings.get("ARN_AWS_IAM")
                    svc_l7_yaml_parser.dump_it()
                    self.kubernetes.create_objects_from_dict(svc_l7_yaml)
                    self.kubernetes.delete_config_map_using_name("nginx-configuration", "ingress-nginx")
                    time.sleep(5)
                    self.kubernetes.create_objects_from_dict(self.output_yaml_directory.
                                                             joinpath("nginx/patch-configmap-l7.yaml"))
                else:
                    self.kubernetes.delete_config_map_using_name("nginx-configuration", "ingress-nginx")
                    time.sleep(5)
                    self.kubernetes.create_objects_from_dict(self.output_yaml_directory.
                                                             joinpath("nginx/service-l4.yaml"))
                    self.kubernetes.create_objects_from_dict(self.output_yaml_directory.
                                                             joinpath("nginx/patch-configmap-l4.yaml"))

            self.wait_for_nginx_add()

        if self.settings.get("DEPLOYMENT_ARCH") in ("gke", "aks", "do", "local"):
            self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("nginx/cloud-generic.yaml"))
            self.wait_for_nginx_add()
        if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "local"):
            self.wait_for_nginx_add()
            self.set_lb_address()
        ingress_name_list = ["gluu-ingress-base", "gluu-ingress-openid-configuration",
                             "gluu-ingress-uma2-configuration", "gluu-ingress-webfinger",
                             "gluu-ingress-simple-web-discovery", "gluu-ingress-scim-configuration",
                             "gluu-ingress-fido-u2f-configuration", "gluu-ingress", "gluu-ingress-stateful",
                             "gluu-casa", "gluu-ingress-fido2-configuration"]

        ingress_file = self.output_yaml_directory.joinpath("nginx/nginx.yaml")
        for ingress_name in ingress_name_list:
            parser = Parser(ingress_file, "Ingress", ingress_name)
            parser["spec"]["tls"][0]["hosts"][0] = self.settings.get("GLUU_FQDN")
            parser["spec"]["rules"][0]["host"] = self.settings.get("GLUU_FQDN")
            parser.dump_it()

        self.kubernetes.create_objects_from_dict(ingress_file, self.settings.get("GLUU_NAMESPACE"))

    @property
    def generate_postgres_init_sql(self):
        services_using_postgres = []
        if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
            services_using_postgres.append("JACKRABBIT")
        if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            services_using_postgres.append("KONG")
            services_using_postgres.append("GLUU_GATEWAY_UI")
        # Generate init sql
        postgres_init_sql = ""
        for service in services_using_postgres:
            pg_user = self.settings.get("{}_PG_USER".format(service))
            pg_password = self.settings.get("{}_PG_PASSWORD".format(service))
            pg_database = self.settings.get("{}_DATABASE".format(service))
            postgres_init_sql_jackrabbit = "CREATE USER {};\nALTER USER {} PASSWORD '{}';\nCREATE DATABASE {};\n" \
                                           "GRANT ALL PRIVILEGES ON DATABASE {} TO {};\n" \
                .format(pg_user, pg_user, pg_password, pg_database, pg_database, pg_user)
            postgres_init_sql = postgres_init_sql + postgres_init_sql_jackrabbit
        return postgres_init_sql

    def create_patch_secret_init_sql(self):
        postgres_init_sql = self.generate_postgres_init_sql
        encoded_postgers_init_bytes = base64.b64encode(postgres_init_sql.encode("utf-8"))
        encoded_postgers_init_string = str(encoded_postgers_init_bytes, "utf-8")
        self.kubernetes.patch_or_create_namespaced_secret(name="pg-init-sql",
                                                          namespace=self.settings.get("POSTGRES_NAMESPACE"),
                                                          literal="data.sql",
                                                          value_of_literal=encoded_postgers_init_string)

    def deploy_postgres(self):
        self.uninstall_postgres()
        self.kubernetes.create_namespace(name=self.settings.get("POSTGRES_NAMESPACE"), labels={"app": "postgres"})
        self.create_patch_secret_init_sql()
        postgres_storage_class = Path("./postgres/storageclasses.yaml")
        self.analyze_storage_class(postgres_storage_class)
        self.kubernetes.create_objects_from_dict(postgres_storage_class)

        postgres_yaml = Path("./postgres/postgres.yaml")
        postgres_parser = Parser(postgres_yaml, "Postgres")
        postgres_parser["spec"]["replicas"] = self.settings.get("POSTGRES_REPLICAS")
        postgres_parser["spec"]["monitor"]["prometheus"]["namespace"] = self.settings.get("POSTGRES_NAMESPACE")
        postgres_parser["metadata"]["namespace"] = self.settings.get("POSTGRES_NAMESPACE")
        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube") or \
                self.settings.get("TEST_ENVIRONMENT") == "Y":
            try:
                del postgres_parser["spec"]["podTemplate"]["spec"]["resources"]
            except KeyError:
                logger.info("Resources not deleted as they are not found inside yaml.")

        postgres_parser.dump_it()
        self.kubernetes.create_namespaced_custom_object(filepath=postgres_yaml,
                                                        group="kubedb.com",
                                                        version="v1alpha1",
                                                        plural="postgreses",
                                                        namespace=self.settings.get("POSTGRES_NAMESPACE"))
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("POSTGRES_NAMESPACE"), "app=postgres", self.timeout)

    def deploy_kong_init(self):
        self.kubernetes.create_namespace(name=self.settings.get("KONG_NAMESPACE"), labels={"app": "ingress-kong"})
        encoded_kong_pass_bytes = base64.b64encode(self.settings.get("KONG_PG_PASSWORD").encode("utf-8"))
        encoded_kong_pass_string = str(encoded_kong_pass_bytes, "utf-8")
        self.kubernetes.patch_or_create_namespaced_secret(name="kong-postgres-pass",
                                                          namespace=self.settings.get("KONG_NAMESPACE"),
                                                          literal="KONG_PG_PASSWORD",
                                                          value_of_literal=encoded_kong_pass_string)
        kong_init_job = Path("./gluu-gateway-ui/kong-init-job.yaml")
        kong_init_job_parser = Parser(kong_init_job, "Job")
        kong_init_job_parser["spec"]["template"]["spec"]["containers"][0]["env"] = [
            {"name": "KONG_DATABASE", "value": "postgres"},
            {"name": "KONG_PG_HOST", "value": self.settings.get("POSTGRES_URL")},
            {"name": "KONG_PG_USER", "value": self.settings.get("KONG_PG_USER")},
            {"name": "KONG_PG_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "kong-postgres-pass",
                                                                        "key": "KONG_PG_PASSWORD"}}}
        ]
        kong_init_job_parser["metadata"]["namespace"] = self.settings.get("KONG_NAMESPACE")
        kong_init_job_parser["spec"]["template"]["spec"]["containers"][0]["image"] = \
            self.settings.get("GLUU_GATEWAY_IMAGE_NAME") + ":" + self.settings.get("GLUU_GATEWAY_IMAGE_TAG")
        kong_init_job_parser.dump_it()
        self.kubernetes.create_objects_from_dict(kong_init_job)

    def deploy_kong(self):
        self.uninstall_kong()
        self.deploy_kong_init()
        kong_all_in_one_db = Path("./gluu-gateway-ui/kong-all-in-one-db.yaml")

        kong_all_in_one_db_parser_sa = Parser(kong_all_in_one_db, "ServiceAccount")
        kong_all_in_one_db_parser_sa["metadata"]["namespace"] = self.settings.get("KONG_NAMESPACE")
        kong_all_in_one_db_parser_sa.dump_it()

        kong_all_in_one_db_parser_crb = Parser(kong_all_in_one_db, "ClusterRoleBinding")
        kong_all_in_one_db_parser_crb["subjects"][0]["namespace"] = self.settings.get("KONG_NAMESPACE")
        kong_all_in_one_db_parser_crb.dump_it()

        kong_all_in_one_db_parser_svc_proxy = Parser(kong_all_in_one_db, "Service", "kong-proxy")
        kong_all_in_one_db_parser_svc_proxy["metadata"]["namespace"] = self.settings.get("KONG_NAMESPACE")
        kong_all_in_one_db_parser_svc_proxy.dump_it()

        kong_all_in_one_db_parser_svc_webhook = Parser(kong_all_in_one_db, "Service", "kong-validation-webhook")
        kong_all_in_one_db_parser_svc_webhook["metadata"]["namespace"] = self.settings.get("KONG_NAMESPACE")
        kong_all_in_one_db_parser_svc_webhook.dump_it()

        kong_all_in_one_db_parser_svc_admin = Parser(kong_all_in_one_db, "Service", "kong-admin")
        kong_all_in_one_db_parser_svc_admin["metadata"]["namespace"] = self.settings.get("KONG_NAMESPACE")
        kong_all_in_one_db_parser_svc_admin.dump_it()

        kong_all_in_one_db_parser_deploy = Parser(kong_all_in_one_db, "Deployment")
        kong_containers = kong_all_in_one_db_parser_deploy["spec"]["template"]["spec"]["containers"]
        kong_all_in_one_db_parser_deploy["metadata"]["namespace"] = self.settings.get("KONG_NAMESPACE")
        proxy_index = 0
        ingress_controller_index = 1
        for container in kong_containers:
            if container["name"] == "proxy":
                proxy_index = kong_containers.index(container)
            if container["name"] == "ingress-controller":
                ingress_controller_index = kong_containers.index(container)
        # Adjust proxy container envs
        env_list = kong_all_in_one_db_parser_deploy["spec"]["template"]["spec"]["containers"][proxy_index]["env"]
        for env in env_list:
            if env["name"] == "KONG_PG_HOST":
                env_list.remove(env)
            if env["name"] == "KONG_PG_USER":
                env_list.remove(env)
        env_list.append({"name": "KONG_PG_HOST", "value": self.settings.get("POSTGRES_URL")})
        env_list.append({"name": "KONG_PG_USER", "value": self.settings.get("KONG_PG_USER")})
        # Adjust kong ingress controller envs
        env_list = \
            kong_all_in_one_db_parser_deploy["spec"]["template"]["spec"]["containers"][ingress_controller_index]["env"]
        for env in env_list:
            if env["name"] == "CONTROLLER_PUBLISH_SERVICE":
                env_list.remove(env)
        env_list.append(
            {"name": "CONTROLLER_PUBLISH_SERVICE", "value": self.settings.get("KONG_NAMESPACE") + "/kong-proxy"})
        kong_all_in_one_db_parser_deploy["spec"]["template"]["spec"]["containers"][ingress_controller_index]["env"] \
            = env_list
        for container in kong_containers:
            if container["name"] == "proxy":
                container["image"] = self.settings.get("GLUU_GATEWAY_IMAGE_NAME") + ":" + \
                                     self.settings.get("GLUU_GATEWAY_IMAGE_TAG")
        kong_all_in_one_db_parser_deploy.dump_it()
        self.kubernetes.create_objects_from_dict(kong_all_in_one_db)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("KONG_NAMESPACE"), "app=ingress-kong", self.timeout)

    def deploy_gluu_gateway_ui(self):
        self.kubernetes.create_namespace(name=self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"),
                                         labels={"APP_NAME": "gluu-gateway-ui"})

        self.setup_tls(namespace=self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"))

        encoded_gg_ui_pg_pass_bytes = base64.b64encode(self.settings.get("GLUU_GATEWAY_UI_PG_PASSWORD").encode("utf-8"))
        encoded_gg_ui_pg_pass_string = str(encoded_gg_ui_pg_pass_bytes, "utf-8")

        self.kubernetes.patch_or_create_namespaced_secret(name="gg-ui-postgres-pass",
                                                          namespace=self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"),
                                                          literal="DB_PASSWORD",
                                                          value_of_literal=encoded_gg_ui_pg_pass_string)
        if self.settings.get("IS_GLUU_FQDN_REGISTERED") != "Y":
            if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "local"):
                self.kubernetes = Kubernetes()
                self.kubernetes.create_objects_from_dict(self.update_lb_ip_yaml,
                                                         self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"))
        self.kubernetes.create_objects_from_dict(self.gg_ui_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"),
                                                "app=gg-kong-ui", self.timeout)

    def uninstall_gluu_gateway_ui(self):
        self.kubernetes.delete_deployment_using_label(self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"), "app=gg-kong-ui")
        self.kubernetes.delete_config_map_using_label(self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"), "app=gg-kong-ui")
        self.kubernetes.delete_job(self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"), "app=gg-kong-ui")
        self.kubernetes.delete_service("gg-kong-ui", self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"))
        self.kubernetes.delete_ingress("gluu-gg-ui", self.settings.get("GLUU_GATEWAY_UI_NAMESPACE"))

    def install_gluu_gateway_dbmode(self):
        # Jackrabbit Cluster would have installed postgres
        if self.settings.get("JACKRABBIT_CLUSTER") == "N":
            self.deploy_postgres()
        else:
            self.create_patch_secret_init_sql()
            logger.info("Restarting postgres...please wait 2mins..")
            self.kubernetes.patch_namespaced_stateful_set_scale(name="postgres",
                                                                replicas=0,
                                                                namespace=self.settings.get("POSTGRES_NAMESPACE"))
            time.sleep(120)
            self.kubernetes.patch_namespaced_stateful_set_scale(name="postgres",
                                                                replicas=3,
                                                                namespace=self.settings.get("POSTGRES_NAMESPACE"))
            self.kubernetes.check_pods_statuses(self.settings.get("POSTGRES_NAMESPACE"), "app=postgres", self.timeout)
        self.deploy_kong()
        self.kustomize_gluu_gateway_ui()
        self.adjust_fqdn_yaml_entries()
        self.deploy_gluu_gateway_ui()

    def deploy_redis(self):
        self.uninstall_redis()
        self.kubernetes.create_namespace(name=self.settings.get("REDIS_NAMESPACE"), labels={"app": "redis"})
        redis_storage_class = Path("./redis/storageclasses.yaml")
        self.analyze_storage_class(redis_storage_class)
        self.kubernetes.create_objects_from_dict(redis_storage_class)

        redis_configmap = Path("./redis/configmaps.yaml")
        redis_conf_parser = Parser(redis_configmap, "ConfigMap")
        redis_conf_parser["metadata"]["namespace"] = self.settings.get("REDIS_NAMESPACE")
        redis_conf_parser.dump_it()
        self.kubernetes.create_objects_from_dict(redis_configmap)

        redis_yaml = Path("./redis/redis.yaml")
        redis_parser = Parser(redis_yaml, "Redis")
        redis_parser["spec"]["cluster"]["master"] = self.settings.get("REDIS_MASTER_NODES")
        redis_parser["spec"]["cluster"]["replicas"] = self.settings.get("REDIS_NODES_PER_MASTER")
        redis_parser["spec"]["monitor"]["prometheus"]["namespace"] = self.settings.get("REDIS_NAMESPACE")
        redis_parser["metadata"]["namespace"] = self.settings.get("REDIS_NAMESPACE")
        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube"):
            del redis_parser["spec"]["podTemplate"]["spec"]["resources"]
        redis_parser.dump_it()
        self.kubernetes.create_namespaced_custom_object(filepath=redis_yaml,
                                                        group="kubedb.com",
                                                        version="v1alpha1",
                                                        plural="redises",
                                                        namespace=self.settings.get("REDIS_NAMESPACE"))

        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=redis-cluster", self.timeout)

    def deploy_config(self):
        self.kubernetes.create_objects_from_dict(self.config_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=config-init-load",
                                                self.timeout)

    def deploy_ldap(self):
        self.kubernetes.create_objects_from_dict(self.ldap_yaml)
        logger.info("Deploying LDAP.Please wait..")
        time.sleep(10)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=opendj", self.timeout)

    def def_jackrabbit_secret(self):
        if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
            encoded_jackrabbit_pg_pass_bytes = base64.b64encode(
                self.settings.get("JACKRABBIT_PG_PASSWORD").encode("utf-8"))
            encoded_jackrabbit_pg_pass_string = str(encoded_jackrabbit_pg_pass_bytes, "utf-8")

            self.kubernetes.patch_or_create_namespaced_secret(name="gluu-jackrabbit-postgres-pass",
                                                              namespace=self.settings.get("GLUU_NAMESPACE"),
                                                              literal="postgres_password",
                                                              value_of_literal=encoded_jackrabbit_pg_pass_string)
            jackrabbit_parser = Parser(self.jackrabbit_yaml, "StatefulSet")
            jackrabbit_parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
                {"mountPath": "/etc/gluu/conf/postgres_password",
                 "name": "jackrabbit-postgres-pass", "subPath": "postgres_password"})
            jackrabbit_parser["spec"]["template"]["spec"]["volumes"].append(
                {"name": "jackrabbit-postgres-pass", "secret": {"secretName": "gluu-jackrabbit-postgres-pass"}})
            jackrabbit_parser.dump_it()
        encoded_jackrabbit_admin_pass_bytes = base64.b64encode(
            self.settings.get("JACKRABBIT_ADMIN_PASSWORD").encode("utf-8"))
        encoded_jackrabbit_admin_pass_string = str(encoded_jackrabbit_admin_pass_bytes, "utf-8")
        self.kubernetes.patch_or_create_namespaced_secret(name="gluu-jackrabbit-admin-pass",
                                                          namespace=self.settings.get("GLUU_NAMESPACE"),
                                                          literal="jackrabbit_admin_password",
                                                          value_of_literal=encoded_jackrabbit_admin_pass_string)

    def deploy_jackrabbit(self):
        self.def_jackrabbit_secret()
        self.kubernetes.create_objects_from_dict(self.jackrabbit_yaml)
        logger.info("Deploying Jackrabbit content repository.Please wait..")
        time.sleep(10)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=jackrabbit", self.timeout)

    def deploy_persistence(self):
        self.kubernetes.create_objects_from_dict(self.persistence_yaml)
        logger.info("Trying to import ldifs...")
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=persistence-load",
                                                self.timeout)
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
            self.kubernetes.patch_namespaced_stateful_set_scale(name="opendj",
                                                                replicas=self.settings.get("LDAP_REPLICAS"),
                                                                namespace=self.settings.get("GLUU_NAMESPACE"))
            if not self.settings.get("AWS_LB_TYPE") == "alb":
                self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=opendj", self.timeout)

    def deploy_update_lb_ip(self):
        self.kubernetes.create_objects_from_dict(self.update_lb_ip_yaml)

    def deploy_oxauth(self):
        self.kubernetes.create_objects_from_dict(self.oxauth_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=oxauth", self.timeout)
        self.kubernetes.patch_namespaced_deployment_scale(name="oxauth", replicas=self.settings.get("OXAUTH_REPLICAS"),
                                                          namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_fido2(self):
        self.kubernetes.create_objects_from_dict(self.fido2_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=fido2", self.timeout)
        self.kubernetes.patch_namespaced_deployment_scale(name="fido2", replicas=self.settings.get("FIDO2_REPLICAS"),
                                                          namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_scim(self):
        self.kubernetes.create_objects_from_dict(self.scim_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=scim", self.timeout)
        self.kubernetes.patch_namespaced_deployment_scale(name="scim", replicas=self.settings.get("SCIM_REPLICAS"),
                                                          namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_oxd(self):
        self.kubernetes.create_objects_from_dict(self.oxd_server_yaml)
        self.kubernetes.create_objects_from_dict(Path("./oxd-server/base/networkpolicy.yaml"),
                                                 self.settings.get("GLUU_NAMESPACE"))
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=oxd-server", self.timeout)
        self.kubernetes.patch_namespaced_deployment_scale(name="oxd-server",
                                                          replicas=self.settings.get("OXD_SERVER_REPLICAS"),
                                                          namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_casa(self):
        self.kubernetes.create_objects_from_dict(self.casa_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=casa", self.timeout)
        self.kubernetes.patch_namespaced_deployment_scale(name="casa", replicas=self.settings.get("CASA_REPLICAS"),
                                                          namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_oxtrust(self):
        self.kubernetes.create_objects_from_dict(self.oxtrust_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=oxtrust", self.timeout)
        self.kubernetes.patch_namespaced_stateful_set_scale(name="oxtrust",
                                                            replicas=self.settings.get("OXTRUST_REPLICAS"),
                                                            namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_oxshibboleth(self):
        self.kubernetes.create_objects_from_dict(self.oxshibboleth_yaml)
        self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=oxshibboleth", self.timeout)
        self.kubernetes.patch_namespaced_stateful_set_scale(name="oxshibboleth",
                                                            replicas=self.settings.get("OXSHIBBOLETH_REPLICAS"),
                                                            namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_oxpassport(self):
        self.kubernetes.create_objects_from_dict(self.oxpassport_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=oxpassport", self.timeout)
        self.kubernetes.patch_namespaced_deployment_scale(name="oxpassport",
                                                          replicas=self.settings.get("OXPASSPORT_REPLICAS"),
                                                          namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_oxauth_key_rotation(self):
        self.kubernetes.create_objects_from_dict(self.oxauth_key_rotate_yaml)

    def deploy_radius(self):
        self.kubernetes.create_objects_from_dict(self.radius_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=radius", self.timeout)
        self.kubernetes.patch_namespaced_deployment_scale(name="radius", replicas=self.settings.get("RADIUS_REPLICAS"),
                                                          namespace=self.settings.get("GLUU_NAMESPACE"))

    def deploy_cr_rotate(self):
        self.kubernetes.delete_role("gluu-role", self.settings.get("GLUU_NAMESPACE"))
        self.kubernetes.delete_role_binding("gluu-rolebinding", self.settings.get("GLUU_NAMESPACE"))
        self.kubernetes.delete_cluster_role_binding("gluu-rolebinding")
        time.sleep(10)
        self.kubernetes.create_objects_from_dict(self.cr_rotate_yaml)

    def deploy_gluu_istio_ingress(self):
        self.kubernetes.create_objects_from_dict(self.gluu_istio_ingress_yaml,
                                                 namespace=self.settings.get("GLUU_NAMESPACE"))

    def copy_configs_before_restore(self):
        self.gluu_secret = self.kubernetes.read_namespaced_secret("gluu", self.settings.get("GLUU_NAMESPACE")).data
        self.gluu_config = self.kubernetes.read_namespaced_configmap("gluu", self.settings.get("GLUU_NAMESPACE")).data

    def save_a_copy_of_config(self):
        self.kubernetes.patch_or_create_namespaced_secret(name="secret-params", literal=None, value_of_literal=None,
                                                          namespace=self.settings.get("GLUU_NAMESPACE"),
                                                          data=self.gluu_secret)
        self.kubernetes.patch_or_create_namespaced_configmap(name="config-params",
                                                             namespace=self.settings.get("GLUU_NAMESPACE"),
                                                             data=self.gluu_config)

    def mount_config(self):
        self.kubernetes.patch_or_create_namespaced_secret(name="gluu", literal=None, value_of_literal=None,
                                                          namespace=self.settings.get("GLUU_NAMESPACE"),
                                                          data=self.gluu_secret)
        self.kubernetes.patch_or_create_namespaced_configmap(name="gluu",
                                                             namespace=self.settings.get("GLUU_NAMESPACE"),
                                                             data=self.gluu_config)

    def run_backup_command(self):
        try:
            exec_ldap_command = ["/opt/opendj/bin/import-ldif", "-n", " ",
                                 "-l", "/opt/opendj/ldif/backup-this-copy.ldif",
                                 "--bindPassword", self.settings.get("LDAP_PW")]
            self.kubernetes.connect_get_namespaced_pod_exec(exec_command=exec_ldap_command,
                                                            app_label="app=opendj",
                                                            container="opendj",
                                                            namespace=self.settings.get("GLUU_NAMESPACE"))
        except (ConnectionError, Exception):
            pass

    def setup_backup_ldap(self):
        encoded_ldap_pw_bytes = base64.b64encode(self.settings.get("LDAP_PW").encode("utf-8"))
        encoded_ldap_pw_string = str(encoded_ldap_pw_bytes, "utf-8")
        self.kubernetes.patch_or_create_namespaced_secret(name="ldap-auth",
                                                          namespace=self.settings.get("GLUU_NAMESPACE"),
                                                          literal="password",
                                                          value_of_literal=encoded_ldap_pw_string)
        kustomize_parser = Parser("ldap/backup/kustomization.yaml", "Kustomization")
        kustomize_parser["namespace"] = self.settings.get("GLUU_NAMESPACE")
        kustomize_parser["configMapGenerator"][0]["literals"] = ["GLUU_LDAP_AUTO_REPLICATE=" + self.settings.get(
            "GLUU_CACHE_TYPE"), "GLUU_CONFIG_KUBERNETES_NAMESPACE=" + self.settings.get("GLUU_NAMESPACE"),
                                                                 "GLUU_SECRET_KUBERNETES_NAMESPACE=" +
                                                                 self.settings.get("GLUU_NAMESPACE"),
                                                                 "GLUU_CONFIG_ADAPTER=kubernetes",
                                                                 "GLUU_SECRET_ADAPTER=kubernetes",
                                                                 "GLUU_LDAP_INIT='true'",
                                                                 "GLUU_LDAP_INIT_HOST='opendj'",
                                                                 "GLUU_LDAP_INIT_PORT='1636'",
                                                                 "GLUU_CERT_ALT_NAME='opendj'",
                                                                 "GLUU_PERSISTENCE_LDAP_MAPPING=" + self.settings.get(
                                                                     "HYBRID_LDAP_HELD_DATA"),
                                                                 "GLUU_PERSISTENCE_TYPE=" + self.settings.get(
                                                                     "PERSISTENCE_BACKEND")]
        kustomize_parser.dump_it()
        cron_job_parser = Parser("ldap/backup/cronjobs.yaml", "CronJob")
        cron_job_parser["spec"]["schedule"] = self.settings.get("LDAP_BACKUP_SCHEDULE")
        cron_job_parser.dump_it()
        command = self.kubectl + " kustomize ldap/backup"
        exec_cmd(command, output_file="./ldap-backup.yaml")
        self.kubernetes.create_objects_from_dict("./ldap-backup.yaml")

    def upgrade(self):
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
            exec_delete_command = ["/opt/opendj/bin/dsconfig", "delete-backend-index", "--backend-name", "userRoot",
                                   "--index-name", "oxAuthExpiration", "--hostName", "0.0.0.0", "--port", "4444",
                                   "--bindDN",
                                   "'cn=Directory Manager'", "--trustAll", "-f"]
            manual_exec_delete_command = " ".join(exec_delete_command)
            logger.warning("Please delete backend index manually by calling\n kubectl exec -ti opendj-0 -n {} "
                           "-- {}".format(self.settings.get("GLUU_NAMESPACE"), manual_exec_delete_command))
            input("Press Enter once index has been deleted...")
            self.kubernetes.delete_stateful_set(self.settings.get("GLUU_NAMESPACE"), "app=opendj")
        self.kustomize_gluu_upgrade()
        self.kustomize_it()
        self.adjust_fqdn_yaml_entries()
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=gluu-upgrade", self.timeout)
        self.kubernetes = Kubernetes()
        if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
            if self.settings.get("INSTALL_GLUU_GATEWAY") == "N":
                self.deploy_postgres()
            else:
                self.create_patch_secret_init_sql()
                logger.info("Restarting postgres...please wait 2mins..")
                self.kubernetes.patch_namespaced_stateful_set_scale(name="postgres",
                                                                    replicas=0,
                                                                    namespace=self.settings.get("POSTGRES_NAMESPACE"))
                time.sleep(120)
                self.kubernetes.patch_namespaced_stateful_set_scale(name="postgres",
                                                                    replicas=3,
                                                                    namespace=self.settings.get("POSTGRES_NAMESPACE"))
                self.kubernetes.check_pods_statuses(self.settings.get("POSTGRES_NAMESPACE"), "app=postgres",
                                                    self.timeout)
            self.def_jackrabbit_secret()
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap"):
            self.kubernetes.create_objects_from_dict("ldap/base/101-ox.yaml",
                                                     self.settings.get("GLUU_NAMESPACE"))
            ldap_parser = Parser(self.ldap_yaml, "StatefulSet")
            ldap_parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"].append(
                {"mountPath": "/opt/opendj/config/schema/101-ox.ldif",
                 "name": "ox-ldif-cm", "subPath": "101-ox.ldif"})
            ldap_parser["spec"]["template"]["spec"]["volumes"].append(
                {"name": "ox-ldif-cm", "configMap": {"name": "oxldif"}})
            ldap_parser.dump_it()
            exec_cmd("kubectl apply -f {} --record".format(self.config_yaml), silent=True)
            exec_cmd("kubectl apply -f {} --record".format(self.ldap_yaml), silent=True)
            logger.info("Deploying LDAP.Please wait..")
            time.sleep(10)
            if not self.settings.get("AWS_LB_TYPE") == "alb":
                self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=opendj", self.timeout)
        self.kubernetes.create_objects_from_dict(self.gluu_upgrade_yaml)
        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("GLUU_NAMESPACE"), "app=gluu-upgrade", self.timeout)
        logger.info("Updating manifests and Gluu version...")
        stdout, stderr, retcode = exec_cmd("kubectl apply -f {}/. --record".format(self.output_yaml_directory),
                                           silent=True)

    def install(self, install_couchbase=True, restore=False):
        if not restore:
            labels = {"app": "gluu"}
            if self.settings.get("USE_ISTIO") == "Y":
                labels = {"app": "gluu", "istio-injection": "enabled"}
            self.kubernetes.create_namespace(name=self.settings.get("GLUU_NAMESPACE"), labels=labels)
        self.kustomize_it()
        self.adjust_fqdn_yaml_entries()
        if install_couchbase:
            if self.settings.get("PERSISTENCE_BACKEND") != "ldap":
                if self.settings.get("INSTALL_COUCHBASE") == "Y":
                    couchbase_app = Couchbase()
                    couchbase_app.uninstall()
                    couchbase_app = Couchbase()
                    couchbase_app.install()
                else:
                    encoded_cb_pass_bytes = base64.b64encode(self.settings.get("COUCHBASE_PASSWORD").encode("utf-8"))
                    encoded_cb_pass_string = str(encoded_cb_pass_bytes, "utf-8")
                    encoded_cb_super_pass_bytes = base64.b64encode(
                        self.settings.get("COUCHBASE_SUPERUSER_PASSWORD").encode("utf-8"))
                    encoded_cb_super_pass_string = str(encoded_cb_super_pass_bytes, "utf-8")
                    couchbase_app = Couchbase()
                    couchbase_app.create_couchbase_gluu_cert_pass_secrets(self.settings.get("COUCHBASE_CRT"),
                                                                          encoded_cb_pass_string,
                                                                          encoded_cb_super_pass_string)
        if not restore:
            self.kubernetes = Kubernetes()
            if self.settings.get("AWS_LB_TYPE") == "alb":
                self.prepare_alb()
                self.deploy_alb()
            elif self.settings.get("USE_ISTIO_INGRESS") == "Y":
                self.deploy_gluu_istio_ingress()
                self.set_lb_address()
            else:
                self.deploy_nginx()
        self.adjust_fqdn_yaml_entries()
        if self.settings.get("DEPLOY_MULTI_CLUSTER") != "Y":
            self.kubernetes = Kubernetes()
            if restore:
                self.mount_config()
                self.save_a_copy_of_config()
            else:
                self.deploy_config()

        if self.settings.get("USE_ISTIO_INGRESS") == "Y":
            self.setup_tls(namespace=self.settings.get("ISTIO_SYSTEM_NAMESPACE"))

        if self.settings.get("INSTALL_JACKRABBIT") == "Y" and not restore:
            self.kubernetes = Kubernetes()
            if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
                self.deploy_postgres()

            self.deploy_jackrabbit()

        if not self.settings.get("AWS_LB_TYPE") == "alb":
            self.setup_tls(namespace=self.settings.get("GLUU_NAMESPACE"))

        if self.settings.get("INSTALL_REDIS") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_redis()

        if self.settings.get("PERSISTENCE_BACKEND") == "hybrid" or \
                self.settings.get("PERSISTENCE_BACKEND") == "ldap":
            self.kubernetes = Kubernetes()
            if restore:
                self.run_backup_command()
                self.mount_config()
                self.wait_for_nginx_add()
            else:
                self.deploy_ldap()
                if self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
                    self.setup_backup_ldap()

        if not restore:
            self.kubernetes = Kubernetes()
            self.deploy_persistence()

        if self.settings.get("IS_GLUU_FQDN_REGISTERED") != "Y":
            if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "local"):
                self.kubernetes = Kubernetes()
                self.deploy_update_lb_ip()

        self.kubernetes = Kubernetes()
        self.deploy_oxauth()

        if self.settings.get("ENABLE_FIDO2") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_fido2()

        if self.settings.get("ENABLE_SCIM") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_scim()

        if self.settings.get("ENABLE_OXD") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_oxd()

        if self.settings.get("ENABLE_CASA") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_casa()
        self.kubernetes = Kubernetes()
        self.deploy_oxtrust()

        if self.settings.get("ENABLE_OXSHIBBOLETH") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_oxshibboleth()
            if restore:
                self.mount_config()

        if self.settings.get("ENABLE_OXPASSPORT") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_oxpassport()

        if self.settings.get("ENABLE_CACHE_REFRESH") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_cr_rotate()

        if self.settings.get("ENABLE_OXAUTH_KEY_ROTATE") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_oxauth_key_rotation()
            if restore:
                self.mount_config()

        if self.settings.get("ENABLE_RADIUS") == "Y":
            self.deploy_radius()

        if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            self.kubernetes = Kubernetes()
            self.install_gluu_gateway_dbmode()

    def uninstall(self, restore=False):
        gluu_service_names = ["casa", "cr-rotate", "opendj", "oxauth", "oxpassport",
                              "oxshibboleth", "oxtrust", "radius", "oxd-server",
                              "jackrabbit", "fido2", "scim", "config-init-load-job"]
        gluu_storage_class_names = ["opendj-sc", "jackrabbit-sc"]
        nginx_service_name = "ingress-nginx"
        gluu_deployment_app_labels = ["app=casa", "app=oxauth", "app=fido2", "app=scim", "app=oxd-server",
                                      "app=oxpassport", "app=radius", "app=oxauth-key-rotation", "app=jackrabbit"]
        nginx_deployemnt_app_name = "nginx-ingress-controller"
        stateful_set_labels = ["app=opendj", "app=oxtrust", "app=oxshibboleth", "app=jackrabbit"]
        jobs_labels = ["app=config-init-load", "app=persistence-load", "app=gluu-upgrade"]
        secrets = ["oxdkeystorecm", "gluu", "tls-certificate",
                   "gluu-jackrabbit-admin-pass", "gluu-jackrabbit-postgres-pass"]
        cb_secrets = ["cb-pass", "cb-crt", "cb-super-pass"]
        daemon_set_label = "app=cr-rotate"
        all_labels = gluu_deployment_app_labels + stateful_set_labels + jobs_labels + [daemon_set_label]
        gluu_config_maps_names = ["casacm", "updatelbip", "gluu"]
        nginx_config_maps_names = ["nginx-configuration", "tcp-services", "udp-services"]
        gluu_cluster_role_bindings_name = "cluster-admin-binding"
        nginx_roles_name = "nginx-ingress-role"
        nginx_cluster_role_name = "nginx-ingress-clusterrole"
        nginx_role_bindings_name = "nginx-ingress-role-nisa-binding"
        nginx_cluster_role_bindings_name = "nginx-ingress-clusterrole-nisa-binding"
        nginx_service_account_name = "nginx-ingress-serviceaccount"
        nginx_ingress_extensions_names = ["gluu-ingress-base", "gluu-ingress-openid-configuration",
                                          "gluu-ingress-uma2-configuration", "gluu-ingress-webfinger",
                                          "gluu-ingress-simple-web-discovery", "gluu-ingress-scim-configuration",
                                          "gluu-ingress-fido-u2f-configuration", "gluu-ingress",
                                          "gluu-ingress-stateful", "gluu-casa", "gluu-ingress-fido2-configuration"]
        network_policies = ["oxd-server-policy"]
        minkube_yamls_folder = Path("./gluuminikubeyamls")
        microk8s_yamls_folder = Path("./gluumicrok8yamls")
        eks_yamls_folder = Path("./gluueksyamls")
        gke_yamls_folder = Path("./gluugkeyamls")
        aks_yamls_folder = Path("./gluuaksyamls")
        if restore:
            gluu_service_names.pop(3)
            gluu_storage_class_names.pop(1)
            stateful_set_labels.pop(0)

        for service in gluu_service_names:
            self.kubernetes.delete_service(service, self.settings.get("GLUU_NAMESPACE"))
        for network_policy in network_policies:
            self.kubernetes.delete_network_policy(network_policy, self.settings.get("GLUU_NAMESPACE"))
        if not restore:
            if self.settings.get("INSTALL_REDIS") == "Y":
                self.uninstall_redis()
            if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
                self.uninstall_postgres()
                self.uninstall_kong()
                self.uninstall_gluu_gateway_ui()
            elif self.settings.get("JACKRABBIT_CLUSTER") == "Y":
                self.uninstall_postgres()

            self.kubernetes.delete_service(nginx_service_name, "ingress-nginx")
        self.kubernetes.delete_cronjob(self.settings.get("GLUU_NAMESPACE"), "app=oxauth-key-rotation")
        for deployment in gluu_deployment_app_labels:
            self.kubernetes.delete_deployment_using_label(self.settings.get("GLUU_NAMESPACE"), deployment)
        if not restore:
            self.kubernetes.delete_deployment_using_name(nginx_deployemnt_app_name, "ingress-nginx")
        for stateful_set in stateful_set_labels:
            self.kubernetes.delete_stateful_set(self.settings.get("GLUU_NAMESPACE"), stateful_set)
        for job in jobs_labels:
            self.kubernetes.delete_job(self.settings.get("GLUU_NAMESPACE"), job)
        for secret in secrets:
            self.kubernetes.delete_secret(secret, self.settings.get("GLUU_NAMESPACE"))
        if not restore:
            for secret in cb_secrets:
                self.kubernetes.delete_secret(secret, self.settings.get("GLUU_NAMESPACE"))
        self.kubernetes.delete_daemon_set(self.settings.get("GLUU_NAMESPACE"), daemon_set_label)
        for config_map in gluu_config_maps_names:
            self.kubernetes.delete_config_map_using_name(config_map, self.settings.get("GLUU_NAMESPACE"))
        if not restore:
            for config_map in nginx_config_maps_names:
                self.kubernetes.delete_config_map_using_name(config_map, "ingress-nginx")
        for cm_pv_pvc in all_labels:
            self.kubernetes.delete_config_map_using_label(self.settings.get("GLUU_NAMESPACE"), cm_pv_pvc)
            self.kubernetes.delete_persistent_volume(cm_pv_pvc)
            self.kubernetes.delete_persistent_volume_claim(self.settings.get("GLUU_NAMESPACE"), cm_pv_pvc)
        for storage_class in gluu_storage_class_names:
            self.kubernetes.delete_storage_class(storage_class)

        if not restore:
            self.kubernetes.delete_role("gluu-role", self.settings.get("GLUU_NAMESPACE"))
            self.kubernetes.delete_role_binding("gluu-rolebinding", self.settings.get("GLUU_NAMESPACE"))
            self.kubernetes.delete_role(nginx_roles_name, "ingress-nginx")
            self.kubernetes.delete_cluster_role_binding("gluu-rolebinding")
            self.kubernetes.delete_cluster_role_binding(gluu_cluster_role_bindings_name)
            self.kubernetes.delete_role_binding(nginx_role_bindings_name, "ingress-nginx")
            self.kubernetes.delete_cluster_role_binding(nginx_cluster_role_bindings_name)
            self.kubernetes.delete_service_account(nginx_service_account_name, "ingress-nginx")
            self.kubernetes.delete_cluster_role(nginx_cluster_role_name)
            for extension in nginx_ingress_extensions_names:
                self.kubernetes.delete_ingress(extension, self.settings.get("GLUU_NAMESPACE"))
        if minkube_yamls_folder.exists() or microk8s_yamls_folder.exists():
            shutil.rmtree('/data', ignore_errors=True)
        else:
            for node_ip in self.settings.get("NODES_IPS"):
                if self.settings.get("DEPLOYMENT_ARCH") == "minikube":
                    exec_cmd("minikube ssh 'sudo rm -rf /data'")
                elif self.settings.get("DEPLOYMENT_ARCH") == "microk8s":
                    shutil.rmtree('/data', ignore_errors=True)
                else:
                    if self.settings.get("APP_VOLUME_TYPE") in (6, 16):
                        if self.settings.get("DEPLOYMENT_ARCH") == "eks":
                            ssh_and_remove(self.settings.get("NODE_SSH_KEY"), "ec2-user", node_ip, "/data")
                        elif self.settings.get("DEPLOYMENT_ARCH") == "aks":
                            ssh_and_remove(self.settings.get("NODE_SSH_KEY"), "opc", node_ip, "/data")
            if self.settings.get("APP_VOLUME_TYPE") == 11:
                if self.settings.get("DEPLOYMENT_ARCH") == "gke":
                    for node_name in self.settings.get("NODES_NAMES"):
                        for zone in self.settings.get("NODES_ZONES"):
                            exec_cmd("gcloud compute ssh user@{} --zone={} --command='sudo rm -rf $HOME/opendj'".
                                     format(node_name, zone))
                            exec_cmd("gcloud compute ssh user@{} --zone={} --command='sudo rm -rf $HOME/jackrabbit'".
                                     format(node_name, zone))
        if not restore:
            shutil.rmtree(Path("./previousgluuminikubeyamls"), ignore_errors=True)
            shutil.rmtree(Path("./previousgluumicrok8yamls"), ignore_errors=True)
            shutil.rmtree(Path("./previousgluueksyamls"), ignore_errors=True)
            shutil.rmtree(Path("./previousgluuaksyamls"), ignore_errors=True)
            shutil.rmtree(Path("./previousgluugkeyamls"), ignore_errors=True)
            with contextlib.suppress(FileNotFoundError):
                shutil.copytree(minkube_yamls_folder, Path("./previousgluuminikubeyamls"))
            with contextlib.suppress(FileNotFoundError):
                shutil.copytree(microk8s_yamls_folder, Path("./previousgluumicrok8yamls"))
            with contextlib.suppress(FileNotFoundError):
                shutil.copytree(eks_yamls_folder, Path("./previousgluueksyamls"))
            with contextlib.suppress(FileNotFoundError):
                shutil.copytree(aks_yamls_folder, Path("./previousgluuaksyamls"))
            with contextlib.suppress(FileNotFoundError):
                shutil.copytree(gke_yamls_folder, Path("./previousgluugkeyamls"))
            with contextlib.suppress(FileNotFoundError):
                shutil.move(Path("./ingress.crt"), Path("./previous-ingress.crt"))
            with contextlib.suppress(FileNotFoundError):
                shutil.move(Path("./ingress.key"), Path("./previous-ingress.key"))
            with contextlib.suppress(FileNotFoundError):
                time_str = time.strftime("_created_%d-%m-%Y_%H-%M-%S")
                shutil.copy(Path("./settings.json"), Path("./settings" + time_str + ".json"))

    def uninstall_redis(self):
        logger.info("Removing gluu-redis-cluster...")
        logger.info("Removing redis...")
        redis_yaml = Path("./redis/redis.yaml")
        self.kubernetes.delete_namespaced_custom_object(filepath=redis_yaml,
                                                        group="kubedb.com",
                                                        version="v1alpha1",
                                                        plural="redises",
                                                        namespace=self.settings.get("REDIS_NAMESPACE"))
        self.kubernetes.delete_storage_class("redis-sc")
        self.kubernetes.delete_service("kubedb", self.settings.get("REDIS_NAMESPACE"))

    def uninstall_kong(self):
        logger.info("Removing gluu gateway kong...")
        self.kubernetes.delete_job(self.settings.get("KONG_NAMESPACE"), "app=kong-migration-job")
        self.kubernetes.delete_custom_resource("kongconsumers.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("kongcredentials.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("kongingresses.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("kongplugins.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("tcpingresses.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("kongclusterplugins.configuration.konghq.com")
        self.kubernetes.delete_cluster_role("kong-ingress-clusterrole")
        self.kubernetes.delete_service_account("kong-serviceaccount", self.settings.get("KONG_NAMESPACE"))
        self.kubernetes.delete_cluster_role_binding("kong-ingress-clusterrole-nisa-binding")
        self.kubernetes.delete_config_map_using_name("kong-server-blocks", self.settings.get("KONG_NAMESPACE"))
        self.kubernetes.delete_service("kong-proxy", self.settings.get("KONG_NAMESPACE"))
        self.kubernetes.delete_service("kong-validation-webhook", self.settings.get("KONG_NAMESPACE"))
        self.kubernetes.delete_service("kong-admin", self.settings.get("KONG_NAMESPACE"))
        self.kubernetes.delete_deployment_using_name("ingress-kong", self.settings.get("KONG_NAMESPACE"))

    def uninstall_postgres(self):
        logger.info("Removing gluu-postgres...")
        self.kubernetes.delete_namespaced_custom_object_by_name(group="kubedb.com",
                                                                version="v1alpha1",
                                                                plural="postgreses",
                                                                name="postgres",
                                                                namespace=self.settings.get("POSTGRES_NAMESPACE"))
        self.kubernetes.delete_namespaced_custom_object_by_name(group="kubedb.com",
                                                                version="v1alpha1",
                                                                plural="postgresversions",
                                                                name="postgres",
                                                                namespace=self.settings.get("POSTGRES_NAMESPACE"))
        self.kubernetes.delete_storage_class("postgres-sc")
        self.kubernetes.delete_service("kubedb", self.settings.get("POSTGRES_NAMESPACE"))
        self.kubernetes.delete_service("postgres", self.settings.get("POSTGRES_NAMESPACE"))
        self.kubernetes.delete_service("postgres-replicas", self.settings.get("POSTGRES_NAMESPACE"))
        self.kubernetes.delete_service("postgres-stats", self.settings.get("POSTGRES_NAMESPACE"))
