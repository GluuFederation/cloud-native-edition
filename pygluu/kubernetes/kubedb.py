"""
pygluu.kubernetes.kubedb
~~~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles KubeDB
"""

from pathlib import Path
from pygluu.kubernetes.helpers import get_logger, exec_cmd
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import SettingsHandler
import time

logger = get_logger("gluu-kubedb        ")


class Kubedb(object):
    def __init__(self):
        self.values_file = Path("./helm/gluu/values.yaml").resolve()
        self.upgrade_values_file = Path("./helm/gluu-upgrade/values.yaml").resolve()
        self.settings = SettingsHandler()
        self.kubernetes = Kubernetes()
        self.ldap_backup_release_name = self.settings.get('CN_HELM_RELEASE_NAME') + "-ldap-backup"
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

    def install_kubedb(self):
        self.uninstall_kubedb()
        self.kubernetes.create_namespace(name="gluu-kubedb", labels={"app": "kubedb"})
        try:
            exec_cmd("helm repo add appscode https://charts.appscode.com/stable/")
            exec_cmd("helm repo update")
            exec_cmd("helm install kubedb-operator appscode/kubedb  --version v0.13.0-rc.0 "
                     "--namespace gluu-kubedb")
            self.kubernetes.check_pods_statuses("gluu-kubedb", "app=kubedb")
            exec_cmd("helm install kubedb-catalog appscode/kubedb-catalog  --version v0.13.0-rc.0 "
                     "--namespace gluu-kubedb")
        except FileNotFoundError:
            logger.error("Helm v3 is not installed. Please install it to continue "
                         "https://helm.sh/docs/intro/install/")
            raise SystemExit(1)

    def uninstall_kubedb(self):
        logger.info("Deleting KubeDB...This may take a little while.")
        try:
            exec_cmd("helm repo add appscode https://charts.appscode.com/stable/")
            exec_cmd("helm repo update")
            exec_cmd("helm delete kubedb-operator --namespace gluu-kubedb")
            exec_cmd("helm delete kubedb-catalog --namespace gluu-kubedb")
            time.sleep(20)
        except FileNotFoundError:
            logger.error("Helm v3 is not installed. Please install it to continue "
                         "https://helm.sh/docs/intro/install/")
            raise SystemExit(1)
