"""
pygluu.kubernetes.postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles  Postgres operations
"""

from pygluu.kubernetes.helpers import get_logger, exec_cmd
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import ValuesHandler

logger = get_logger("gluu-postgres      ")


class Postgres(object):
    def __init__(self):
        self.settings = ValuesHandler()
        self.kubernetes = Kubernetes()
        self.timeout = 120

    def install_postgres(self):
        self.uninstall_postgres()
        self.kubernetes.create_namespace(name=self.settings.get("installer-settings.postgres.namespace"),
                                         labels={"app": "postgres"})

        exec_cmd("helm repo add bitnami https://charts.bitnami.com/bitnami")
        exec_cmd("helm repo update")
        exec_cmd("helm install {} bitnami/postgresql "
                 "--set global.postgresql.postgresqlDatabase={} "
                 "--set global.postgresql.postgresqlPassword={} "
                 "--set global.postgresql.servicePort={} "
                 "--set global.postgresql.postgresqlUsername={} "
                 "--namespace={}".format("postgresql",
                                         self.settings.get("config.configmap.cnJackrabbitPostgresDatabaseName"),
                                         self.settings.get("jackrabbit.secrets.cnJackrabbitPostgresPassword"),
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
