"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Installs and configures Couchbase
"""

from pathlib import Path
import shutil
import tarfile
from .kubeapi import Kubernetes
from .yamlparser import Parser
from .common import get_logger, exec_cmd
from .settings import SettingsHandler
from .pycert import setup_crts
import sys
import base64
import random
import os

logger = get_logger("gluu-couchbase     ")


def extract_couchbase_tar(tar_file):
    """
    Extracts couchbase kubernetes tar file
    :param tar_file:
    """
    extract_folder = Path("./couchbase-source-folder")
    logger.info("Extracting {} in {} ".format(tar_file, extract_folder))
    tr = tarfile.open(tar_file)
    tr.extractall(path=extract_folder)
    tr.close()


def set_memory_for_buckets(memory_quota):
    buckets = ["gluu", "gluu-site", "gluu-user"]
    ephemeral_buckets = ["gluu-cache", "gluu-token", "gluu-session"]

    for bucket in buckets:
        parser = Parser("./couchbase/couchbase-buckets.yaml", "CouchbaseBucket", bucket)
        parser["spec"]["memoryQuota"] = str(memory_quota + 100) + "Mi"
        parser.dump_it()

    for bucket in ephemeral_buckets:
        parser = Parser("./couchbase/couchbase-ephemeral-buckets.yaml", "CouchbaseEphemeralBucket", bucket)
        parser["spec"]["memoryQuota"] = str(memory_quota + 100) + "Mi"
        parser.dump_it()


def create_server_spec_per_cb_service(zones, number_of_cb_service_nodes, cb_service_name, mem_req, mem_limit,
                                      cpu_req, cpu_limit):
    """
    Creates the server spec section inside couchbase.yaml for each couchbase service
    :param zones:
    :param number_of_cb_service_nodes:
    :param cb_service_name:
    :param mem_req:
    :param mem_limit:
    :param cpu_req:
    :param cpu_limit:
    :return:
    """
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
    def __init__(self):
        self.settings = SettingsHandler()
        self.kubernetes = Kubernetes()
        self.storage_class_file = Path("./couchbase/storageclasses.yaml")
        self.couchbase_cluster_file = Path("./couchbase/couchbase-cluster.yaml")
        self.couchbase_buckets_file = Path("./couchbase/couchbase-buckets.yaml")
        self.couchbase_ephemeral_buckets_file = Path("./couchbase/couchbase-ephemeral-buckets.yaml")
        self.couchbase_source_folder_pattern, self.couchbase_source_file = self.get_couchbase_files
        self.couchbase_custom_resource_definition_file = self.couchbase_source_file.joinpath("crd.yaml")
        self.couchbase_operator_dac_file = self.couchbase_source_file.joinpath("operator_dac.yaml")
        self.filename = ""

    @property
    def get_couchbase_files(self):
        """
        Returns the couchbase extracted package folder path containing manifests and the tar package file
        :return:
        """
        if self.settings.get("INSTALL_COUCHBASE") == "Y":
            couchbase_tar_pattern = "couchbase-autonomous-operator-kubernetes_*.tar.gz"
            directory = Path('.')
            try:
                couchbase_tar_file = list(directory.glob(couchbase_tar_pattern))[0]
                if "_1." in str(couchbase_tar_file.resolve()):
                    logger.fatal("Couchbase Autonomous Operator version must be > 2.0")
                    sys.exit()

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
        """
        Create cor patch secret containing couchbase certificate authority crt and couchbase admin password
        :param encoded_ca_crt_string:
        :param encoded_cb_pass_string:
        """
        # Remove this if its not needed
        self.kubernetes.patch_or_create_namespaced_secret(name="cb-crt",
                                                          namespace=self.settings.get("GLUU_NAMESPACE"),
                                                          literal="couchbase.crt",
                                                          value_of_literal=encoded_ca_crt_string)

        # Remove this if its not needed
        self.kubernetes.patch_or_create_namespaced_secret(name="cb-pass",
                                                          namespace=self.settings.get("GLUU_NAMESPACE"),
                                                          literal="couchbase_password",
                                                          value_of_literal=encoded_cb_pass_string)

    def setup_backup_couchbase(self):
        """
        Setups Couchbase backup strategy
        """
        couchbase_backup_file = Path("./couchbase/backup/couchbase-backup.yaml")
        parser = Parser(couchbase_backup_file, "CouchbaseBackup")
        parser["spec"]["full"]["schedule"] = self.settings.get("COUCHBASE_FULL_BACKUP_SCHEDULE")
        parser["spec"]["incremental"]["schedule"] = self.settings.get("COUCHBASE_INCR_BACKUP_SCHEDULE")
        parser["spec"]["backupRetention"] = self.settings.get("COUCHBASE_BACKUP_RETENTION_TIME")
        parser["spec"]["size"] = self.settings.get("COUCHBASE_BACKUP_STORAGE_SIZE")
        parser.dump_it()
        self.kubernetes.create_namespaced_custom_object(filepath=couchbase_backup_file,
                                                        group="couchbase.com",
                                                        version="v2",
                                                        plural="couchbasebackups",
                                                        namespace=self.settings.get("COUCHBASE_NAMESPACE"))

    @property
    def calculate_couchbase_resources(self):
        """
        Return a dictionary containing couchbase resource information calculated
        Alpha
        :return:
        """
        tps = int(self.settings.get("EXPECTED_TRANSACTIONS_PER_SEC"))
        number_of_data_nodes = 0
        number_of_query_nodes = 0
        number_of_index_nodes = 0
        number_of_eventing_service_memory_nodes = 0
        user_ratio = int(self.settings.get("NUMBER_OF_EXPECTED_USERS")) / 50000000
        tps_ratio = tps / 14000

        if self.settings.get("USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW") == "Y":
            number_of_data_nodes += tps_ratio * 7 * user_ratio
            number_of_query_nodes += tps_ratio * 5 * user_ratio
            number_of_index_nodes += tps_ratio * 5 * user_ratio
            number_of_eventing_service_memory_nodes += tps_ratio * 4 * user_ratio

        if self.settings.get("USING_CODE_FLOW") == "Y":
            number_of_data_nodes += tps_ratio * 14 * user_ratio
            number_of_query_nodes += tps_ratio * 12 * user_ratio
            number_of_index_nodes += tps_ratio * 13 * user_ratio
            number_of_eventing_service_memory_nodes += tps_ratio * 7 * user_ratio

        if self.settings.get("USING_SCIM_FLOW") == "Y":
            number_of_data_nodes += tps_ratio * 7 * user_ratio
            number_of_query_nodes += tps_ratio * 5 * user_ratio
            number_of_index_nodes += tps_ratio * 5 * user_ratio
            number_of_eventing_service_memory_nodes += tps_ratio * 4 * user_ratio

        if not self.settings.get("COUCHBASE_GENERAL_STORAGE"):
            self.settings.set("COUCHBASE_GENERAL_STORAGE", str(int((tps_ratio * (
                    int(self.settings.get("NUMBER_OF_EXPECTED_USERS")) / 125000)) + 5)) + "Gi")
        if not self.settings.get("COUCHBASE_DATA_STORAGE"):
            self.settings.set("COUCHBASE_DATA_STORAGE", str(int((tps_ratio * (
                    int(self.settings.get("NUMBER_OF_EXPECTED_USERS")) / 100000)) + 5)) + "Gi")
        if not self.settings.get("COUCHBASE_INDEX_STORAGE"):
            self.settings.set("COUCHBASE_INDEX_STORAGE", str(int((tps_ratio * (
                    int(self.settings.get("NUMBER_OF_EXPECTED_USERS")) / 200000)) + 5)) + "Gi")
        if not self.settings.get("COUCHBASE_QUERY_STORAGE"):
            self.settings.set("COUCHBASE_QUERY_STORAGE", str(int((tps_ratio * (
                    int(self.settings.get("NUMBER_OF_EXPECTED_USERS")) / 200000)) + 5)) + "Gi")
        if not self.settings.get("COUCHBASE_ANALYTICS_STORAGE"):
            self.settings.set("COUCHBASE_ANALYTICS_STORAGE", str(int((tps_ratio * (
                    int(self.settings.get("NUMBER_OF_EXPECTED_USERS")) / 250000)) + 5)) + "Gi")

        if self.settings.get("COUCHBASE_DATA_NODES"):
            number_of_data_nodes = self.settings.get("COUCHBASE_DATA_NODES")
        if self.settings.get("COUCHBASE_QUERY_NODES"):
            number_of_query_nodes = self.settings.get("COUCHBASE_QUERY_NODES")
        if self.settings.get("COUCHBASE_INDEX_NODES"):
            number_of_index_nodes = self.settings.get("COUCHBASE_INDEX_NODES")
        if self.settings.get("COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"):
            number_of_eventing_service_memory_nodes = self.settings.get("COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES")

        data_service_memory_quota = (tps_ratio * 40000 * user_ratio) + 512
        data_memory_request = data_service_memory_quota / 4
        data_memory_limit = data_memory_request
        data_cpu_request = data_service_memory_quota / 4
        data_cpu_limit = data_cpu_request

        query_memory_request = data_memory_request
        query_memory_limit = query_memory_request
        query_cpu_request = data_service_memory_quota / 4
        query_cpu_limit = query_cpu_request

        index_service_memory_quota = (tps_ratio * 25000 * user_ratio) + 256
        index_memory_request = index_service_memory_quota / 3
        index_memory_limit = index_memory_request
        index_cpu_request = index_service_memory_quota / 3
        index_cpu_limit = index_cpu_request

        search_service_memory_quota = (tps_ratio * 4000 * user_ratio) + 256
        eventing_service_memory_quota = (tps_ratio * 4000 * user_ratio) + 256
        analytics_service_memory_quota = (tps_ratio * 4000 * user_ratio) + 1024

        search_eventing_analytics_memory_quota_sum = (search_service_memory_quota + eventing_service_memory_quota +
                                                      analytics_service_memory_quota)
        search_eventing_analytics_memory_request = tps_ratio * 10000 * user_ratio
        search_eventing_analytics_memory_limit = search_eventing_analytics_memory_request
        search_eventing_analytics_cpu_request = tps_ratio * 6000 * user_ratio
        search_eventing_analytics_cpu_limit = search_eventing_analytics_cpu_request

        # Two services because query is assumed to take the same amount of mem quota
        total_mem_resources = \
            data_service_memory_quota + data_service_memory_quota + index_service_memory_quota + \
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
        self.settings.set("COUCHBASE_DATA_NODES", number_of_data_nodes)
        self.settings.set("COUCHBASE_QUERY_NODES", number_of_query_nodes)
        self.settings.set("COUCHBASE_INDEX_NODES", number_of_index_nodes)
        self.settings.set("COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES", number_of_eventing_service_memory_nodes)
        return resources_info

    def analyze_couchbase_cluster_yaml(self):
        """
        Dumps created calculated resources into couchbase.yaml file. ALso includes cloud zones.
        """
        parser = Parser("./couchbase/couchbase-cluster.yaml", "CouchbaseCluster")
        parser["metadata"]["name"] = self.settings.get("COUCHBASE_CLUSTER_NAME")
        number_of_buckets = 5
        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube") or \
                self.settings.get("COUCHBASE_USE_LOW_RESOURCES") == "Y":
            resources_servers = [{"name": "allServices", "size": 1,
                                  "services": ["data", "index", "query", "search", "eventing", "analytics"],
                                  "volumeMounts": {"default": "pvc-general",
                                                   "data": "pvc-data", "index": "pvc-index",
                                                   "analytics": ["pvc-analytics"]}}]
            data_service_memory_quota = 1024
            index_service_memory_quota = 512
            search_service_memory_quota = 512
            eventing_service_memory_quota = 512
            analytics_service_memory_quota = 1024
            memory_quota = 0
            self.settings.set("COUCHBASE_GENERAL_STORAGE", "5Gi")
            self.settings.set("COUCHBASE_DATA_STORAGE", "5Gi")
            self.settings.set("COUCHBASE_INDEX_STORAGE", "5Gi")
            self.settings.set("COUCHBASE_QUERY_STORAGE", "5Gi")
            self.settings.set("COUCHBASE_ANALYTICS_STORAGE", "5Gi")

        else:
            resources = self.calculate_couchbase_resources
            data_service_memory_quota = resources["COUCHBASE_DATA_MEM_QUOTA"]
            index_service_memory_quota = resources["COUCHBASE_INDEX_MEM_QUOTA"]
            search_service_memory_quota = resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_QUOTA"]
            eventing_service_memory_quota = resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_QUOTA"]
            analytics_service_memory_quota = resources["COUCHBASE_SEARCH_EVENTING_ANALYTICS_MEM_QUOTA"] + 1024
            memory_quota = ((resources["COUCHBASE_DATA_MEM_QUOTA"] - 500) / number_of_buckets)
            zones_list = self.settings.get("NODES_ZONES")
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

            resources_servers = \
                data_server_spec + query_server_spec + index_server_spec + \
                search_eventing_analytics_server_spec

        if self.settings.get("NODES_ZONES"):
            unique_zones = list(dict.fromkeys(self.settings.get("NODES_ZONES")))
            parser["spec"]["serverGroups"] = unique_zones
        parser["spec"]["cluster"]["dataServiceMemoryQuota"] = str(data_service_memory_quota) + "Mi"
        parser["spec"]["cluster"]["indexServiceMemoryQuota"] = str(index_service_memory_quota) + "Mi"
        parser["spec"]["cluster"]["searchServiceMemoryQuota"] = str(search_service_memory_quota) + "Mi"
        parser["spec"]["cluster"]["eventingServiceMemoryQuota"] = str(eventing_service_memory_quota) + "Mi"
        parser["spec"]["cluster"]["analyticsServiceMemoryQuota"] = str(analytics_service_memory_quota) + "Mi"

        set_memory_for_buckets(memory_quota)
        parser["metadata"]["name"] = self.settings.get("COUCHBASE_CLUSTER_NAME")
        parser["spec"]["servers"] = resources_servers

        number_of_volume_claims = len(parser["spec"]["volumeClaimTemplates"])
        for i in range(number_of_volume_claims):
            name = parser["spec"]["volumeClaimTemplates"][i]["metadata"]["name"]
            if name == "pvc-general":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings.get("COUCHBASE_GENERAL_STORAGE")
            elif name == "pvc-data":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings.get("COUCHBASE_DATA_STORAGE")
            elif name == "pvc-index":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings.get("COUCHBASE_INDEX_STORAGE")
            elif name == "pvc-query":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings.get("COUCHBASE_QUERY_STORAGE")
            elif name == "pvc-analytics":
                parser["spec"]["volumeClaimTemplates"][i]["spec"]["resources"]["requests"]["storage"] = \
                    self.settings.get("COUCHBASE_ANALYTICS_STORAGE")
        parser.dump_it()

    def install(self):
        """
        Installs Couchbase
        """
        self.kubernetes.create_namespace(name=self.settings.get("GLUU_NAMESPACE"))
        if self.settings.get("COUCHBASE_CLUSTER_FILE_OVERRIDE") == "N":
            self.analyze_couchbase_cluster_yaml()
        cb_namespace = self.settings.get("COUCHBASE_NAMESPACE")
        storage_class_file_parser = Parser(self.storage_class_file, "StorageClass")
        if self.settings.get('DEPLOYMENT_ARCH') == "gke" or \
                self.settings.get('DEPLOYMENT_ARCH') == "aks" or \
                self.settings.get('DEPLOYMENT_ARCH') == "do":
            try:
                del storage_class_file_parser["parameters"]["encrypted"]
            except KeyError:
                logger.info("Key not found")
            storage_class_file_parser["parameters"]["type"] = self.settings.get("COUCHBASE_VOLUME_TYPE")
        if self.settings.get('DEPLOYMENT_ARCH') == "gke":
            storage_class_file_parser["provisioner"] = "kubernetes.io/gce-pd"
        elif self.settings.get('DEPLOYMENT_ARCH') == "aks":
            storage_class_file_parser["provisioner"] = "kubernetes.io/azure-disk"
        elif self.settings.get('DEPLOYMENT_ARCH') == "do":
            storage_class_file_parser["provisioner"] = "dobs.csi.digitalocean.com"
        elif self.settings.get('DEPLOYMENT_ARCH') == "microk8s":
            storage_class_file_parser["provisioner"] = "microk8s.io/hostpath"
            try:
                del storage_class_file_parser["allowVolumeExpansion"]
                del storage_class_file_parser["parameters"]
            except KeyError:
                logger.info("Key not found")
            storage_class_file_parser.dump_it()
        elif self.settings.get('DEPLOYMENT_ARCH') == "minikube":
            storage_class_file_parser["provisioner"] = "k8s.io/minikube-hostpath"
            try:
                del storage_class_file_parser["allowVolumeExpansion"]
                del storage_class_file_parser["parameters"]
            except KeyError:
                logger.info("Key not found")
            storage_class_file_parser.dump_it()
        else:
            try:
                storage_class_file_parser["parameters"]["type"] = self.settings.get("COUCHBASE_VOLUME_TYPE")
            except KeyError:
                logger.info("Key not found")
        storage_class_file_parser.dump_it()

        logger.info("Installing Couchbase...")
        couchbase_crts_keys = Path("couchbase_crts_keys")
        if not couchbase_crts_keys.exists():
            os.mkdir(couchbase_crts_keys)
        custom_cb_ca_crt = Path("./couchbase_crts_keys/ca.crt")
        custom_cb_crt = Path("./couchbase_crts_keys/chain.pem")
        custom_cb_key = Path("./couchbase_crts_keys/pkey.key")
        if not custom_cb_ca_crt.exists() and not custom_cb_crt.exists() and not custom_cb_key.exists():
            setup_crts(ca_common_name=self.settings.get("COUCHBASE_CN"),
                       cert_common_name="couchbase-server",
                       san_list=self.settings.get("COUCHBASE_SUBJECT_ALT_NAME"),
                       ca_cert_file="./couchbase_crts_keys/ca.crt",
                       ca_key_file="./couchbase_crts_keys/ca.key",
                       cert_file="./couchbase_crts_keys/chain.pem",
                       key_file="./couchbase_crts_keys/pkey.key")
        self.kubernetes.create_namespace(name=cb_namespace)
        chain_pem_filepath = Path("./couchbase_crts_keys/chain.pem")
        pkey_filepath = Path("./couchbase_crts_keys/pkey.key")
        tls_cert_filepath = Path("./couchbase_crts_keys/tls-cert-file")
        tls_private_key_filepath = Path("./couchbase_crts_keys/tls-private-key-file")
        ca_cert_filepath = Path("./couchbase_crts_keys/ca.crt")
        shutil.copyfile(ca_cert_filepath, Path("./couchbase_crts_keys/couchbase.crt"))
        shutil.copyfile(chain_pem_filepath, tls_cert_filepath)
        shutil.copyfile(pkey_filepath, tls_private_key_filepath)

        encoded_ca_crt_string = self.settings.get("COUCHBASE_CRT")
        if not encoded_ca_crt_string:
            with open(ca_cert_filepath) as content_file:
                ca_crt_content = content_file.read()
                encoded_ca_crt_bytes = base64.b64encode(ca_crt_content.encode("utf-8"))
                encoded_ca_crt_string = str(encoded_ca_crt_bytes, "utf-8")
            self.settings.set("COUCHBASE_CRT", encoded_ca_crt_string)

        with open(chain_pem_filepath) as content_file:
            chain_pem_content = content_file.read()
            encoded_chain_bytes = base64.b64encode(chain_pem_content.encode("utf-8"))
            encoded_chain_string = str(encoded_chain_bytes, "utf-8")

        with open(pkey_filepath) as content_file:
            pkey_content = content_file.read()
            encoded_pkey_bytes = base64.b64encode(pkey_content.encode("utf-8"))
            encoded_pkey_string = str(encoded_pkey_bytes, "utf-8")

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

        encoded_cb_user_bytes = base64.b64encode(self.settings.get("COUCHBASE_USER").encode("utf-8"))
        encoded_cb_user_string = str(encoded_cb_user_bytes, "utf-8")
        encoded_cb_pass_bytes = base64.b64encode(self.settings.get("COUCHBASE_PASSWORD").encode("utf-8"))
        encoded_cb_pass_string = str(encoded_cb_pass_bytes, "utf-8")

        self.create_couchbase_gluu_cert_pass_secrets(encoded_ca_crt_string, encoded_cb_pass_string)

        command = "./{}/bin/cbopcfg -backup=true -namespace={}".format(self.couchbase_source_file,
                                                                       self.settings.get("COUCHBASE_NAMESPACE"))
        exec_cmd(command, output_file=self.couchbase_operator_dac_file)
        couchbase_cluster_parser = Parser(self.couchbase_cluster_file, "CouchbaseCluster")
        couchbase_cluster_parser["spec"]["networking"]["tls"]["static"]["serverSecret"] = "couchbase-server-tls"
        couchbase_cluster_parser["spec"]["networking"]["tls"]["static"]["operatorSecret"] = "couchbase-operator-tls"
        couchbase_cluster_parser.dump_it()

        self.kubernetes.create_objects_from_dict(self.couchbase_custom_resource_definition_file,
                                                 namespace=cb_namespace)

        self.kubernetes.create_objects_from_dict(self.couchbase_operator_dac_file,
                                                 namespace=cb_namespace)

        self.kubernetes.check_pods_statuses(cb_namespace, "app=couchbase-operator", 700)

        self.kubernetes.patch_or_create_namespaced_secret(name="cb-auth",
                                                          namespace=cb_namespace,
                                                          literal="username",
                                                          value_of_literal=encoded_cb_user_string,
                                                          second_literal="password",
                                                          value_of_second_literal=encoded_cb_pass_string)

        self.kubernetes.create_objects_from_dict(self.storage_class_file, namespace=cb_namespace)
        self.kubernetes.create_namespaced_custom_object(filepath=self.couchbase_cluster_file,
                                                        group="couchbase.com",
                                                        version="v2",
                                                        plural="couchbaseclusters",
                                                        namespace=cb_namespace)
        self.kubernetes.create_namespaced_custom_object(filepath=self.couchbase_buckets_file,
                                                        group="couchbase.com",
                                                        version="v2",
                                                        plural="couchbasebuckets",
                                                        namespace=cb_namespace)
        self.kubernetes.create_namespaced_custom_object(filepath=self.couchbase_ephemeral_buckets_file,
                                                        group="couchbase.com",
                                                        version="v2",
                                                        plural="couchbaseephemeralbuckets",
                                                        namespace=cb_namespace)

        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_analytics=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_data=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_eventing=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_index=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_query=enabled", 700)
        self.kubernetes.check_pods_statuses(cb_namespace, "couchbase_service_search=enabled", 700)
        # Setup couchbase backups
        if self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            self.setup_backup_couchbase()
        shutil.rmtree(self.couchbase_source_folder_pattern, ignore_errors=True)

        if self.settings.get("DEPLOY_MULTI_CLUSTER") == "Y":
            logger.info("Setup XDCR between the running Gluu couchbase cluster and this one")

    def uninstall(self):
        """
        Uninstalls couchbase
        """
        logger.info("Deleting Couchbase...")
        self.kubernetes.delete_storage_class("couchbase-sc")
        self.kubernetes.delete_custom_resource("couchbaseclusters.couchbase.com")
        self.kubernetes.delete_validating_webhook_configuration("couchbase-operator-admission")
        self.kubernetes.delete_mutating_webhook_configuration("couchbase-operator-admission")
        self.kubernetes.delete_cluster_role_binding("couchbase-operator-admission")
        self.kubernetes.delete_cluster_role("couchbase-operator-admission")
        self.kubernetes.delete_role("couchbase-operator", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_secret("cb-auth", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_deployment_using_name("couchbase-operator", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_role_binding("couchbase-operator", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_service_account("couchbase-operator", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_service("couchbase-operator-admission", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_deployment_using_name("couchbase-operator-admission",
                                                     self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_service("couchbase-operator", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_custom_resource("couchbasebackuprestores.couchbase.com")
        self.kubernetes.delete_custom_resource("couchbasebackups.couchbase.com")
        self.kubernetes.delete_custom_resource("couchbasebuckets.couchbase.com")
        self.kubernetes.delete_custom_resource("couchbaseephemeralbuckets.couchbase.com")
        self.kubernetes.delete_custom_resource("couchbasereplications.couchbase.com")
        self.kubernetes.delete_custom_resource("couchbaserolebindings.couchbase.com")
        self.kubernetes.delete_custom_resource("couchbasegroups.couchbase.com")
        self.kubernetes.delete_custom_resource("couchbasememcachedbuckets.couchbase.com")
        self.kubernetes.delete_custom_resource("couchbaseusers.couchbase.com")

        self.kubernetes.delete_service_account("couchbase-operator-admission", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_secret("couchbase-operator-admission", self.settings.get("COUCHBASE_NAMESPACE"))
        self.kubernetes.delete_secret("couchbase-operator-tls", self.settings.get("COUCHBASE_NAMESPACE"))
        shutil.rmtree(Path("./couchbase-source-folder"), ignore_errors=True)
