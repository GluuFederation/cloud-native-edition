"""
pygluu.kubernetes.kustomize
~~~~~~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
"""
import base64
import contextlib
import shutil
import time
from pathlib import Path

from pygluu.kubernetes.helpers import get_logger, copy, exec_cmd, ssh_and_remove
from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.yamlparser import Parser
from pygluu.kubernetes.settings import SettingsHandler

logger = get_logger("gluu-kustomize     ")


class Kustomize(object):
    def __init__(self, timeout=300):

        self.settings = SettingsHandler()
        self.all_apps = self.settings.get("ENABLED_SERVICES_LIST")
        self.kubernetes = Kubernetes()
        self.timeout = timeout
        self.kubectl = self.detect_kubectl
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

    def kustomize_gluu_upgrade(self):
        self.update_kustomization_yaml(kustomization_yaml="upgrade/base/kustomization.yaml",
                                       namespace=self.settings.get("CN_NAMESPACE"),
                                       image_name_key="UPGRADE_IMAGE_NAME",
                                       image_tag_key="UPGRADE_IMAGE_TAG")
        command = self.kubectl + " kustomize upgrade/base"
        exec_cmd(command, output_file=self.gluu_upgrade_yaml)
        upgrade_cm_parser = Parser(self.gluu_upgrade_yaml, "ConfigMap")
        upgrade_cm_parser["data"]["DOMAIN"] = self.settings.get("CN_FQDN")
        upgrade_cm_parser["data"]["CN_CACHE_TYPE"] = self.settings.get("CN_CACHE_TYPE")
        upgrade_cm_parser["data"]["CN_COUCHBASE_URL"] = self.settings.get("COUCHBASE_URL")
        upgrade_cm_parser["data"]["CN_COUCHBASE_USER"] = self.settings.get("COUCHBASE_USER")
        upgrade_cm_parser["data"]["CN_COUCHBASE_SUPERUSER"] = self.settings.get("COUCHBASE_SUPERUSER")
        upgrade_cm_parser["data"]["CN_PERSISTENCE_LDAP_MAPPING"] = self.settings.get("HYBRID_LDAP_HELD_DATA")
        upgrade_cm_parser["data"]["CN_PERSISTENCE_TYPE"] = self.settings.get("PERSISTENCE_BACKEND")
        upgrade_cm_parser["data"]["CN_CONFIG_KUBERNETES_NAMESPACE"] = self.settings.get("CN_NAMESPACE")
        upgrade_cm_parser["data"]["CN_SECRET_KUBERNETES_NAMESPACE"] = self.settings.get("CN_NAMESPACE")
        upgrade_cm_parser.dump_it()

        upgrade_job_parser = Parser(self.gluu_upgrade_yaml, "Job")
        upgrade_job_parser["spec"]["template"]["spec"]["containers"][0]["args"] = \
            ["--source", self.settings.get("CN_VERSION"),
             "--target", self.settings.get("CN_UPGRADE_TARGET_VERSION")]
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
            gg_ui_ingress_parser["spec"]["tls"][0]["hosts"][0] = self.settings.get("CN_FQDN")
            gg_ui_ingress_parser["spec"]["rules"][0]["host"] = self.settings.get("CN_FQDN")
            gg_ui_ingress_parser.dump_it()
            self.remove_resources(self.gg_ui_yaml, "Deployment")
            self.adjust_yamls_for_fqdn_status[self.gg_ui_yaml] = "Deployment"

    def prepare_alb(self):
        services = [self.auth_server_yaml, self.oxtrust_yaml, self.casa_yaml,
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
        ingress_parser["spec"]["rules"][0]["host"] = self.settings.get("CN_FQDN")
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

    def deploy_alb(self):
        shutil.copy(Path("./alb/ingress.yaml"), self.output_yaml_directory.joinpath("ingress.yaml"))
        self.kubernetes.create_objects_from_dict(self.output_yaml_directory.joinpath("ingress.yaml"),
                                                 self.settings.get("CN_NAMESPACE"))
        if self.settings.get("IS_CN_FQDN_REGISTERED") != "Y":
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
        client_api_server_url = "https://{}.{}.svc.cluster.local:8443".format(
            self.settings.get("CLIENT_API_APPLICATION_KEYSTORE_CN"), self.settings.get("CN_NAMESPACE"))
        gg_ui_cm_parser = Parser(self.gg_ui_yaml, "ConfigMap")
        gg_ui_cm_parser["data"]["DB_USER"] = self.settings.get("GLUU_GATEWAY_UI_PG_USER")
        gg_ui_cm_parser["data"]["KONG_ADMIN_URL"] = "https://kong-admin.{}.svc.cluster.local:8444".format(
            self.settings.get("KONG_NAMESPACE"))
        gg_ui_cm_parser["data"]["DB_HOST"] = self.settings.get("POSTGRES_URL")
        gg_ui_cm_parser["data"]["DB_DATABASE"] = self.settings.get("GLUU_GATEWAY_UI_DATABASE")
        gg_ui_cm_parser["data"]["CLIENT_API_URL"] = client_api_server_url
        # Register new client if one was not provided
        if not gg_ui_cm_parser["data"]["CLIENT_ID"] or \
                not gg_ui_cm_parser["data"]["CLIENT_API_ID"] or \
                not gg_ui_cm_parser["data"]["CLIENT_SECRET"]:
            client_api_id, client_id, client_secret = register_op_client(self.settings.get("CN_NAMESPACE"),
                                                                         "konga-client",
                                                                         self.settings.get("CN_FQDN"),
                                                                         client_api_server_url)
            gg_ui_cm_parser["data"]["CLIENT_API_ID"] = client_api_id
            gg_ui_cm_parser["data"]["CLIENT_ID"] = client_id
            gg_ui_cm_parser["data"]["CLIENT_SECRET"] = client_secret
        gg_ui_cm_parser["data"]["OP_SERVER_URL"] = "https://" + self.settings.get("CN_FQDN")

        gg_ui_cm_parser["data"]["GG_HOST"] = self.settings.get("CN_FQDN") + "/gg-ui/"
        gg_ui_cm_parser["data"]["GG_UI_REDIRECT_URL_HOST"] = self.settings.get("CN_FQDN") + "/gg-ui/"

        gg_ui_cm_parser.dump_it()

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

    def patch_or_deploy_postgres(self):

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

    def deploy_postgres(self):
        self.uninstall_postgres()
        self.kubernetes.create_namespace(name=self.settings.get("POSTGRES_NAMESPACE"), labels={"app": "postgres"})
        self.create_patch_secret_init_sql()
        if self.settings.get("DEPLOYMENT_ARCH") != "local":
            postgres_storage_class = Path("./postgres/storageclasses.yaml")
            self.analyze_storage_class(postgres_storage_class)
            self.kubernetes.create_objects_from_dict(postgres_storage_class)

        postgres_yaml = Path("./postgres/postgres.yaml")
        postgres_parser = Parser(postgres_yaml, "Postgres")
        postgres_parser["spec"]["replicas"] = self.settings.get("POSTGRES_REPLICAS")
        postgres_parser["spec"]["monitor"]["prometheus"]["namespace"] = self.settings.get("POSTGRES_NAMESPACE")
        if self.settings.get("DEPLOYMENT_ARCH") == "local":
            postgres_parser["spec"]["storage"]["storageClassName"] = "openebs-hostpath"
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
        if self.settings.get("IS_CN_FQDN_REGISTERED") != "Y":
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
        self.patch_or_deploy_postgres()
        self.deploy_kong()
        self.kustomize_gluu_gateway_ui()
        self.adjust_fqdn_yaml_entries()
        self.deploy_gluu_gateway_ui()

    def deploy_redis(self):
        self.uninstall_redis()
        self.kubernetes.create_namespace(name=self.settings.get("REDIS_NAMESPACE"), labels={"app": "redis"})
        if self.settings.get("DEPLOYMENT_ARCH") != "local":
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

    def copy_configs_before_restore(self):
        self.gluu_secret = self.kubernetes.read_namespaced_secret("gluu", self.settings.get("CN_NAMESPACE")).data
        self.gluu_config = self.kubernetes.read_namespaced_configmap("gluu", self.settings.get("CN_NAMESPACE")).data

    def save_a_copy_of_config(self):
        self.kubernetes.patch_or_create_namespaced_secret(name="secret-params", literal=None, value_of_literal=None,
                                                          namespace=self.settings.get("CN_NAMESPACE"),
                                                          data=self.gluu_secret)
        self.kubernetes.patch_or_create_namespaced_configmap(name="config-params",
                                                             namespace=self.settings.get("CN_NAMESPACE"),
                                                             data=self.gluu_config)

    def mount_config(self):
        self.kubernetes.patch_or_create_namespaced_secret(name="gluu", literal=None, value_of_literal=None,
                                                          namespace=self.settings.get("CN_NAMESPACE"),
                                                          data=self.gluu_secret)
        self.kubernetes.patch_or_create_namespaced_configmap(name="gluu",
                                                             namespace=self.settings.get("CN_NAMESPACE"),
                                                             data=self.gluu_config)

    def install(self, install_couchbase=True, restore=False):
        if not restore:
            labels = {"app": "gluu"}
            if self.settings.get("USE_ISTIO") == "Y":
                labels = {"app": "gluu", "istio-injection": "enabled"}
            self.kubernetes.create_namespace(name=self.settings.get("CN_NAMESPACE"), labels=labels)
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
            self.setup_tls(namespace=self.settings.get("CN_NAMESPACE"))

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

        if self.settings.get("IS_CN_FQDN_REGISTERED") != "Y":
            if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "local"):
                self.kubernetes = Kubernetes()
                self.deploy_update_lb_ip()

        self.kubernetes = Kubernetes()
        self.deploy_auth_server()

        if self.settings.get("ENABLE_FIDO2") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_fido2()

        if self.settings.get("ENABLE_SCIM") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_scim()

        if self.settings.get("ENABLE_CLIENT_API") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_client_api()

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

        if self.settings.get("ENABLE_AUTH_SERVER_KEY_ROTATE") == "Y":
            self.kubernetes = Kubernetes()
            self.deploy_auth_server_key_rotation()
            if restore:
                self.mount_config()

        if self.settings.get("ENABLE_RADIUS") == "Y":
            self.deploy_radius()

        if self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
            self.kubernetes = Kubernetes()
            self.install_gluu_gateway_dbmode()

    def uninstall(self, restore=False):
        gluu_service_names = ["casa", "cr-rotate", "opendj", "auth-server", "oxpassport",
                              "oxshibboleth", "oxtrust", "radius", "client-api",
                              "jackrabbit", "fido2", "scim", "configuration-manager-load-job"]
        gluu_storage_class_names = ["opendj-sc", "jackrabbit-sc"]
        nginx_service_name = "ingress-nginx"
        gluu_deployment_app_labels = ["app=casa", "app=auth-server", "app=fido2", "app=scim", "app=client-api",
                                      "app=oxpassport", "app=radius", "app=auth-server-key-rotation", "app=jackrabbit"]
        nginx_deployemnt_app_name = "nginx-ingress-controller"
        stateful_set_labels = ["app=opendj", "app=oxtrust", "app=oxshibboleth", "app=jackrabbit"]
        jobs_labels = ["app=configuration-manager-load", "app=persistence-load", "app=gluu-upgrade"]
        secrets = ["clientApikeystorecm", "gluu", "tls-certificate",
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
                                          "gluu-ingress-fido-u2f-configuration", "gluu-ingress", "gluu-ingress-scim",
                                          "gluu-ingress-stateful", "gluu-casa", "gluu-ingress-fido2-configuration"]
        network_policies = ["client-api-policy"]
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
            self.kubernetes.delete_service(service, self.settings.get("CN_NAMESPACE"))
        for network_policy in network_policies:
            self.kubernetes.delete_network_policy(network_policy, self.settings.get("CN_NAMESPACE"))
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
        self.kubernetes.delete_cronjob(self.settings.get("CN_NAMESPACE"), "app=auth-server-key-rotation")
        for deployment in gluu_deployment_app_labels:
            self.kubernetes.delete_deployment_using_label(self.settings.get("CN_NAMESPACE"), deployment)
        if not restore:
            self.kubernetes.delete_deployment_using_name(nginx_deployemnt_app_name, "ingress-nginx")
        for stateful_set in stateful_set_labels:
            self.kubernetes.delete_stateful_set(self.settings.get("CN_NAMESPACE"), stateful_set)
        for job in jobs_labels:
            self.kubernetes.delete_job(self.settings.get("CN_NAMESPACE"), job)
        for secret in secrets:
            self.kubernetes.delete_secret(secret, self.settings.get("CN_NAMESPACE"))
        if not restore:
            for secret in cb_secrets:
                self.kubernetes.delete_secret(secret, self.settings.get("CN_NAMESPACE"))
        self.kubernetes.delete_daemon_set(self.settings.get("CN_NAMESPACE"), daemon_set_label)
        for config_map in gluu_config_maps_names:
            self.kubernetes.delete_config_map_using_name(config_map, self.settings.get("CN_NAMESPACE"))
        if not restore:
            for config_map in nginx_config_maps_names:
                self.kubernetes.delete_config_map_using_name(config_map, "ingress-nginx")
        for cm_pv_pvc in all_labels:
            self.kubernetes.delete_config_map_using_label(self.settings.get("CN_NAMESPACE"), cm_pv_pvc)
            self.kubernetes.delete_persistent_volume(cm_pv_pvc)
            self.kubernetes.delete_persistent_volume_claim(self.settings.get("CN_NAMESPACE"), cm_pv_pvc)
        for storage_class in gluu_storage_class_names:
            self.kubernetes.delete_storage_class(storage_class)

        if not restore:
            self.kubernetes.delete_role("gluu-role", self.settings.get("CN_NAMESPACE"))
            self.kubernetes.delete_role_binding("gluu-rolebinding", self.settings.get("CN_NAMESPACE"))
            self.kubernetes.delete_role(nginx_roles_name, "ingress-nginx")
            self.kubernetes.delete_cluster_role_binding("gluu-rolebinding")
            self.kubernetes.delete_cluster_role_binding(gluu_cluster_role_bindings_name)
            self.kubernetes.delete_role_binding(nginx_role_bindings_name, "ingress-nginx")
            self.kubernetes.delete_cluster_role_binding(nginx_cluster_role_bindings_name)
            self.kubernetes.delete_service_account(nginx_service_account_name, "ingress-nginx")
            self.kubernetes.delete_cluster_role(nginx_cluster_role_name)
            for extension in nginx_ingress_extensions_names:
                self.kubernetes.delete_ingress(extension, self.settings.get("CN_NAMESPACE"))
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
