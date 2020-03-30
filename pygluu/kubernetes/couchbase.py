"""
 License terms and conditions:
 https://www.gluu.org/license/enterprise-edition/
"""

from pathlib import Path
import shutil
import tarfile
from .kubeapi import Kubernetes
from .yamlparser import Parser, get_logger, update_settings_json_file
from .pycert import check_cert_with_private_key, setup_crts
import subprocess
import sys
import base64
import random

logger = get_logger("gluu-couchbase     ")


def subprocess_cmd(command):
    """Execute command"""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout


def extract_couchbase_tar(tar_file):
    extract_folder = Path("./couchbase-source-folder")
    logger.info("Extracting {} in {} ".format(tar_file, extract_folder))
    tr = tarfile.open(tar_file)
    tr.extractall(path=extract_folder)
    tr.close()


def create_server_spec_per_cb_service(zones, number_of_cb_service_nodes, cb_service_name, mem_req, mem_limit,
                                      cpu_req, cpu_limit):
    server_spec = []
    zones = zones
    number_of_zones = len(zones)
    size = dict()
    # Create defualt size 1 for all the zones available
    for n in range(number_of_cb_service_nodes):
        random_zone_index = random.randint(0, number_of_zones - 1)
        try:
            size[zones[random_zone_index]] = size[zones[random_zone_index]] + 1
        except KeyError:
            size[zones[random_zone_index]] = 1

    for k, v in size.items():
        node_zone = k
        name = "pvc-" + cb_service_name
        if cb_service_name == "analytics":
            name = ["pvc-" + cb_service_name]
        spec = {"name": cb_service_name + "-" + node_zone, "size": v, "serverGroups": [node_zone],
                "services": [cb_service_name],
                "pod": {
                    "volumeMounts": {"default": "pvc-general", cb_service_name: name},
                    "resources": {"limits": {"cpu": str(cpu_limit) + "m", "memory": str(mem_limit) + "Mi"},
                                  "requests": {"cpu": str(cpu_req) + "m", "memory": str(mem_req) + "Mi"}}

                }}
        server_spec.append(spec)

    return server_spec

class Couchbase(object):
    def __init__(self, settings):
        self.settings = settings
        self.kubernetes = Kubernetes()
        self.storage_class_file = Path("./couchbase/storageclasses.yaml")
        self.couchbase_cluster_file = Path("./couchbase/couchbase-cluster.yaml")
        self.couchbase_source_folder_pattern, self.couchbase_source_file = self.get_couchbase_files
        self.couchbase_admission_file = self.couchbase_source_file.joinpath("admission.yaml")
        self.couchbbase_custom_resource_definition_file = self.couchbase_source_file.joinpath("crd.yaml")
        self.couchbase_operator_role_file = self.couchbase_source_file.joinpath("operator-role.yaml")
        self.couchbase_operator_deployment_file = self.couchbase_source_file.joinpath("operator-deployment.yaml")
        self.filename = ""

    @property
    def get_couchbase_files(self):
        if self.settings["INSTALL_COUCHBASE"] == "Y":
            couchbase_tar_pattern = "couchbase-autonomous-operator-kubernetes_*.tar.gz"
            directory = Path('.')
            try:
                couchbase_tar_file = list(directory.glob(couchbase_tar_pattern))[0]
            except IndexError:
                logger.fatal("Couchbase package not found.")
                logger.info("Please download the couchbase kubernetes package and place it inside the same directory "
                            "containing the create.py script.https://www.couchbase.com/downloads")
                sys.exit()
            extract_couchbase_tar(couchbase_tar_file)
            couchbase_source_folder_pattern = "./couchbase-source-folder/couchbase-autonomous-operator-kubernetes_*"
            couchbase_source_folder = list(directory.glob(couchbase_source_folder_pattern))[0]

            return couchbase_tar_file, couchbase_source_folder
        # Couchbase is installed.
        return Path("."), Path(".")

    def create_couchbase_gluu_cert_pass_secrets(self, encoded_ca_crt_string, encoded_cb_pass_string):
        # Remove this if its not needed
        self.kubernetes.patch_or_create_namespaced_secret(name="cb-crt",
                                                          namespace=self.settings["GLUU_NAMESPACE"],
                                                          literal="couchbase.crt",
                                                          value_of_literal=encoded_ca_crt_string)

        # Remove this if its not needed
        self.kubernetes.patch_or_create_namespaced_secret(name="cb-pass",
                                                          namespace=self.settings["GLUU_NAMESPACE"],
                                                          literal="couchbase_password",
                                                          value_of_literal=encoded_cb_pass_string)

    def setup_backup_couchbase(self):
        encoded_cb_pass_bytes = base64.b64encode(self.settings["COUCHBASE_PASSWORD"].encode("utf-8"))
        encoded_cb_pass_string = str(encoded_cb_pass_bytes, "utf-8")
        encoded_cb_user_bytes = base64.b64encode(self.settings["COUCHBASE_USER"].encode("utf-8"))
        encoded_cb_user_string = str(encoded_cb_user_bytes, "utf-8")
        encoded_cb_url_bytes = base64.b64encode(self.settings["COUCHBASE_URL"].encode("utf-8"))
        encoded_cb_url_string = str(encoded_cb_url_bytes, "utf-8")
        self.kubernetes.patch_or_create_namespaced_secret(name="cb-auth",
                                                          namespace=self.settings["COUCHBASE_NAMESPACE"],
                                                          literal="username",
                                                          value_of_literal=encoded_cb_user_string,
                                                          second_literal="password",
                                                          value_of_second_literal=encoded_cb_pass_string)
        kustomize_parser = Parser("couchbase/backup/kustomization.yaml", "Kustomization")
        kustomize_parser["namespace"] = self.settings["COUCHBASE_NAMESPACE"]
        kustomize_parser.dump_it()
        command = "kubectl kustomize couchbase/backup > ./couchbase-backup.yaml"
        subprocess_cmd(command)
        self.kubernetes.patch_or_create_namespaced_secret(name="cb-url",
                                                          namespace=self.settings["COUCHBASE_NAMESPACE"],
                                                          literal="url",
                                                          value_of_literal=encoded_cb_url_string)

        storage_class_parser = Parser("./couchbase-backup.yaml", "StorageClass")

        if self.settings["DEPLOYMENT_ARCH"] == "gke":
            storage_class_parser["provisioner"] = "kubernetes.io/gce-pd"
            del storage_class_parser["parameters"]["fsType"]
            del storage_class_parser["metadata"]["labels"]["k8s-addon"]
            storage_class_parser["parameters"]["type"] = self.settings["LDAP_VOLUME"]

        elif self.settings["DEPLOYMENT_ARCH"] == "aks":
            storage_class_parser["provisioner"] = "kubernetes.io/gce-pd"
            del storage_class_parser["parameters"]["fsType"]
            del storage_class_parser["metadata"]["labels"]["k8s-addon"]
            storage_class_parser["parameters"]["type"] = self.settings["LDAP_VOLUME"]
        storage_class_parser.dump_it()

        self.kubernetes.create_objects_from_dict("./couchbase-backup.yaml")

    @property
    def calculate_couchbase_resources(self):
        flows_string = self.settings["USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW"] + self.settings[
            "USING_CODE_FLOW"] + \
                       self.settings["USING_SCIM_FLOW"]
        tps = int(self.settings["EXPECTED_TRANSACTIONS_PER_SEC"])
        number_of_flows = flows_string.count("Y")
        if number_of_flows < 1:
            number_of_flows = 1
        number_of_data_nodes = number_of_flows + 1
        number_of_query_nodes = number_of_flows
        number_of_index_nodes = number_of_flows
        number_of_eventing_service_memory_nodes = number_of_flows - 1
        if number_of_eventing_service_memory_nodes < 1:
            number_of_eventing_service_memory_nodes = 1

        if not self.settings["COUCHBASE_GENERAL_STORAGE"]:
            self.settings["COUCHBASE_GENERAL_STORAGE"] = str(int(((tps / 2000) * 200 * (
                    int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 10000000)) + 5)) + "Gi"
        if not self.settings["COUCHBASE_DATA_STORAGE"]:
            self.settings["COUCHBASE_DATA_STORAGE"] = str(int(((tps / 2000) * 500 * (
                    int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 10000000)) + 5)) + "Gi"
        if not self.settings["COUCHBASE_INDEX_STORAGE"]:
            self.settings["COUCHBASE_INDEX_STORAGE"] = str(int(((tps / 2000) * 150 * (
                    int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 10000000)) + 5)) + "Gi"
        if not self.settings["COUCHBASE_QUERY_STORAGE"]:
            self.settings["COUCHBASE_QUERY_STORAGE"] = str(int(((tps / 2000) * 150 * (
                    int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 10000000)) + 5)) + "Gi"
        if not self.settings["COUCHBASE_ANALYTICS_STORAGE"]:
            self.settings["COUCHBASE_ANALYTICS_STORAGE"] = str(int(((tps / 2000) * 100 * (
                    int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 10000000)) + 5)) + "Gi"

        if self.settings["COUCHBASE_DATA_NODES"]:
            number_of_data_nodes = self.settings["COUCHBASE_DATA_NODES"]
        if self.settings["COUCHBASE_QUERY_NODES"]:
            number_of_query_nodes = self.settings["COUCHBASE_QUERY_NODES"]
        if self.settings["COUCHBASE_INDEX_NODES"]:
            number_of_index_nodes = self.settings["COUCHBASE_INDEX_NODES"]
        if self.settings["COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"]:
            number_of_eventing_service_memory_nodes = self.settings["COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"]

        data_service_memory_quota = ((tps / 2000) * 12800 * number_of_flows * (
                int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 1000000)) + 512
        if data_service_memory_quota > 12800:
            number_of_data_nodes = round(data_service_memory_quota / 12800)
            number_of_query_nodes = number_of_data_nodes - 1
            data_service_memory_quota = 12800
        data_memory_request = data_service_memory_quota * 1.40
        data_memory_limit = data_memory_request + 2000
        data_cpu_request = data_service_memory_quota * 0.625
        data_cpu_limit = data_cpu_request + 2000

        query_memory_request = data_service_memory_quota * 1.40
        query_memory_limit = query_memory_request + 2000
        query_cpu_request = data_service_memory_quota * 0.625
        query_cpu_limit = query_cpu_request + 2000

        index_service_memory_quota = ((tps / 2000) * 25600 * number_of_flows * (
                int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 1000000)) + 256
        if index_service_memory_quota > 25600:
            number_of_index_nodes = round(index_service_memory_quota / 25600)
            index_service_memory_quota = 25600
        index_memory_request = index_service_memory_quota * 1.40
        index_memory_limit = index_memory_request + 2000
        index_cpu_request = index_service_memory_quota * 0.625
        index_cpu_limit = index_cpu_request + 2000

        search_service_memory_quota = ((tps / 2000) * 4266 * number_of_flows * (
                int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 1000000)) + 256
        eventing_service_memory_quota = (4266 * number_of_flows * (
                int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 1000000)) + 256
        analytics_service_memory_quota = (4266 * number_of_flows * (
                int(self.settings["NUMBER_OF_EXPECTED_USERS"]) / 1000000)) + 1024
        if search_service_memory_quota > 4266:
            number_of_eventing_service_memory_nodes = round(search_service_memory_quota / 4266)
            search_service_memory_quota = 4266
            eventing_service_memory_quota = 4266
            analytics_service_memory_quota = 4266

        search_eventing_analytics_memory_quota_sum = (search_service_memory_quota + eventing_service_memory_quota +
                                                      analytics_service_memory_quota)
        search_eventing_analytics_memory_request = search_eventing_analytics_memory_quota_sum * 1.40
        search_eventing_analytics_memory_limit = search_eventing_analytics_memory_request + 2000
        search_eventing_analytics_cpu_request = search_eventing_analytics_memory_quota_sum * 0.625
        search_eventing_analytics_cpu_limit = search_eventing_analytics_cpu_request + 2000

        # Two services because query is assumed to take the same amount of mem quota
        total_mem_resources = data_service_memory_quota + data_service_memory_quota + index_service_memory_quota + \
                              search_eventing_analytics_memory_quota_sum

        total_cpu_resources = data_cpu_limit + query_cpu_limit + index_cpu_limit + search_eventing_analytics_cpu_limit

        resources_info = dict(COUCHBASE_DATA_NODES=int(number_of_data_nodes),
                              COUCHBASE_QUERY_NODES=int(number_of_query_nodes),
                              COUCHBASE_INDEX_NODES=int(number_of_index_nodes),
                              COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES=int(number_of_eventing_service_memory_nodes),
                              COUCHBASE_DATA_MEM_QUOTA=round(data_service_memory_quota),
                              COUCHBASE_DATA_MEM_REQUEST=round(data_memory_request),
                              COUCHBASE_DATA_MEM_LIMIT=round(data_memory_limit),
                              COUCHBASE_DATA_CPU_REQUEST=round(data_cpu_request),
                              COUCHBASE_DATA_CPU_LIMIT=round(data_cpu_limit),
                              COUCHBASE_QUERY_MEM_QUOTA=round(data_service_memory_quota),
                              COUCHBASE_QUERY_MEM_REQUEST=round(query_memory_request),
                              COUCHBASE_QUERY_MEM_LIMIT=round(query_memory_limit),
                              COUCHBASE_QUERY_CPU_REQUEST=round(query_cpu_request),
                              COUCHBASE_QUERY_CPU_LIMIT=round(query_cpu_limit),
                              COUCHBASE_INDEX_MEM_QUOTA=round(index_service_memory_quota),
                              COUCHBASE_INDEX_MEM_REQUEST=round(index_memory_request),
                              COUCHBASE_INDEX_MEM_LIMIT=round(index_memory_limit),
                              COUCHBASE_INDEX_CPU_REQUEST=round(index_cpu_request),
                              COUCHBASE_INDEX_CPU_LIMIT=round(index_cpu_limit),
                              COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_QUOTA=round(search_service_memory_quota),
                              COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_REQUEST=round(
                                  search_eventing_analytics_memory_request),
                              COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_LIMIT=round(
                                  search_eventing_analytics_memory_limit),
                              COUCHBASE_SEARCH_EVENTING_ANALYTICS_CPU_REQUEST=round(
                                  search_eventing_analytics_cpu_request),
                              COUCHBASE_SEARCH_EVENTING_ANALYTICS_CPU_LIMIT=round(search_eventing_analytics_cpu_limit),
                              TOTAL_RAM_NEEDED=round(total_mem_resources),
                              TOTAL_CPU_NEEDED=round(total_cpu_resources)
                              )
        self.settings["COUCHBASE_DATA_NODES"] = number_of_data_nodes
        self.settings["COUCHBASE_QUERY_NODES"] = number_of_query_nodes
        self.settings["COUCHBASE_INDEX_NODES"] = number_of_index_nodes
        self.settings["COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"] = number_of_eventing_service_memory_nodes
        return resources_info

    def analyze_couchbase_cluster_yaml(self):
        parser = Parser("./couchbase/couchbase-cluster.yaml", "CouchbaseCluster")
        parser["metadata"]["name"] = self.settings["COUCHBASE_CLUSTER_NAME"]
        number_of_buckets = len(parser["spec"]["buckets"])
        if self.settings["DEPLOYMENT_ARCH"] == "microk8s" or self.settings["DEPLOYMENT_ARCH"] == "minikube" or \
                self.settings["COUCHBASE_USE_LOW_RESOURCES"] == "Y":
            resources_servers = [{"name": "allServices", "size": 1,
                                  "services": ["data", "index", "query", "search", "eventing", "analytics"],
                                  "pod": {"volumeMounts":
                                              {"default": "pvc-general", "data": "pvc-data", "index": "pvc-index",
                                               "analytics": ["pvc-analytics"]}}}]
            data_service_memory_quota = 1024
            index_service_memory_quota = 512
            search_service_memory_quota = 512
            eventing_service_memory_quota = 512
            analytics_service_memory_quota = 1024
            memory_quota = 100
            self.settings["COUCHBASE_GENERAL_STORAGE"] = "5Gi"
            self.settings["COUCHBASE_DATA_STORAGE"] = "5Gi"
            self.settings["COUCHBASE_INDEX_STORAGE"] = "5Gi"
            self.settings["COUCHBASE_QUERY_STORAGE"] = "5Gi"
            self.settings["COUCHBASE_ANALYTICS_STORAGE"] = "5Gi"

        else:
            resources = self.calculate_couchbase_resources
            data_service_memory_quota = resources["COUCHBASE_DATA_MEM_QUOTA"]
            index_service_memory_quota = resources["COUCHBASE_INDEX_MEM_QUOTA"]
            search_service_memory_quota = resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_QUOTA"]
            eventing_service_memory_quota = resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_QUOTA"]
            analytics_service_memory_quota = resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_QUOTA"] + 1024
            memory_quota = ((resources["COUCHBASE_DATA_MEM_QUOTA"] - 500) / number_of_buckets)
            zones_list = self.settings["NODES_ZONES"]
            data_server_spec = create_server_spec_per_cb_service(zones_list, int(resources["COUCHBASE_DATA_NODES"]),
                                                                 "data",
                                                                 str(resources["COUCHBASE_DATA_MEM_REQUEST"]),
                                                                 str(resources["COUCHBASE_DATA_MEM_LIMIT"]),
                                                                 str(resources["COUCHBASE_DATA_CPU_REQUEST"]),
                                                                 str(resources["COUCHBASE_DATA_CPU_LIMIT"]))

            query_server_spec = create_server_spec_per_cb_service(zones_list, int(resources["COUCHBASE_QUERY_NODES"]),
                                                                  "query",
                                                                  str(resources["COUCHBASE_QUERY_MEM_REQUEST"]),
                                                                  str(resources["COUCHBASE_QUERY_MEM_LIMIT"]),
                                                                  str(resources["COUCHBASE_QUERY_CPU_REQUEST"]),
                                                                  str(resources["COUCHBASE_QUERY_CPU_LIMIT"]))

            index_server_spec = create_server_spec_per_cb_service(zones_list,
                                                                  int(resources["COUCHBASE_INDEX_NODES"]), "index",
                                                                  str(resources["COUCHBASE_INDEX_MEM_REQUEST"]),
                                                                  str(resources["COUCHBASE_INDEX_MEM_LIMIT"]),
                                                                  str(resources["COUCHBASE_INDEX_CPU_REQUEST"]),
                                                                  str(resources["COUCHBASE_INDEX_CPU_LIMIT"]))

            search_eventing_analytics_server_spec = create_server_spec_per_cb_service(
                zones_list,
                int(resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"]), "analytics",
                str(resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_REQUEST"]),
                str(resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_LIMIT"]),
                str(resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_CPU_REQUEST"]),
                str(resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_CPU_LIMIT"]))

            resources_servers = data_server_spec + query_server_spec + \
                                index_server_spec + search_eventing_analytics_server_spec

        if self.settings["NODES_ZONES"]:
            unique_zones = list(dict.fromkeys(self.settings["NODES_ZONES"]))
            parser["spec"]["serverGroups"] = unique_zones
        parser["spec"]["cluster"]["dataServiceMemoryQuota"] = data_service_memory_quota
        parser["spec"]["cluster"]["indexServiceMemoryQuota"] = index_service_memory_quota
        parser["spec"]["cluster"]["searchServiceMemoryQuota"] = search_service_memory_quota
        parser["spec"]["cluster"]["eventingServiceMemoryQuota"] = eventing_service_memory_quota
        parser["spec"]["cluster"]["analyticsServiceMemoryQuota"] = analytics_service_memory_quota

        for i in range(number_of_buckets):
            parser["spec"]["buckets"][i]["memoryQuota"] = int(memory_quota + 100)
        parser["metadata"]["name"] = self.settings["COUCHBASE_CLUSTER_NAME"]
        parser["spec"]["servers"] = resources_servers

        number_of_volume_claims = len(parser["spec"]["volumeClaimTemplates"])
        for i in range(number_of_volume_claims):
            name = parser["spec"]["volumeClaimTemplates"][i]["metadata"]["name"]
            if name == "pvc-general":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings["COUCHBASE_GENERAL_STORAGE"]
            elif name == "pvc-data":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings["COUCHBASE_DATA_STORAGE"]
            elif name == "pvc-index":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings["COUCHBASE_INDEX_STORAGE"]
            elif name == "pvc-query":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings["COUCHBASE_QUERY_STORAGE"]
            elif name == "pvc-analytics":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings["COUCHBASE_ANALYTICS_STORAGE"]
        parser.dump_it()

    def install(self):
        self.kubernetes.delete_namespace(self.settings["GLUU_NAMESPACE"])
        self.kubernetes.create_namespace(name=self.settings["GLUU_NAMESPACE"])
        if self.settings["COUCHBASE_CLUSTER_FILE_OVERRIDE"] == "N":
            self.analyze_couchbase_cluster_yaml()
        cb_namespace = self.settings["COUCHBASE_NAMESPACE"]
        storage_class_file_parser = Parser(self.storage_class_file, "StorageClass")
        if self.settings['DEPLOYMENT_ARCH'] == "gke":
            storage_class_file_parser["provisioner"] = "kubernetes.io/gce-pd"
            try:
                del storage_class_file_parser["parameters"]["encrypted"]
            except KeyError:
                logger.info("Key not found")
            storage_class_file_parser["parameters"]["type"] = self.settings["COUCHBASE_VOLUME_TYPE"]
            storage_class_file_parser.dump_it()
        elif self.settings['DEPLOYMENT_ARCH'] == "microk8s":
            storage_class_file_parser["provisioner"] = "microk8s.io/hostpath"
            try:
                del storage_class_file_parser["allowVolumeExpansion"]
                del storage_class_file_parser["parameters"]
            except KeyError:
                logger.info("Key not found")
            storage_class_file_parser.dump_it()
        elif self.settings['DEPLOYMENT_ARCH'] == "minikube":
            storage_class_file_parser["provisioner"] = "k8s.io/minikube-hostpath"
            try:
                del storage_class_file_parser["allowVolumeExpansion"]
                del storage_class_file_parser["parameters"]
            except KeyError:
                logger.info("Key not found")
            storage_class_file_parser.dump_it()
        else:
            try:
                storage_class_file_parser["parameters"]["type"] = self.settings["COUCHBASE_VOLUME_TYPE"]
            except KeyError:
                logger.info("Key not found")
            storage_class_file_parser.dump_it()

        logger.info("Installing Couchbase...")
        custom_cb_ca_crt = Path("./ca.crt")
        custom_cb_crt = Path("./chain.pem")
        custom_cb_key = Path("./pkey.key")
        if not custom_cb_ca_crt.exists() and not custom_cb_crt.exists() and not custom_cb_key.exists():
            setup_crts(self.settings["COUCHBASE_CN"], "couchbase-server", self.settings["COUCHBASE_SUBJECT_ALT_NAME"])
        self.kubernetes.create_namespace(name=cb_namespace)
        chain_pem_filepath = Path("chain.pem")
        pkey_filepath = Path("pkey.key")
        tls_cert_filepath = Path("tls-cert-file")
        tls_private_key_filepath = Path("tls-private-key-file")
        ca_cert_filepath = Path("ca.crt")
        shutil.copyfile(ca_cert_filepath, Path("./couchbase.crt"))
        shutil.copyfile(chain_pem_filepath, tls_cert_filepath)
        shutil.copyfile(pkey_filepath, tls_private_key_filepath)
        with open(tls_cert_filepath) as content_file:
            tls_crt_content = content_file.read()
            encoded_tls_crt_bytes = base64.b64encode(tls_crt_content.encode("utf-8"))
            encoded_tls_crt_string = str(encoded_tls_crt_bytes, "utf-8")

        with open(tls_private_key_filepath) as content_file:
            tls_key_content = content_file.read()
            encoded_tls_key_bytes = base64.b64encode(tls_key_content.encode("utf-8"))
            encoded_tls_key_string = str(encoded_tls_key_bytes, "utf-8")

        encoded_ca_crt_string = self.settings["COUCHBASE_CRT"]
        if not encoded_ca_crt_string:
            with open(ca_cert_filepath) as content_file:
                ca_crt_content = content_file.read()
                encoded_ca_crt_bytes = base64.b64encode(ca_crt_content.encode("utf-8"))
                encoded_ca_crt_string = str(encoded_ca_crt_bytes, "utf-8")
            self.settings["COUCHBASE_CRT"] = encoded_ca_crt_string

        with open(chain_pem_filepath) as content_file:
            chain_pem_content = content_file.read()
            encoded_chain_bytes = base64.b64encode(chain_pem_content.encode("utf-8"))
            encoded_chain_string = str(encoded_chain_bytes, "utf-8")

        with open(pkey_filepath) as content_file:
            pkey_content = content_file.read()
            encoded_pkey_bytes = base64.b64encode(pkey_content.encode("utf-8"))
            encoded_pkey_string = str(encoded_pkey_bytes, "utf-8")

        update_settings_json_file(self.settings)
        self.kubernetes.patch_or_create_namespaced_secret(name="couchbase-server-tls",
                                                          namespace=cb_namespace,
                                                          literal=chain_pem_filepath.name,
                                                          value_of_literal=encoded_chain_string,
                                                          second_literal=pkey_filepath.name,
                                                          value_of_second_literal=encoded_pkey_string)
        self.kubernetes.patch_or_create_namespaced_secret(name="couchbase-operator-tls",
                                                          namespace=cb_namespace,
                                                          literal=ca_cert_filepath.name,
                                                          value_of_literal=encoded_ca_crt_string)

        couchbase_admission_file_secret_parser = Parser(self.couchbase_admission_file, "Secret")
        couchbase_admission_file_secret_parser["data"]["tls-cert-file"] = encoded_tls_crt_string
        couchbase_admission_file_secret_parser["data"]["tls-private-key-file"] = encoded_tls_key_string
        couchbase_admission_file_secret_parser.dump_it()

        couchbase_admission_file_mutating_webhook_configuration_parser = Parser(self.couchbase_admission_file,
                                                                                "MutatingWebhookConfiguration")
        couchbase_admission_file_mutating_webhook_configuration_parser["webhooks"][0]["clientConfig"]["caBundle"] \
            = encoded_tls_crt_string
        couchbase_admission_file_mutating_webhook_configuration_parser["webhooks"][0]["clientConfig"]["service"][
            "namespace"] = cb_namespace
        couchbase_admission_file_mutating_webhook_configuration_parser.dump_it()

        couchbase_admission_file_validating_webhook_configuration_parser = Parser(self.couchbase_admission_file,
                                                                                  "ValidatingWebhookConfiguration")
        couchbase_admission_file_validating_webhook_configuration_parser["webhooks"][0][
            "clientConfig"]["caBundle"] = encoded_tls_crt_string
        couchbase_admission_file_validating_webhook_configuration_parser["webhooks"][0]["clientConfig"]["service"][
            "namespace"] = cb_namespace
        couchbase_admission_file_validating_webhook_configuration_parser.dump_it()

        couchbase_admission_file_cluster_role_binding_parser = Parser(self.couchbase_admission_file,
                                                                      "ClusterRoleBinding")
        couchbase_admission_file_cluster_role_binding_parser["subjects"][0]["namespace"] \
            = cb_namespace
        couchbase_admission_file_cluster_role_binding_parser.dump_it()

        encoded_cb_user_bytes = base64.b64encode(self.settings["COUCHBASE_USER"].encode("utf-8"))
        encoded_cb_user_string = str(encoded_cb_user_bytes, "utf-8")
        encoded_cb_pass_bytes = base64.b64encode(self.settings["COUCHBASE_PASSWORD"].encode("utf-8"))
        encoded_cb_pass_string = str(encoded_cb_pass_bytes, "utf-8")

        self.create_couchbase_gluu_cert_pass_secrets(encoded_ca_crt_string, encoded_cb_pass_string)

        self.kubernetes.create_objects_from_dict(self.couchbase_admission_file, namespace=cb_namespace)
        self.kubernetes.create_objects_from_dict(self.couchbbase_custom_resource_definition_file,
                                                 namespace=cb_namespace)
        self.kubernetes.create_objects_from_dict(self.couchbase_operator_role_file, namespace=cb_namespace)
        self.kubernetes.create_namespaced_service_account(name="couchbase-operator", namespace=cb_namespace)
        self.kubernetes.create_namespaced_role_binding(role_binding_name="couchbase-operator",
                                                       service_account_name="couchbase-operator",
                                                       role_name="couchbase-operator",
                                                       namespace=cb_namespace)
        self.kubernetes.create_objects_from_dict(self.couchbase_operator_deployment_file, namespace=cb_namespace)
        self.kubernetes.check_pods_statuses(cb_namespace, "app=couchbase-operator", 700)

        self.kubernetes.patch_or_create_namespaced_secret(name="cb-auth",
                                                          namespace=cb_namespace,
                                                          literal="username",
                                                          value_of_literal=encoded_cb_user_string,
                                                          second_literal="password",
                                                          value_of_second_literal=encoded_cb_pass_string)

        self.kubernetes.create_objects_from_dict(self.storage_class_file, namespace=cb_namespace)
        self.kubernetes.create_namespaced_custom_object(filepath=self.couchbase_cluster_file,
                                                        namespace=cb_namespace)

        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_analytics=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_data=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_eventing=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_index=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_query=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_search=enabled", 700)
        # Setup couchbase backups
        if self.settings["DEPLOYMENT_ARCH"] != "microk8s" and self.settings["DEPLOYMENT_ARCH"] != "minikube":
            self.setup_backup_couchbase()
        shutil.rmtree(self.couchbase_source_folder_pattern, ignore_errors=True)

        if self.settings["DEPLOY_MULTI_CLUSTER"] == "Y":
            logger.info("Setup XDCR between the running gluu couchbase cluster and this one")

    def uninstall(self):
        logger.info("Deleting Couchbase...")
        self.kubernetes.delete_storage_class("couchbase-sc")
        self.kubernetes.delete_custom_resource("couchbaseclusters.couchbase.com")
        self.kubernetes.delete_validating_webhook_configuration("couchbase-operator-admission")
        self.kubernetes.delete_mutating_webhook_configuration("couchbase-operator-admission")
        self.kubernetes.delete_cluster_role_binding("couchbase-operator-admission")
        self.kubernetes.delete_cluster_role("couchbase-operator-admission")
        self.kubernetes.delete_role("couchbase-operator", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_secret("cb-auth", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_deployment_using_name("couchbase-operator", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_role_binding("couchbase-operator", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_service_account("couchbase-operator", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_service("couchbase-operator-admission", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_deployment_using_name("couchbase-operator-admission",
                                                     self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_service_account("couchbase-operator-admission", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_secret("couchbase-operator-admission", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_secret("couchbase-operator-tls", self.settings["COUCHBASE_NAMESPACE"])
        self.kubernetes.delete_namespace(self.settings["COUCHBASE_NAMESPACE"])
        shutil.rmtree(Path("./couchbase-source-folder"), ignore_errors=True)
