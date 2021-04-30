"""
pygluu.kubernetes.postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles  Postgres operations
"""

from psycopg2 import sql
from pygluu.kubernetes.helpers import get_logger, exec_cmd
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import ValuesHandler
import time
import base64

logger = get_logger("gluu-postgres      ")


class Postgres(object):
    def __init__(self):
        self.settings = ValuesHandler()
        self.kubernetes = Kubernetes()
        self.timeout = 120

    @property
    def generate_postgres_init_sql(self):
        services_using_postgres = []
        if self.settings.get("installer-settings.jackrabbit.clusterMode"):
            services_using_postgres.append("JACKRABBIT")
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
                                                          namespace=self.settings.get("installer-settings.postgres.install"),
                                                          literal="data.sql",
                                                          value_of_literal=encoded_postgers_init_string)

    def patch_or_install_postgres(self):
        # Jackrabbit Cluster would have installed postgres
        if self.settings.get("installer-settings.jackrabbit.clusterMode"):
            self.install_postgres()
        else:
            self.create_patch_secret_init_sql()
            logger.info("Restarting postgres...please wait 2mins..")
            self.kubernetes.patch_namespaced_stateful_set_scale(name="postgres",
                                                                replicas=0,
                                                                namespace=self.settings.get("installer-settings.postgres.install"))
            time.sleep(120)
            self.kubernetes.patch_namespaced_stateful_set_scale(name="postgres",
                                                                replicas=3,
                                                                namespace=self.settings.get("installer-settings.postgres.install"))
            self.kubernetes.check_pods_statuses(self.settings.get("installer-settings.postgres.install"), "app=postgres", self.timeout)

    def install_postgres(self):
        self.uninstall_postgres()
        self.kubernetes.create_namespace(name=self.settings.get("installer-settings.postgres.install"), 
                                         labels={"app": "postgres"})

        exec_cmd("helm repo add bitnami https://charts.bitnami.com/bitnami")
        exec_cmd("helm repo update")
        exec_cmd("helm install {} bitnami/postgresql "
                 "--set global.postgresql.postgresqlDatabase={} "
                 "--set --host={} "
                 "--set usePasswordFile={} "
                 "--set global.postgresql.servicePort={} "
                 "--set global.postgresql.postgresqlUsername={} "
                 "--namespace={}".format("postgresql",
                                         self.settings.get("config.configmap.cnJackrabbitPostgresDatabaseName"),
                                         self.settings.get("config.configmap.cnJackrabbitPostgresHost"),
                                         self.settings.get("config.configmap.cnJackrabbitPostgresPasswordFile"),
                                         self.settings.get("config.configmap.cnJackrabbitPostgresPort"),
                                         self.settings.get("config.configmap.cnJackrabbitPostgresUser"),
                                         self.settings.get("installer-settings.postgres.namespace")))

        if not self.settings.get("installer-settings.aws.lbType") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("installer-settings.postgres.install"), "app=postgres", 
                                                self.timeout)

    def uninstall_postgres(self):
        logger.info("Removing gluu-postgres...")
        logger.info("Removing postgresql...")
        exec_cmd("helm delete {} --namespace={}".format("postgresql",
                                                        self.settings.get("installer-settings.postgres.namespace")))
