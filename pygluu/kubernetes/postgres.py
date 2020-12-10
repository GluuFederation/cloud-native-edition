"""
pygluu.kubernetes.helm
~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles  Postgres operations
"""

from pathlib import Path
from pygluu.kubernetes.yamlparser import Parser
from pygluu.kubernetes.helpers import get_logger, analyze_storage_class
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import SettingsHandler
import time
import base64

logger = get_logger("gluu-postgres      ")


class Postgres(object):
    def __init__(self):
        self.settings = SettingsHandler()
        self.kubernetes = Kubernetes()
        self.timeout = 120

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

    def patch_or_install_postgres(self):
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

    def install_postgres(self):
        self.uninstall_postgres()
        self.kubernetes.create_namespace(name=self.settings.get("POSTGRES_NAMESPACE"), labels={"app": "postgres"})
        self.create_patch_secret_init_sql()
        if self.settings.get("DEPLOYMENT_ARCH") != "local":
            postgres_storage_class = Path("./postgres/storageclasses.yaml")
            analyze_storage_class(self.settings, postgres_storage_class)
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
