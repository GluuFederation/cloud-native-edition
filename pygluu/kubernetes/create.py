#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 License terms and conditions:
 https://www.gluu.org/license/enterprise-edition/
"""

import argparse
from pathlib import Path
import contextlib
import os
import shutil
import time
import errno
import socket
import subprocess
import sys
from .kubeapi import Kubernetes
from .couchbase import Couchbase
from .prompt import Prompt
from .yamlparser import Parser, get_logger
from .helm import Helm

logger = get_logger("gluu-create        ")

# Local Deployments
local_minikube_folder = Path("./ldap/overlays/minikube/local-storage/")
local_microk8s_folder = Path("./ldap/overlays/microk8s/local-storage/")
# AWS
local_eks_folder = Path("./ldap/overlays/eks/local-storage/")
dynamic_eks_folder = Path("./ldap/overlays/eks/dynamic-ebs/")
static_eks_folder = Path("./ldap/overlays/eks/static-ebs/")
efs_eks_folder = Path("./ldap/overlays/eks/efs/")
# GCE
local_gke_folder = Path("./ldap/overlays/gke/local-storage/")
dynamic_gke_folder = Path("./ldap/overlays/gke/dynamic-pd/")
static_gke_folder = Path("./ldap/overlays/gke/static-pd/")
# AZURE
local_azure_folder = Path("./ldap/overlays/azure/local-storage/")
dynamic_azure_folder = Path("./ldap/overlays/azure/dynamic-dn/")
static_azure_folder = Path("./ldap/overlays/azure/static-dn/")


def subprocess_cmd(command):
    """Execute command"""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout


def ssh_and_remove(key, user, node_ip, folder_to_be_removed):
    """Execute ssh command and remove directory"""
    subprocess_cmd("ssh -oStrictHostKeyChecking=no -i {} {}@{} sudo rm -rf {}"
                   .format(key, user, node_ip, folder_to_be_removed))


def check_port(host, port):
    """Check if ports are open"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        conn = sock.connect_ex((host, port))
        if conn == 0:
            # port is not available
            return False
        return True


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            logger.error('Directory not copied. Error: {}'.format(e))


def copy_templates():
    entries = Path(
        os.path.join(os.path.dirname(__file__), "templates")
    )
    curdir = os.getcwd()
    for entry in entries.iterdir():
        dst = os.path.join(curdir, entry.name)
        if os.path.exists(dst):
            continue
        copy(entry, dst)


class App(object):
    def __init__(self):
        self.kubernetes = Kubernetes()
        prompts = Prompt()
        self.settings = prompts.check_settings_and_prompt

        if self.settings["DEPLOYMENT_ARCH"] != "microk8s":
            for port in [80, 443]:
                port_available = check_port("0.0.0.0", port)
                if not port_available:
                    logger.error(f'Required port {port} is bind to another process')
                    raise SystemExit(1)

        self.kubectl = self.detect_kubectl
        self.output_yaml_directory, self.kustomize_yaml_directory = self.set_output_yaml_directory
        self.shared_shib_yaml = str(self.output_yaml_directory.joinpath("shared-shib.yaml").resolve())
        self.config_yaml = str(self.output_yaml_directory.joinpath("config.yaml").resolve())
        self.ldap_yaml = str(self.output_yaml_directory.joinpath("ldap.yaml").resolve())
        self.persistence_yaml = str(self.output_yaml_directory.joinpath("persistence.yaml").resolve())
        self.oxauth_yaml = str(self.output_yaml_directory.joinpath("oxauth.yaml").resolve())
        self.oxtrust_yaml = str(self.output_yaml_directory.joinpath("oxtrust.yaml").resolve())
        self.oxshibboleth_yaml = str(self.output_yaml_directory.joinpath("oxshibboleth.yaml").resolve())
        self.oxpassport_yaml = str(self.output_yaml_directory.joinpath("oxpassport.yaml").resolve())
        self.key_rotate_yaml = str(self.output_yaml_directory.joinpath("key-rotation.yaml").resolve())
        self.cr_rotate_yaml = str(self.output_yaml_directory.joinpath("cr-rotate.yaml").resolve())
        self.oxd_server_yaml = str(self.output_yaml_directory.joinpath("oxd-server.yaml").resolve())
        self.casa_yaml = str(self.output_yaml_directory.joinpath("casa.yaml").resolve())
        self.radius_yaml = str(self.output_yaml_directory.joinpath("radius.yaml").resolve())
        self.redis_yaml = str(self.output_yaml_directory.joinpath("redis.yaml").resolve())
        self.update_lb_ip_yaml = str(self.output_yaml_directory.joinpath("updatelbip.yaml").resolve())
        self.adjust_yamls_for_fqdn_status = dict()

    @property
    def detect_kubectl(self):
        """Detect kubectl command"""
        # TODO: Set alias microk8s.kubectl to kubectl

        if self.settings["DEPLOYMENT_ARCH"] == "microk8s":
            kubectl = "microk8s.kubectl"
        else:
            kubectl = "kubectl"
        return kubectl

    @property
    def set_output_yaml_directory(self):

        if self.settings["DEPLOYMENT_ARCH"] == "minikube":
            copy(local_microk8s_folder, local_minikube_folder)
            output_yamls_folder = Path("gluu_minikube_yamls")
            kustomize_yaml_directory = local_minikube_folder

        elif self.settings["DEPLOYMENT_ARCH"] == "eks":
            output_yamls_folder = Path("gluu_eks_yamls")
            if self.settings["LDAP_VOLUME_TYPE"] == 7:
                parser = Parser(dynamic_eks_folder.joinpath("storageclasses.yaml"), "StorageClass")
                parser["provisioner"] = "kubernetes.io/aws-ebs"
                parser["parameters"]["encrypted"] = "true"
                parser["parameters"]["type"] = self.settings["LDAP_VOLUME"]
                parser["allowedTopologies"][0]["matchLabelExpressions"][0]["values"] = self.settings["NODES_ZONES"]
                parser.dump_it()
                kustomize_yaml_directory = dynamic_eks_folder
            elif self.settings["LDAP_VOLUME_TYPE"] == 8:
                kustomize_yaml_directory = static_eks_folder
            elif self.settings["LDAP_VOLUME_TYPE"] == 9:
                kustomize_yaml_directory = efs_eks_folder
            else:
                kustomize_yaml_directory = local_eks_folder

        elif self.settings["DEPLOYMENT_ARCH"] == "gke":
            output_yamls_folder = Path("gluu_gke_yamls")
            if self.settings["LDAP_VOLUME_TYPE"] == 12:
                try:
                    shutil.rmtree(dynamic_gke_folder)
                except FileNotFoundError:
                    logger.info("Directory not found. Copying...")
                copy(dynamic_eks_folder, dynamic_gke_folder)
                parser = Parser(dynamic_gke_folder.joinpath("storageclasses.yaml"), "StorageClass")
                parser["provisioner"] = "kubernetes.io/gce-pd"
                del parser["parameters"]["encrypted"]
                parser["parameters"]["type"] = self.settings["LDAP_VOLUME"]
                parser["allowedTopologies"][0]["matchLabelExpressions"][0]["values"] = self.settings["NODES_ZONES"]
                parser.dump_it()
                kustomize_yaml_directory = dynamic_gke_folder
            elif self.settings["LDAP_VOLUME_TYPE"] == 13:
                kustomize_yaml_directory = static_gke_folder
            else:
                kustomize_yaml_directory = local_gke_folder

        elif self.settings["DEPLOYMENT_ARCH"] == "aks":
            output_yamls_folder = Path("gluu_aks_yamls")
            if self.settings["LDAP_VOLUME_TYPE"] == 17:
                copy(dynamic_eks_folder, dynamic_azure_folder)
                parser = Parser(dynamic_azure_folder.joinpath("storageclasses.yaml"), "StorageClass")
                parser["provisioner"] = "kubernetes.io/azure-disk"
                del parser["parameters"]["encrypted"]
                del parser["parameters"]["type"]
                parser["parameters"]["storageaccounttype"] = self.settings["LDAP_VOLUME"]
                parser["allowedTopologies"][0]["matchLabelExpressions"][0]["values"] = self.settings["NODES_ZONES"]
                parser.dump_it()
                kustomize_yaml_directory = dynamic_azure_folder
            elif self.settings["LDAP_VOLUME_TYPE"] == 18:
                kustomize_yaml_directory = static_azure_folder
            else:
                kustomize_yaml_directory = local_azure_folder
        else:
            output_yamls_folder = Path("gluu_microk8s_yamls")
            kustomize_yaml_directory = local_microk8s_folder
        if not output_yamls_folder.exists():
            os.mkdir(output_yamls_folder)
        return output_yamls_folder, kustomize_yaml_directory

    def adjust_fqdn_yaml_entries(self):
        if self.settings["IS_GLUU_FQDN_REGISTERED"] == "Y" \
                or self.settings["DEPLOYMENT_ARCH"] == "microk8s" or self.settings["DEPLOYMENT_ARCH"] == "minikube" \
                or self.settings["DEPLOYMENT_ARCH"] == "gke":
            for k, v in self.adjust_yamls_for_fqdn_status.items():
                parser = Parser(k, v)
                volume_mount_list = parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
                volume_list = parser["spec"]["template"]["spec"]["volumes"]

                if k != self.cr_rotate_yaml and k != self.key_rotate_yaml:
                    cm_parser = Parser(k, "ConfigMap")
                    del cm_parser["data"]["LB_ADDR"]
                    cm_parser.dump_it()
                    if self.settings["DEPLOYMENT_ARCH"] == "microk8s" or self.settings["DEPLOYMENT_ARCH"] == "minikube" or self.settings[
                        "DEPLOYMENT_ARCH"] == "gke":
                        parser["spec"]["template"]["spec"]["hostAliases"][0]["hostnames"] = [self.settings["GLUU_FQDN"]]
                        parser["spec"]["template"]["spec"]["hostAliases"][0]["ip"] = self.settings["HOST_EXT_IP"]
                    else:
                        del parser["spec"]["template"]["spec"]["hostAliases"]
                    del parser["spec"]["template"]["spec"]["containers"][0]["command"]
                    update_lb_ip_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "update-lb-ip"), None)
                    del volume_mount_list[update_lb_ip_vm_index]
                    volume_list = parser["spec"]["template"]["spec"]["volumes"]
                    update_lb_ip_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "update-lb-ip"), None)
                    del volume_list[update_lb_ip_v_index]

                if k != self.oxd_server_yaml and self.settings["PERSISTENCE_BACKEND"] == "ldap":
                    couchbase_password_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "cb-pass"), None)
                    del volume_list[couchbase_password_v_index]
                    couchbase_crt_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "cb-crt"), None)
                    del volume_list[couchbase_crt_v_index]

                    couchbase_password_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "cb-pass"), None)
                    del volume_mount_list[couchbase_password_vm_index]
                    couchbase_crt_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "cb-crt"), None)
                    del volume_mount_list[couchbase_crt_vm_index]

                parser.dump_it()

        else:
            for k, v in self.adjust_yamls_for_fqdn_status.items():
                # oxAuth
                cm_parser = Parser(k, "ConfigMap")
                cm_parser["data"]["LB_ADDR"] = self.settings["LB_ADD"]
                cm_parser.dump_it()

                parser = Parser(k, v)
                # Check Couchbase entries
                if k != self.oxd_server_yaml and self.settings["PERSISTENCE_BACKEND"] == "ldap":
                    volume_mount_list = parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
                    volume_list = parser["spec"]["template"]["spec"]["volumes"]

                    couchbase_password_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "cb-pass"), None)
                    del volume_list[couchbase_password_v_index]
                    couchbase_crt_v_index = next(
                        (index for (index, d) in enumerate(volume_list) if d["name"] == "cb-crt"), None)
                    del volume_list[couchbase_crt_v_index]

                    couchbase_password_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "cb-pass"), None)
                    del volume_mount_list[couchbase_password_vm_index]
                    couchbase_crt_vm_index = next(
                        (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "cb-crt"), None)
                    del volume_mount_list[couchbase_crt_vm_index]

                if k != self.key_rotate_yaml and k != self.cr_rotate_yaml:
                    parser["spec"]["template"]["spec"]["containers"][0]["command"] = \
                        ['/bin/sh', '-c', '/usr/bin/python /scripts/update-lb-ip.py & \n/app/scripts/entrypoint.sh\n']
                    volume_mount_list = parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
                    parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"][len(volume_mount_list) - 1] = \
                        dict([('mountPath', '/scripts'), ('name', 'update-lb-ip')])
                    parser["spec"]["template"]["spec"]["hostAliases"][0]["hostnames"] = [self.settings["GLUU_FQDN"]]
                    parser["spec"]["template"]["spec"]["hostAliases"][0]["ip"] = self.settings["HOST_EXT_IP"]
                parser.dump_it()

    def update_kustomization_yaml(self):
        def update_image_name_tag(image_name_key, image_tag_key):
            parser["images"][0]["name"] = self.settings[image_name_key]
            parser["images"][0]["newTag"] = self.settings[image_tag_key]

        app_kustomization_yamls = ["./casa/base", "./config/base", "./cr-rotate/base", "./key-rotation/base",
                                   "./ldap/base", "./oxauth/base", "./oxd-server/base", "./oxpassport/base",
                                   "./oxshibboleth/base", "./oxtrust/base", "./persistence/base", "./radius/base"]
        other_kustomization_yamls = ["./update-lb-ip/base", "./shared-shib/efs", "./shared-shib/localstorage",
                                     "./shared-shib/nfs"]
        all_kustomization_yamls = app_kustomization_yamls + other_kustomization_yamls
        for yaml in all_kustomization_yamls:
            kustomization_yaml = yaml + "/kustomization.yaml"
            parser = Parser(kustomization_yaml, "Kustomization")
            parser["namespace"] = self.settings["GLUU_NAMESPACE"]
            if yaml in app_kustomization_yamls:
                if "casa" in yaml:
                    update_image_name_tag("CASA_IMAGE_NAME", "CASA_IMAGE_TAG")
                elif "config" in yaml:
                    update_image_name_tag("CONFIG_IMAGE_NAME", "CONFIG_IMAGE_TAG")
                elif "cr-rotate" in yaml:
                    update_image_name_tag("CACHE_REFRESH_ROTATE_IMAGE_NAME", "CACHE_REFRESH_ROTATE_IMAGE_TAG")
                elif "key-rotation" in yaml:
                    update_image_name_tag("KEY_ROTATE_IMAGE_NAME", "KEY_ROTATE_IMAGE_TAG")
                elif "ldap" in yaml:
                    update_image_name_tag("LDAP_IMAGE_NAME", "LDAP_IMAGE_TAG")
                elif "oxauth" in yaml:
                    update_image_name_tag("OXAUTH_IMAGE_NAME", "OXAUTH_IMAGE_TAG")
                elif "oxd-server" in yaml:
                    update_image_name_tag("OXD_IMAGE_NAME", "OXD_IMAGE_TAG")
                elif "oxpassport" in yaml:
                    update_image_name_tag("OXPASSPORT_IMAGE_NAME", "OXPASSPORT_IMAGE_TAG")
                elif "oxshibboleth" in yaml:
                    update_image_name_tag("OXSHIBBOLETH_IMAGE_NAME", "OXSHIBBOLETH_IMAGE_TAG")
                elif "oxtrust" in yaml:
                    update_image_name_tag("OXTRUST_IMAGE_NAME", "OXTRUST_IMAGE_TAG")
                elif "persistence" in yaml:
                    update_image_name_tag("PERSISTENCE_IMAGE_NAME", "PERSISTENCE_IMAGE_TAG")
                elif "radius" in yaml:
                    update_image_name_tag("RADIUS_IMAGE_NAME", "RADIUS_IMAGE_TAG")
            parser.dump_it()

    def setup_tls(self):
        while True:
            try:
                ssl_cert = self.kubernetes.read_namespaced_secret("gluu",
                                                                  self.settings["GLUU_NAMESPACE"]).data["ssl_cert"]
                ssl_key = self.kubernetes.read_namespaced_secret("gluu",
                                                                 self.settings["GLUU_NAMESPACE"]).data["ssl_key"]
                break
            except Exception:
                logger.info("Waiting for Gluu secret...")
                time.sleep(10)

        self.kubernetes.create_namespaced_secret_from_literal(name="tls-certificate",
                                                              namespace=self.settings["GLUU_NAMESPACE"],
                                                              literal="tls.crt",
                                                              value_of_literal=ssl_cert,
                                                              secret_type="kubernetes.io/tls",
                                                              second_literal="tls.key",
                                                              value_of_second_literal=ssl_key)

    def kustomize_shared_shib(self):
        if self.settings["DEPLOYMENT_ARCH"] == "eks" and self.settings["OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE"] == "efs":
            command = self.kubectl + " kustomize shared-shib/efs > " + self.shared_shib_yaml
            subprocess_cmd(command)

        elif self.settings["DEPLOYMENT_ARCH"] == "gke" or self.settings["DEPLOYMENT_ARCH"] == "aks":
            command = self.kubectl + " kustomize shared-shib/nfs > " + self.shared_shib_yaml
            subprocess_cmd(command)

            nfs_pvc_parser = Parser(self.shared_shib_yaml, "PersistentVolumeClaim", "nfs-pvc")
            nfs_pvc_parser["spec"]["resources"]["requests"]["storage"] = self.settings["NFS_STORAGE_SIZE"]
            nfs_pvc_parser.dump_it()

        else:
            command = self.kubectl + " kustomize shared-shib/localstorage > " + self.shared_shib_yaml
            subprocess_cmd(command)

        shared_shib_pv_parser = Parser(self.shared_shib_yaml, "PersistentVolume", "shared-shib-pv")
        shared_shib_pv_parser["spec"]["capacity"]["storage"] = self.settings["OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE"]
        shared_shib_pv_parser.dump_it()

        shared_shib_pvc_parser = Parser(self.shared_shib_yaml, "PersistentVolumeClaim", "shared-shib-pvc")
        shared_shib_pvc_parser["spec"]["resources"]["requests"]["storage"] = self.settings[
            "OXTRUST_OXSHIBBOLETH_SHARED_STORAGE_SIZE"]
        shared_shib_pvc_parser.dump_it()

    def kustomize_config(self):
        config_kustmoization_yaml = Path("./config/base/kustomization.yaml")
        parser = Parser(config_kustmoization_yaml, "Kustomization")
        list_of_config_resource_files = parser["resources"]
        if self.settings["DEPLOYMENT_ARCH"] == "gke":
            if "cluster-role-bindings.yaml" not in list_of_config_resource_files:
                list_of_config_resource_files.append("cluster-role-bindings.yaml")
        else:
            if "cluster-role-bindings.yaml" in list_of_config_resource_files:
                list_of_config_resource_files.remove("cluster-role-bindings.yaml")

        parser["resources"] = list_of_config_resource_files
        parser.dump_it()
        command = self.kubectl + " kustomize config/base > " + self.config_yaml
        subprocess_cmd(command)

        comfig_cm_parser = Parser(self.config_yaml, "ConfigMap", "config-cm")
        comfig_cm_parser["data"]["GLUU_CACHE_TYPE"] = self.settings["GLUU_CACHE_TYPE"]
        comfig_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
        comfig_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
        comfig_cm_parser.dump_it()

    def kustomize_ldap(self):
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            command = self.kubectl + " kustomize " + str(
                self.kustomize_yaml_directory.resolve()) + " > " + self.ldap_yaml
            subprocess_cmd(command)

            ldap_cm_parser = Parser(self.ldap_yaml, "ConfigMap")
            ldap_cm_parser["data"]["GLUU_CACHE_TYPE"] = self.settings["GLUU_CACHE_TYPE"]
            ldap_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
            ldap_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
            ldap_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            ldap_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            ldap_cm_parser.dump_it()

            ldap_statefulset_parser = Parser(self.ldap_yaml, "StatefulSet")
            ldap_statefulset_parser["spec"]["volumeClaimTemplates"][0]["spec"]["resources"]["requests"]["storage"] \
                = self.settings["LDAP_STORAGE_SIZE"]
            ldap_statefulset_parser.dump_it()

            if self.settings["LDAP_VOLUME_TYPE"] != 7 and self.settings["LDAP_VOLUME_TYPE"] != 12 and self.settings[
                "LDAP_VOLUME_TYPE"] != 17:
                ldap_pv_parser = Parser(self.ldap_yaml, "PersistentVolume")
                ldap_pv_parser["spec"]["capacity"]["storage"] = self.settings["LDAP_STORAGE_SIZE"]
                if self.settings["LDAP_VOLUME_TYPE"] == 11:
                    ldap_pv_parser["spec"]["hostPath"]["path"] = self.settings["GOOGLE_NODE_HOME_DIR"] + "/opendj"
                ldap_pv_parser.dump_it()

    def kustomize_persistence(self):
        command = self.kubectl + " kustomize persistence/base > " + self.persistence_yaml
        subprocess_cmd(command)

        persistence_cm_parser = Parser(self.persistence_yaml, "ConfigMap")
        persistence_cm_parser["data"]["DOMAIN"] = self.settings["GLUU_FQDN"]
        persistence_cm_parser["data"]["GLUU_CACHE_TYPE"] = self.settings["GLUU_CACHE_TYPE"]
        persistence_cm_parser["data"]["GLUU_CASA_ENABLED"] = self.settings["ENABLE_CASA_BOOLEAN"]
        persistence_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
        persistence_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
        persistence_cm_parser["data"]["GLUU_OXTRUST_API_ENABLED"] = self.settings["ENABLE_OXTRUST_API_BOOLEAN"]
        persistence_cm_parser["data"]["GLUU_OXTRUST_API_TEST_MODE"] = self.settings["ENABLE_OXTRUST_TEST_MODE_BOOLEAN"]
        persistence_cm_parser["data"]["GLUU_PASSPORT_ENABLED"] = self.settings["ENABLE_OXPASSPORT_BOOLEAN"]
        persistence_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
        persistence_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
        persistence_cm_parser["data"]["GLUU_RADIUS_ENABLED"] = self.settings["ENABLE_RADIUS_BOOLEAN"]
        persistence_cm_parser["data"]["GLUU_SAML_ENABLED"] = self.settings["ENABLE_SAML_BOOLEAN"]
        persistence_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
        persistence_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
        persistence_cm_parser.dump_it()

        if self.settings["PERSISTENCE_BACKEND"] == "ldap":
            persistence_job_parser = Parser(self.persistence_yaml, "Job")
            del persistence_job_parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
            del persistence_job_parser["spec"]["template"]["spec"]["volumes"]
            persistence_job_parser.dump_it()

    def kustomize_oxauth(self):
        command = self.kubectl + " kustomize oxauth/base > " + self.oxauth_yaml
        subprocess_cmd(command)

        oxauth_cm_parser = Parser(self.oxauth_yaml, "ConfigMap")
        oxauth_cm_parser["data"]["DOMAIN"] = self.settings["GLUU_FQDN"]
        oxauth_cm_parser["data"]["GLUU_CACHE_TYPE"] = self.settings["GLUU_CACHE_TYPE"]
        oxauth_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
        oxauth_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
        oxauth_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
        oxauth_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
        oxauth_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
        oxauth_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
        oxauth_cm_parser.dump_it()

        self.adjust_yamls_for_fqdn_status[self.oxauth_yaml] = "Deployment"

    def kustomize_oxtrust(self):
        command = self.kubectl + " kustomize oxtrust/base > " + self.oxtrust_yaml
        subprocess_cmd(command)
        oxtrust_cm_parser = Parser(self.oxtrust_yaml, "ConfigMap")
        oxtrust_cm_parser["data"]["DOMAIN"] = self.settings["GLUU_FQDN"]
        oxtrust_cm_parser["data"]["GLUU_CACHE_TYPE"] = self.settings["GLUU_CACHE_TYPE"]
        oxtrust_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
        oxtrust_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
        oxtrust_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
        oxtrust_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
        oxtrust_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
        oxtrust_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
        oxtrust_cm_parser.dump_it()

        self.adjust_yamls_for_fqdn_status[self.oxtrust_yaml] = "StatefulSet"

        if self.settings["ENABLE_OXSHIBBOLETH"] != "Y" or self.settings["ENABLE_OXSHIBBOLETH"] != "y":
            oxtrust_statefulset_parser = Parser(self.oxtrust_yaml, "StatefulSet")
            volume_mount_list = oxtrust_statefulset_parser["spec"]["template"]["spec"]["containers"][0]["volumeMounts"]
            volume_list = oxtrust_statefulset_parser["spec"]["template"]["spec"]["volumes"]
            shared_shib_vm_index = next(
                (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "shared-shib"), None)
            shared_shib_v_index = next(
                (index for (index, d) in enumerate(volume_mount_list) if d["name"] == "shared-shib"), None)
            del volume_mount_list[shared_shib_vm_index]
            del volume_list[shared_shib_v_index]
            oxtrust_statefulset_parser.dump_it()

    def kustomize_oxshibboleth(self):
        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            command = self.kubectl + " kustomize oxshibboleth/base > " + self.oxshibboleth_yaml
            subprocess_cmd(command)

            oxshibboleth_cm_parser = Parser(self.oxshibboleth_yaml, "ConfigMap")
            oxshibboleth_cm_parser["data"]["DOMAIN"] = self.settings["GLUU_FQDN"]
            oxshibboleth_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
            oxshibboleth_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
            oxshibboleth_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
            oxshibboleth_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
            oxshibboleth_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            oxshibboleth_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            oxshibboleth_cm_parser.dump_it()

            self.adjust_yamls_for_fqdn_status[self.oxshibboleth_yaml] = "StatefulSet"

    def kustomize_oxpassport(self):
        if self.settings["ENABLE_OXPASSPORT"] == "Y":
            command = self.kubectl + " kustomize oxpassport/base > " + self.oxpassport_yaml
            subprocess_cmd(command)

            oxpassport_cm_parser = Parser(self.oxpassport_yaml, "ConfigMap")
            oxpassport_cm_parser["data"]["DOMAIN"] = self.settings["GLUU_FQDN"]
            oxpassport_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
            oxpassport_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
            oxpassport_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
            oxpassport_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
            oxpassport_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            oxpassport_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            oxpassport_cm_parser.dump_it()

            self.adjust_yamls_for_fqdn_status[self.oxpassport_yaml] = "Deployment"

    def kustomize_key_rotation(self):
        if self.settings["ENABLE_KEY_ROTATE"] == "Y":
            command = self.kubectl + " kustomize key-rotation/base > " + self.key_rotate_yaml
            subprocess_cmd(command)

            key_rotate_cm_parser = Parser(self.key_rotate_yaml, "ConfigMap")
            key_rotate_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
            key_rotate_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
            key_rotate_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
            key_rotate_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
            key_rotate_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            key_rotate_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            key_rotate_cm_parser.dump_it()

            self.adjust_yamls_for_fqdn_status[self.key_rotate_yaml] = "Deployment"

    def kustomize_cr_rotate(self):
        if self.settings["ENABLE_CACHE_REFRESH"] == "Y":
            command = self.kubectl + " kustomize cr-rotate/base > " + self.cr_rotate_yaml
            subprocess_cmd(command)

            cr_rotate_cm_parser = Parser(self.cr_rotate_yaml, "ConfigMap")
            cr_rotate_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
            cr_rotate_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
            cr_rotate_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
            cr_rotate_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
            cr_rotate_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            cr_rotate_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            cr_rotate_cm_parser.dump_it()

            self.adjust_yamls_for_fqdn_status[self.cr_rotate_yaml] = "DaemonSet"

    def kustomize_oxd_server(self):
        if self.settings["ENABLE_OXD"] == "Y":
            command = self.kubectl + " kustomize oxd-server/base > " + self.oxd_server_yaml
            subprocess_cmd(command)

            oxd_server_cm_parser = Parser(self.oxd_server_yaml, "ConfigMap")
            oxd_server_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
            oxd_server_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
            oxd_server_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
            oxd_server_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
            oxd_server_cm_parser["data"]["ADMIN_KEYSTORE_PASSWORD"] = self.settings["OXD_SERVER_PW"]
            oxd_server_cm_parser["data"]["APPLICATION_KEYSTORE_PASSWORD"] = self.settings["OXD_SERVER_PW"]
            oxd_server_cm_parser["data"]["APPLICATION_KEYSTORE_CN"] = self.settings["OXD_APPLICATION_KEYSTORE_CN"]
            oxd_server_cm_parser["data"]["ADMIN_KEYSTORE_CN"] = self.settings["OXD_ADMIN_KEYSTORE_CN"]
            oxd_server_cm_parser["data"]["GLUU_SERVER_HOST"] = self.settings["GLUU_FQDN"]
            oxd_server_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            oxd_server_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            oxd_server_cm_parser.dump_it()

            self.adjust_yamls_for_fqdn_status[self.oxd_server_yaml] = "Deployment"

    def kustomize_casa(self):
        if self.settings["ENABLE_CASA"] == "Y":
            command = self.kubectl + " kustomize casa/base > " + self.casa_yaml
            subprocess_cmd(command)

            casa_cm_parser = Parser(self.casa_yaml, "ConfigMap")
            casa_cm_parser["data"]["DOMAIN"] = self.settings["GLUU_FQDN"]
            casa_cm_parser["data"]["GLUU_CACHE_TYPE"] = self.settings["GLUU_CACHE_TYPE"]
            casa_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
            casa_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
            casa_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
            casa_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
            casa_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            casa_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]

            casa_cm_parser.dump_it()

            self.adjust_yamls_for_fqdn_status[self.casa_yaml] = "Deployment"

    def kustomize_radius(self):
        if self.settings["ENABLE_RADIUS"] == "Y":
            command = self.kubectl + " kustomize radius/base > " + self.radius_yaml
            subprocess_cmd(command)

            radius_cm_parser = Parser(self.radius_yaml, "ConfigMap")
            radius_cm_parser["data"]["DOMAIN"] = self.settings["GLUU_FQDN"]
            radius_cm_parser["data"]["GLUU_CACHE_TYPE"] = self.settings["GLUU_CACHE_TYPE"]
            radius_cm_parser["data"]["GLUU_COUCHBASE_URL"] = self.settings["COUCHBASE_URL"]
            radius_cm_parser["data"]["GLUU_COUCHBASE_USER"] = self.settings["COUCHBASE_USER"]
            radius_cm_parser["data"]["GLUU_PERSISTENCE_LDAP_MAPPING"] = self.settings["HYBRID_LDAP_HELD_DATA"]
            radius_cm_parser["data"]["GLUU_PERSISTENCE_TYPE"] = self.settings["PERSISTENCE_BACKEND"]
            radius_cm_parser["data"]["GLUU_CONFIG_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            radius_cm_parser["data"]["GLUU_SECRET_KUBERNETES_NAMESPACE"] = self.settings["GLUU_NAMESPACE"]
            radius_cm_parser.dump_it()

            self.adjust_yamls_for_fqdn_status[self.radius_yaml] = "Deployment"

    def kustomize_redis(self):
        if self.settings["GLUU_CACHE_TYPE"] == "REDIS":
            command = self.kubectl + " kustomize redis/base > " + self.redis_yaml
            subprocess_cmd(command)

    def kustomize_update_lb_ip(self):
        if self.settings["IS_GLUU_FQDN_REGISTERED"] != "Y" or self.settings["IS_GLUU_FQDN_REGISTERED"] != "y":
            if self.settings["DEPLOYMENT_ARCH"] == "eks":
                command = self.kubectl + " kustomize update-lb-ip/base > " + self.update_lb_ip_yaml
                subprocess_cmd(command)

    def deploy_nginx(self):
        copy(Path("./nginx"), self.output_yaml_directory.joinpath("nginx"))
        if self.settings["DEPLOYMENT_ARCH"] == "minikube":
            subprocess_cmd("minikube addons enable ingress")
        self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("nginx/mandatory.yaml"))
        if self.settings["DEPLOYMENT_ARCH"] == "eks":
            lb_hostname = None
            if self.settings["AWS_LB_TYPE"] == "nlb":
                self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("nginx/nlb-service.yaml"))
                while True:
                    try:
                        lb_hostname = self.kubernetes.read_namespaced_service(name="ingress-nginx",
                                                                              namespace="ingress-nginx").status.load_balancer.ingress[
                            0].hostname
                        ip_static = socket.gethostbyname(str(lb_hostname))
                        if ip_static:
                            break
                    except TypeError:
                        logger.info("Waiting for LB to recieve an ip assignment from AWS")
                    time.sleep(10)
            else:
                if self.settings["USE_ARN"] == "Y":
                    svc_l7_yaml = self.output_yaml_directory.joinpath("nginx/service-l7.yaml")
                    svc_l7_yaml_parser = Parser(svc_l7_yaml, "Service")
                    svc_l7_yaml_parser["metadata"]["annotations"][
                        "service.beta.kubernetes.io/aws-load-balancer-ssl-cert"] = self.settings["ARN_AWS_IAM"]
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

            while True:
                try:
                    if lb_hostname:
                        break
                    lb_hostname = self.kubernetes.read_namespaced_service(name="ingress-nginx",
                                                                          namespace="ingress-nginx").status.load_balancer.ingress[
                        0].hostname
                except TypeError:
                    logger.info("Waiting for loadbalancer address..")
                    time.sleep(10)
            self.settings["LB_ADD"] = lb_hostname

        if self.settings["DEPLOYMENT_ARCH"] == "gke" or self.settings["DEPLOYMENT_ARCH"] == "aks":
            self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("nginx/cloud-generic.yaml"))
            ip = None
            while True:
                try:
                    if ip:
                        break
                    ip = self.kubernetes.read_namespaced_service(
                        name="ingress-nginx", namespace="ingress-nginx").status.load_balancer.ingress[0].ip
                except TypeError:
                    logger.info("Waiting for the ip of the Loadbalancer")
                    time.sleep(10)
            logger.info(ip)
            self.settings["HOST_EXT_IP"] = ip

        ingress_name_list = ["gluu-ingress-base", "gluu-ingress-openid-configuration",
                             "gluu-ingress-uma2-configuration", "gluu-ingress-webfinger",
                             "gluu-ingress-simple-web-discovery", "gluu-ingress-scim-configuration",
                             "gluu-ingress-fido-u2f-configuration", "gluu-ingress", "gluu-ingress-stateful",
                             "gluu-casa"]

        for ingress_name in ingress_name_list:
            yaml = self.output_yaml_directory.joinpath("nginx/nginx.yaml")
            parser = Parser(yaml, "Ingress", ingress_name)
            parser["spec"]["tls"][0]["hosts"][0] = self.settings["GLUU_FQDN"]
            parser["spec"]["rules"][0]["host"] = self.settings["GLUU_FQDN"]
            parser.dump_it()

        self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("nginx/nginx.yaml"),
                                                 self.settings["GLUU_NAMESPACE"])

    def deploy_redis(self):
        self.kubernetes.create_objects_from_dict(self.redis_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=redis")

    def deploy_config(self):
        self.kubernetes.create_objects_from_dict(self.config_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=config-init-load")

    def deploy_ldap(self):
        self.kubernetes.create_objects_from_dict(self.ldap_yaml)
        logger.info("Deploying LDAP.Please wait..")
        time.sleep(10)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=opendj")

    def deploy_persistence(self):
        self.kubernetes.create_objects_from_dict(self.persistence_yaml)
        logger.info("Trying to import ldifs...")
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=persistence-load")
        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            self.kubernetes.patch_namespaced_stateful_set_scale(name="opendj",
                                                                replicas=self.settings["LDAP_REPLICAS"],
                                                                namespace=self.settings["GLUU_NAMESPACE"])
            self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=opendj")

    def deploy_nfs(self):
        self.kubernetes.create_objects_from_dict("shared-shib/nfs/services.yaml")
        nfs_ip = None
        while True:
            if nfs_ip:
                break
            nfs_ip = self.kubernetes.read_namespaced_service(name="nfs-server").spec.cluster_ip
            time.sleep(10)

        shared_shib_pv_parser = Parser(self.shared_shib_yaml, "PersistentVolume", "shared-shib-pv")
        shared_shib_pv_parser["spec"]["nfs"]["server"] = nfs_ip
        shared_shib_pv_parser.dump_it()

        self.kubernetes.create_objects_from_dict(self.shared_shib_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "nfs-server")

        exec_command_shared_shib = ["mkdir", "-p", "/exports/opt/shared-shibboleth-idp"]

        self.kubernetes.connect_get_namespaced_pod_exec(exec_command=exec_command_shared_shib, label="app=nfs-server")

    def deploy_efs(self):
        efs_deploy_parser = Parser(self.shared_shib_yaml, "Deployment")
        efs_env_list = efs_deploy_parser["spec"]["template"]["spec"]["containers"][0]["env"]
        for env in efs_env_list:
            if env["name"] == "FILE_SYSTEM_ID":
                env["value"] = self.settings["EFS_FILE_SYSTEM_ID"]
            elif env["name"] == "AWS_REGION":
                env["value"] = self.settings["EFS_AWS_REGION"]

            # Check to makre sure this DNS Name is also changed when using efs
            # elif env["name"] == "DNS_NAME":
            #    env["value"] = self.settings["EFS_DNS"]

        efs_deploy_parser["spec"]["template"]["spec"]["volumes"][0]["nfs"]["server"] = self.settings["EFS_DNS"]
        self.kubernetes.create_objects_from_dict(self.shared_shib_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=efs-provisioner")
        efs_deploy_parser.dump_it()

    def deploy_shared_shib(self):
        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            if self.settings["DEPLOYMENT_ARCH"] == "gke" or self.settings["DEPLOYMENT_ARCH"] == "aks":
                self.deploy_nfs()
            elif self.settings["DEPLOYMENT_ARCH"] == "eks" and self.settings[
                "OXTRUST_OXSHIBBOLETH_SHARED_VOLUME_TYPE"] == "efs":
                self.deploy_efs()
            else:
                self.kubernetes.create_objects_from_dict(self.shared_shib_yaml)

    def deploy_update_lb_ip(self):
        self.kubernetes.create_objects_from_dict(self.update_lb_ip_yaml)

    def deploy_oxauth(self):
        self.kubernetes.create_objects_from_dict(self.oxauth_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=oxauth")
        self.kubernetes.patch_namespaced_deployment_scale(name="oxauth", replicas=self.settings["OXAUTH_REPLICAS"],
                                                          namespace=self.settings["GLUU_NAMESPACE"])

    def deploy_oxd(self):
        self.kubernetes.create_objects_from_dict(self.oxd_server_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=oxd-server")
        self.kubernetes.patch_namespaced_deployment_scale(name="oxd-server",
                                                          replicas=self.settings["OXD_SERVER_REPLICAS"],
                                                          namespace=self.settings["GLUU_NAMESPACE"])

    def deploy_casa(self):
        self.kubernetes.create_objects_from_dict(self.casa_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=casa")
        self.kubernetes.patch_namespaced_deployment_scale(name="casa", replicas=self.settings["CASA_REPLICAS"],
                                                          namespace=self.settings["GLUU_NAMESPACE"])

    def deploy_oxtrust(self):
        self.kubernetes.create_objects_from_dict(self.oxtrust_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=oxtrust")
        self.kubernetes.patch_namespaced_stateful_set_scale(name="oxtrust", replicas=self.settings["OXTRUST_REPLICAS"],
                                                            namespace=self.settings["GLUU_NAMESPACE"])

    def deploy_oxshibboleth(self):
        self.kubernetes.create_objects_from_dict(self.oxshibboleth_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=oxshibboleth")
        self.kubernetes.patch_namespaced_stateful_set_scale(name="oxshibboleth",
                                                            replicas=self.settings["OXSHIBBOLETH_REPLICAS"],
                                                            namespace=self.settings["GLUU_NAMESPACE"])

    def deploy_oxpassport(self):
        self.kubernetes.create_objects_from_dict(self.oxpassport_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=oxpassport")
        self.kubernetes.patch_namespaced_deployment_scale(name="oxpassport",
                                                          replicas=self.settings["OXPASSPORT_REPLICAS"],
                                                          namespace=self.settings["GLUU_NAMESPACE"])

    def deploy_key_rotation(self):
        self.kubernetes.create_objects_from_dict(self.key_rotate_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=key-rotation")

    def deploy_radius(self):
        self.kubernetes.create_objects_from_dict(self.radius_yaml)
        self.kubernetes.check_pods_statuses(self.settings["GLUU_NAMESPACE"], "app=radius")
        self.kubernetes.patch_namespaced_deployment_scale(name="radius", replicas=self.settings["RADIUS_REPLICAS"],
                                                          namespace=self.settings["GLUU_NAMESPACE"])

    def deploy_cr_rotate(self):
        self.kubernetes.delete_role("gluu-role", self.settings["GLUU_NAMESPACE"])
        self.kubernetes.delete_role_binding("gluu-rolebinding", self.settings["GLUU_NAMESPACE"])
        self.kubernetes.delete_cluster_role_binding("gluu-rolebinding")
        time.sleep(10)
        self.kubernetes.create_objects_from_dict(self.cr_rotate_yaml)

    def install(self, install_couchbase=True):
        self.update_kustomization_yaml()
        self.kubernetes.create_namespace(name=self.settings["GLUU_NAMESPACE"])
        self.kustomize_shared_shib()
        self.kustomize_config()
        self.kustomize_ldap()
        self.kustomize_persistence()
        self.kustomize_oxauth()
        self.kustomize_oxtrust()
        self.kustomize_oxshibboleth()
        self.kustomize_oxpassport()
        self.kustomize_key_rotation()
        self.kustomize_cr_rotate()
        self.kustomize_oxd_server()
        self.kustomize_casa()
        self.kustomize_radius()
        self.kustomize_redis()
        self.kustomize_update_lb_ip()
        if install_couchbase:
            if self.settings["PERSISTENCE_BACKEND"] != "ldap" and self.settings["INSTALL_COUCHBASE"] == "Y":
                couchbase_app = Couchbase(self.settings)
                couchbase_app.uninstall()
                couchbase_app = Couchbase(self.settings)
                couchbase_app.install()

        self.deploy_shared_shib()

        if self.settings["DEPLOY_MULTI_CLUSTER"] != "Y" and self.settings["DEPLOY_MULTI_CLUSTER"] != "y":
            self.deploy_config()

        self.setup_tls()

        if self.settings["GLUU_CACHE_TYPE"] == "REDIS":
            self.deploy_redis()

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            self.deploy_ldap()

        self.deploy_nginx()
        self.adjust_fqdn_yaml_entries()
        self.deploy_persistence()

        if self.settings["IS_GLUU_FQDN_REGISTERED"] != "Y" and self.settings["IS_GLUU_FQDN_REGISTERED"] != "y":
            if self.settings["DEPLOYMENT_ARCH"] == "eks":
                self.deploy_update_lb_ip()

        self.deploy_oxauth()
        if self.settings["ENABLE_OXD"] == "Y":
            self.deploy_oxd()

        if self.settings["ENABLE_CASA"] == "Y":
            self.deploy_casa()

        self.deploy_oxtrust()

        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            self.deploy_oxshibboleth()

        if self.settings["ENABLE_OXPASSPORT"] == "Y":
            self.deploy_oxpassport()

        if self.settings["ENABLE_CACHE_REFRESH"] == "Y":
            self.deploy_cr_rotate()

        if self.settings["ENABLE_KEY_ROTATE"] == "Y":
            self.deploy_key_rotation()

        if self.settings["ENABLE_RADIUS"] == "Y":
            self.deploy_radius()

        # storage_class_file_parser = Parser(self.storage_class_file, "StorageClass")

    def uninstall(self):
        gluu_service_names = ["casa", "cr-rotate", "key-rotation", "opendj", "oxauth", "oxpassport",
                              "oxshibboleth", "oxtrust", "radius", "oxd-server", "nfs-server"]
        gluu_storage_class_names = ["aws-efs", "opendj-sc"]
        nginx_service_name = "ingress-nginx"
        gluu_deployment_app_labels = ["app=casa", "app=oxauth", "app=oxd-server", "app=oxpassport",
                                      "app=radius", "app=redis", "app=efs-provisioner", "app=key-rotation"]
        nginx_deployemnt_app_name = "nginx-ingress-controller"
        stateful_set_labels = ["app=opendj", "app=oxtrust", "app=oxshibboleth"]
        jobs_labels = ["app=config-init-load", "app=persistence-load"]
        secrets = ["oxdkeystorecm", "gluu", "tls-certificate", "cb-pass", "cb-crt"]
        daemon_set_label = "app=cr-rotate"
        replication_controller_label = "app=nfs-server"
        shared_shib_label = "app=shared-shib"
        all_labels = gluu_deployment_app_labels + stateful_set_labels + jobs_labels + [daemon_set_label] \
                     + [replication_controller_label] + [shared_shib_label]
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
                                          "gluu-ingress-stateful", "gluu-casa"]
        minkube_yamls_folder = Path("./gluuminikubeyamls")
        microk8s_yamls_folder = Path("./gluumicrok8yamls")
        eks_yamls_folder = Path("./gluueksyamls")
        gke_yamls_folder = Path("./gluugkeyamls")
        aks_yamls_folder = Path("./gluuaksyamls")
        for service in gluu_service_names:
            self.kubernetes.delete_service(service, self.settings["GLUU_NAMESPACE"])
        self.kubernetes.delete_service(nginx_service_name, "ingress-nginx")
        self.kubernetes.delete_service(nginx_service_name, "ingress-nginx")
        for deployment in gluu_deployment_app_labels:
            self.kubernetes.delete_deployment_using_label(self.settings["GLUU_NAMESPACE"], deployment)
        self.kubernetes.delete_deployment_using_name(nginx_deployemnt_app_name, "ingress-nginx")
        for stateful_set in stateful_set_labels:
            self.kubernetes.delete_stateful_set(self.settings["GLUU_NAMESPACE"], stateful_set)
        for job in jobs_labels:
            self.kubernetes.delete_job(self.settings["GLUU_NAMESPACE"], job)
        for secret in secrets:
            self.kubernetes.delete_secret(secret, self.settings["GLUU_NAMESPACE"])
        self.kubernetes.delete_daemon_set(self.settings["GLUU_NAMESPACE"], daemon_set_label)
        self.kubernetes.delete_collection_namespaced_replication_controller(self.settings["GLUU_NAMESPACE"],
                                                                            replication_controller_label)
        for config_map in gluu_config_maps_names:
            self.kubernetes.delete_config_map_using_name(config_map, self.settings["GLUU_NAMESPACE"])
        for config_map in nginx_config_maps_names:
            self.kubernetes.delete_config_map_using_name(config_map, "ingress-nginx")
        for cm_pv_pvc in all_labels:
            self.kubernetes.delete_config_map_using_label(self.settings["GLUU_NAMESPACE"], cm_pv_pvc)
            self.kubernetes.delete_persistent_volume(cm_pv_pvc)
            self.kubernetes.delete_persistent_volume_claim(self.settings["GLUU_NAMESPACE"], cm_pv_pvc)
        for storage_class in gluu_storage_class_names:
            self.kubernetes.delete_storage_class(storage_class)

        self.kubernetes.delete_role("gluu-role", self.settings["GLUU_NAMESPACE"])
        self.kubernetes.delete_role_binding("gluu-rolebinding", self.settings["GLUU_NAMESPACE"])
        self.kubernetes.delete_role(nginx_roles_name, "ingress-nginx")
        self.kubernetes.delete_cluster_role_binding("gluu-rolebinding")
        self.kubernetes.delete_role_binding(nginx_role_bindings_name, "ingress-nginx")
        self.kubernetes.delete_cluster_role_binding(gluu_cluster_role_bindings_name)
        self.kubernetes.delete_cluster_role_binding(nginx_cluster_role_bindings_name)
        self.kubernetes.delete_service_account(nginx_service_account_name, "ingress-nginx")
        self.kubernetes.delete_cluster_role(nginx_cluster_role_name)
        for extension in nginx_ingress_extensions_names:
            self.kubernetes.delete_ingress(extension)
        with contextlib.suppress(FileNotFoundError):
            os.remove("oxd-server.keystore")
        with contextlib.suppress(FileNotFoundError):
            os.remove("easyrsa_ca_password")
        if minkube_yamls_folder.exists() or microk8s_yamls_folder.exists():
            shutil.rmtree('/data', ignore_errors=True)
        else:
            for node_ip in self.settings["NODES_IPS"]:
                if self.settings["DEPLOYMENT_ARCH"] == "minikube":
                    subprocess_cmd("minikube ssh 'sudo rm -rf /data'")
                elif self.settings["DEPLOYMENT_ARCH"] == "microk8s":
                    shutil.rmtree('/data', ignore_errors=True)
                else:
                    if self.settings["LDAP_VOLUME_TYPE"] == 6 or self.settings["LDAP_VOLUME_TYPE"] == 11 or \
                            self.settings["LDAP_VOLUME_TYPE"] == 16:
                        if self.settings["DEPLOYMENT_ARCH"] == "eks":
                            ssh_and_remove(self.settings["NODE_SSH_KEY"], "ec2-user", node_ip, "/data")
                        elif self.settings["DEPLOYMENT_ARCH"] == "aks":
                            ssh_and_remove(self.settings["NODE_SSH_KEY"], "opc", node_ip, "/data")
            if self.settings["LDAP_VOLUME_TYPE"] == 6 or self.settings["LDAP_VOLUME_TYPE"] == 11 or \
                    self.settings["LDAP_VOLUME_TYPE"] == 16:
                if self.settings["DEPLOYMENT_ARCH"] == "gke":
                    for node_name in self.settings["NODES_NAMES"]:
                        for zone in self.settings["NODES_ZONES"]:
                            subprocess_cmd("gcloud compute ssh user@{} --zone={} --command='sudo rm -rf $HOME/opendj'".
                                           format(node_name, zone))
        self.kubernetes.delete_namespace("ingress-nginx")
        if not self.settings["GLUU_NAMESPACE"] == "default":
            self.kubernetes.delete_namespace(self.settings["GLUU_NAMESPACE"])
        shutil.rmtree(Path("./previousgluuminikubeyamls"), ignore_errors=True)
        shutil.rmtree(Path("./previousgluumicrok8yamls"), ignore_errors=True)
        shutil.rmtree(Path("./previousgluueksyamls"), ignore_errors=True)
        shutil.rmtree(Path("./previousgluuaksyamls"), ignore_errors=True)
        shutil.rmtree(Path("./previousgluugkeyamls"), ignore_errors=True)
        try:
            shutil.copytree(minkube_yamls_folder, Path("./previousgluuminikubeyamls"))
            shutil.copytree(microk8s_yamls_folder, Path("./previousgluumicrok8yamls"))
            shutil.copytree(eks_yamls_folder, Path("./previousgluueksyamls"))
            shutil.copytree(aks_yamls_folder, Path("./previousgluuaksyamls"))
            shutil.copytree(gke_yamls_folder, Path("./previousgluugkeyamls"))
            shutil.move(Path("./ingress.crt"), Path("./previous-ingress.crt"))
            shutil.move(Path("./ingress.key"), Path("./previous-ingress.key"))
            shutil.move(Path("./settings.json"), Path("./previous-settings.json"))
        except FileNotFoundError:
            logger.warning("Folder or file not found")


def create_parser():
    """Create parser to handle arguments from CLI.
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", dest="subparser_name")
    subparsers.add_parser("generate-settings", help="Generate settings.json to install "
                                                    "Gluu Enterprise Edition non-interactively")
    subparsers.add_parser("install", help="Install Gluu Enterprise Edition")
    subparsers.add_parser("install-gluu-only", help="Install Gluu Enterprise Edition with out installing Couchbase. "
                                                    "This assunes Couchbase is already installed")
    subparsers.add_parser("uninstall", help="Uninstall Gluu")
    subparsers.add_parser("install-couchbase", help="Install Couchbase only. Used with installation of Gluu with Helm")
    subparsers.add_parser("uninstall-couchbase", help="Uninstall Couchbase only.")
    subparsers.add_parser("helm-install", help="Install Gluu Enterprise Edition using helm. "
                                               "This also installs the nginx-ingress chart")
    subparsers.add_parser("helm-uninstall", help="Uninstall Gluu Enterprise Edition using helm. "
                                               "This also uninstalls the nginx-ingress chart")
    subparsers.add_parser("helm-install-gluu", help="Install Gluu Enterprise Edition using helm. "
                                                    "This assumes nginx-ingress is installed")
    subparsers.add_parser("helm-uninstall-gluu", help="Uninstall Gluu Enterprise Edition using helm. "
                                               "This only uninstalls Gluu")


    return parser


def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    copy_templates()
    try:
        if args.subparser_name == "install":
            app = App()
            app.uninstall()
            app.install()

        elif args.subparser_name == "install-gluu-only":
            prompts = Prompt()
            settings = prompts.prompt_couchbase()
            app = App()
            app.uninstall()
            app.install(install_couchbase=False)

        elif args.subparser_name == "uninstall":
            logger.info("Removing all Gluu resources...")
            app = App()
            app.uninstall()

        elif args.subparser_name == "install-couchbase":
            prompts = Prompt()
            settings = prompts.prompt_couchbase()
            couchbase = Couchbase(settings)
            couchbase.install()

        elif args.subparser_name == "uninstall-couchbase":
            prompts = Prompt()
            settings = prompts.prompt_couchbase()
            couchbase = Couchbase(settings)
            couchbase.uninstall()

        elif args.subparser_name == "generate-settings":
            prompts = Prompt()
            settings = prompts.check_settings_and_prompt
            logger.info("settings.json has been generated")

        elif args.subparser_name == "helm-install":
            prompts = Prompt()
            settings = prompts.check_settings_and_prompt
            settings = prompts.prompt_helm
            helm = Helm(settings)
            helm.install_gluu()

        elif args.subparser_name == "helm-uninstall":
            prompts = Prompt()
            settings = prompts.check_settings_and_prompt
            settings = prompts.prompt_helm
            helm = Helm(settings)
            helm.uninstall_gluu()
            helm.uninstall_nginx_ingress()

        elif args.subparser_name == "helm-install-gluu":
            prompts = Prompt()
            settings = prompts.check_settings_and_prompt
            settings = prompts.prompt_helm
            helm = Helm(settings)
            helm.install_gluu(install_ingress=False)

        elif args.subparser_name == "helm-uninstall-gluu":
            prompts = Prompt()
            settings = prompts.check_settings_and_prompt
            settings = prompts.prompt_helm
            helm = Helm(settings)
            helm.uninstall_gluu()

        else:
            print(parser.print_help())

    except KeyboardInterrupt:
        print("\n[I] Canceled by user; exiting ...")


if __name__ == "__main__":
    main()
