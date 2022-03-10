"""
pygluu.kubernetes.postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles  Postgres operations
"""

from pygluu.kubernetes.helpers import get_logger, exec_cmd
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import SettingsHandler

logger = get_logger("gluu-postgres      ")


class Postgres(object):
    def __init__(self):
        self.settings = SettingsHandler()
        self.kubernetes = Kubernetes()
        self.timeout = 120

    def install_postgres(self):
        self.uninstall_postgres()
        self.kubernetes.create_namespace(name=self.settings.get("POSTGRES_NAMESPACE"),
                                         labels={"app": "postgres"})
        if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
            exec_cmd("helm repo add bitnami https://charts.bitnami.com/bitnami")
            exec_cmd("helm repo update")
            exec_cmd("helm install {} bitnami/postgresql "
                     "--set global.postgresql.auth.database={} "
                     "--set global.postgresql.auth.password={} "
                     "--set global.postgresql.auth.username={} "
                     "--namespace={}".format("postgresql",
                                             self.settings.get("JACKRABBIT_DATABASE"),
                                             self.settings.get("JACKRABBIT_PG_PASSWORD"),
                                             self.settings.get("JACKRABBIT_PG_USER"),
                                             self.settings.get("POSTGRES_NAMESPACE")))

        if self.settings.get("PERSISTENCE_BACKEND") == "sql" and self.settings.get("GLUU_SQL_DB_DIALECT") == "pgsql":
            self.kubernetes.create_namespace(name=self.settings.get("GLUU_SQL_DB_NAMESPACE"),
                                             labels={"app": "mysql"})
            exec_cmd("helm install {} bitnami/postgresql "
                     "--set global.postgresql.postgresqlDatabase={} "
                     "--set global.postgresql.postgresqlPassword={} "
                     "--set global.postgresql.postgresqlUsername={} "
                     "--namespace={}".format("gluu",
                                             self.settings.get("GLUU_SQL_DB_NAME"),
                                             self.settings.get("GLUU_SQL_DB_PASSWORD"),
                                             self.settings.get("GLUU_SQL_DB_USER"),
                                             self.settings.get("GLUU_SQL_DB_NAMESPACE")))

        if not self.settings.get("installer-settings.aws.lbType") == "alb":
            self.kubernetes.check_pods_statuses(self.settings.get("POSTGRES_NAMESPACE"), "app=postgres",
                                                self.timeout)

    def uninstall_postgres(self):
        logger.info("Removing gluu-postgres...")
        logger.info("Removing postgres...")
        exec_cmd("helm delete {} --namespace={}".format("sql",
                                                        self.settings.get("POSTGRES_NAMESPACE")))
        if self.settings.get("PERSISTENCE_BACKEND") == "sql" and self.settings.get("GLUU_SQL_DB_DIALECT") == "pgsql":
            exec_cmd("helm delete {} --namespace={}".format("gluu",
                                                            self.settings.get("GLUU_SQL_DB_NAMESPACE")))
