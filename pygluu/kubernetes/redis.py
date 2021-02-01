"""
pygluu.kubernetes.redis
~~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles Redis installation for testing.
"""

from pathlib import Path
from pygluu.kubernetes.yamlparser import Parser
from pygluu.kubernetes.helpers import get_logger, exec_cmd, analyze_storage_class
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import ValuesHandler


logger = get_logger("gluu-redis         ")


class Redis(object):
    def __init__(self):
        self.settings = ValuesHandler()
        self.kubernetes = Kubernetes()
        self.timeout = 120
        if "gke" in self.settings.get("installer-settings.volumeProvisionStrategy"):
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
        self.kubernetes.create_namespace(name=self.settings.get("installer-settings.redis.namespace"), labels={"app": "redis"})
        if self.settings.get("CN_DEPLOYMENT_ARCH") != "local":
            redis_storage_class = Path("./redis/storageclasses.yaml")
            analyze_storage_class(self.settings, redis_storage_class)
            self.kubernetes.create_objects_from_dict(redis_storage_class)

        redis_configmap = Path("./redis/configmaps.yaml")
        redis_conf_parser = Parser(redis_configmap, "ConfigMap")
        redis_conf_parser["metadata"]["namespace"] = self.settings.get("installer-settings.redis.namespace")
        redis_conf_parser.dump_it()
        self.kubernetes.create_objects_from_dict(redis_configmap)

        redis_yaml = Path("./redis/redis.yaml")
        redis_parser = Parser(redis_yaml, "Redis")
        redis_parser["spec"]["cluster"]["master"] = self.settings.get("installer-settings.redis.masterNodes")
        redis_parser["spec"]["cluster"]["replicas"] = self.settings.get("installer-settings.redis.nodesPerMaster")
        redis_parser["spec"]["monitor"]["prometheus"]["namespace"] = self.settings.get("installer-settings.redis.namespace")
        if self.settings.get("CN_DEPLOYMENT_ARCH") == "local":
            redis_parser["spec"]["storage"]["storageClassName"] = "openebs-hostpath"
        redis_parser["metadata"]["namespace"] = self.settings.get("installer-settings.redis.namespace")
        if self.settings.get("global.storageClass.provisioner") in ("microk8s.io/hostpath", "k8s.io/minikube-hostpath"):
            del redis_parser["spec"]["podTemplate"]["spec"]["resources"]
        redis_parser.dump_it()
        self.kubernetes.create_namespaced_custom_object(filepath=redis_yaml,
                                                        group="kubedb.com",
                                                        version="v1alpha1",
                                                        plural="redises",
                                                        namespace=self.settings.get("installer-settings.redis.namespace"))

        if not self.settings.get("installer-settings.aws.lbType") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("installer-settings.namespace"), "app=redis-cluster", self.timeout)

    def uninstall_redis(self):
        logger.info("Removing gluu-redis-cluster...")
        logger.info("Removing redis...")
        redis_yaml = Path("./redis/redis.yaml")
        self.kubernetes.delete_namespaced_custom_object(filepath=redis_yaml,
                                                        group="kubedb.com",
                                                        version="v1alpha1",
                                                        plural="redises",
                                                        namespace=self.settings.get("installer-settings.redis.namespace"))
        self.kubernetes.delete_storage_class("redis-sc")
        self.kubernetes.delete_service("kubedb", self.settings.get("installer-settings.redis.namespace"))

