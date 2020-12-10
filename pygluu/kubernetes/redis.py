"""
pygluu.kubernetes.helm
~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles Redis installation for testing.
"""

from pathlib import Path
from pygluu.kubernetes.yamlparser import Parser
from pygluu.kubernetes.helpers import get_logger, exec_cmd, analyze_storage_class
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import SettingsHandler


logger = get_logger("gluu-redis         ")


class Redis(object):
    def __init__(self):
        self.settings = SettingsHandler()
        self.kubernetes = Kubernetes()
        self.timeout = 120
        if self.settings.get("DEPLOYMENT_ARCH") == "gke":
            user_account, stderr, retcode = exec_cmd("gcloud config get-value core/account")
            user_account = str(user_account, "utf-8").strip()

            user, stderr, retcode = exec_cmd("whoami")
            user = str(user, "utf-8").strip()
            cluster_role_binding_name = "cluster-admin-{}".format(user)
            self.kubernetes.create_cluster_role_binding(cluster_role_binding_name=cluster_role_binding_name,
                                                        user_name=user_account,
                                                        cluster_role_name="cluster-admin")

    def install_redis(self):
        self.uninstall_redis()
        self.kubernetes.create_namespace(name=self.settings.get("REDIS_NAMESPACE"), labels={"app": "redis"})
        if self.settings.get("DEPLOYMENT_ARCH") != "local":
            redis_storage_class = Path("./redis/storageclasses.yaml")
            analyze_storage_class(self.settings, redis_storage_class)
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
        if self.settings.get("DEPLOYMENT_ARCH") == "local":
            redis_parser["spec"]["storage"]["storageClassName"] = "openebs-hostpath"
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
            self.kubernetes.check_pods_statuses(self.settings.get("CN_NAMESPACE"), "app=redis-cluster", self.timeout)

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

