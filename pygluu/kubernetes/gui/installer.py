import os
import threading
import time
import traceback
from pathlib import Path
from queue import Queue
from pygtail import Pygtail

from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.helm import Helm
from pygluu.kubernetes.helpers import get_logger
from pygluu.kubernetes.kustomize import Kustomize
from pygluu.kubernetes.settings import SettingsHandler

logger = get_logger("gluu-gui        ")


class InstallHandler(object):
    def __init__(self):
        self.target = None
        self.timeout = 120
        self.queue = Queue()
        self.settings = SettingsHandler()
        self.thread = None

    def run_install(self):
        log_offset = Path("./setup.log.offset")
        if log_offset.exists():
            os.unlink('./setup.log.offset')
        Pygtail("./setup.log", paranoid=True).readlines()

        self.thread = threading.Thread(target=self.do_installation, args=(self.target,))
        self.thread.daemon = True
        self.thread.start()

    def run_uninstall(self):
        log_offset = Path("./setup.log.offset")
        if log_offset.exists():
            os.unlink('./setup.log.offset')

        self.thread = threading.Thread(target=self.do_uninstall, args=(self.target,))
        self.thread.daemon = True
        self.thread.start()

    def do_installation(self, target):
        complete_message = 'Installation Completed'
        try:
            if target == "install":
                self.queue.put(('Preparing Installation', 'ONPROGRESS'))
                kustomize = Kustomize(self.timeout)
                kustomize.uninstall()
                if self.settings.get("INSTALL_REDIS") == "Y" or \
                        self.settings.get("INSTALL_GLUU_GATEWAY") == "Y" or \
                        self.settings.get("JACKRABBIT_CLUSTER") == "Y":
                    self.queue.put(('Install Kube-DB', 'ONPROGRESS'))
                    helm = Helm()
                    helm.uninstall_kubedb()
                    helm.install_kubedb()
                self.queue.put(('Installation in progress', 'ONPROGRESS'))
                kustomize.install()

            elif target == "install-ldap-backup":
                kustomize = Kustomize(self.timeout)
                kustomize.setup_backup_ldap()

            elif target == "install-kubedb":
                helm = Helm()
                helm.install_kubedb()

            elif target == "install-gg-dbmode":
                kustomize = Kustomize(self.timeout)
                kustomize.install_gluu_gateway_dbmode()

            elif target == "install-couchbase":
                couchbase = Couchbase()
                couchbase.install()

            elif target == "install-couchbase-backup":
                couchbase = Couchbase()
                couchbase.setup_backup_couchbase()

            elif target == "helm-install":
                helm = Helm()

                if self.settings.get("INSTALL_REDIS") == "Y" or \
                        self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
                    helm.install_kubedb()

                if self.settings.get("INSTALL_REDIS") == "Y":
                    kustomize = Kustomize(self.timeout)
                    kustomize.uninstall_redis()
                    kustomize.deploy_redis()

                helm.install_gluu()

            elif target == "helm-install-gg-dbmode":
                kustomize = Kustomize(self.timeout)
                kustomize.deploy_postgres()
                helm = Helm()
                helm.install_gluu_gateway_dbmode()
                helm.install_gluu_gateway_ui()

            elif target == "helm-install-gluu":
                helm = Helm()
                helm.uninstall_gluu()
                helm.install_gluu(install_ingress=False)

            elif target == "restore":
                self.queue.put(('Restoring Gluu', 'ONPROGRESS'))
                kustomize = Kustomize(self.timeout)
                kustomize.copy_configs_before_restore()
                kustomize.uninstall(restore=True)
                kustomize.install(install_couchbase=False, restore=True)
                complete_message = "Restoring gluu has been completed"

            elif target == "upgrade":
                self.queue.put(('Upgrading Gluu', 'ONPROGRESS'))
                logger.info("Starting upgrade...")
                kustomize = Kustomize(self.timeout)
                kustomize.upgrade()
                complete_message = "Upgrading gluu has been completed"

            self.queue.put((complete_message, 'COMPLETED'))
            os.remove('./setup.log.offset')
        except Exception as exc:
            if self.queue:
                self.queue.put(("ERROR", str(traceback.format_exc()), "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())
                logger.debug(f"Uncaught error={exc}")

    def do_uninstall(self, target):
        try:
            if target == "uninstall":
                logger.info("Removing all Gluu resources...")
                self.queue.put(('Uninstall in progress', 'ONPROGRESS'))
                kustomize = Kustomize(self.timeout)
                kustomize.uninstall()
                if self.settings.get("INSTALL_REDIS") == "Y" or \
                        self.settings.get("INSTALL_GLUU_GATEWAY") == "Y":
                    self.queue.put(('Uninstall kube-db', 'ONPROGRESS'))
                    helm = Helm()
                    helm.uninstall_kubedb()

            elif target == "uninstall-gg-dbmode":
                self.queue.put(('Uninstallation in progress', 'ONPROGRESS'))
                kustomize = Kustomize(self.timeout)
                kustomize.uninstall_kong()
                kustomize.uninstall_gluu_gateway_ui()

            elif target == "uninstall-couchbase":
                self.queue.put(('Uninstallation in progress', 'ONPROGRESS'))
                couchbase = Couchbase()
                couchbase.uninstall()

            elif target == "helm-uninstall":
                kustomize = Kustomize(self.timeout)
                helm = Helm()
                self.queue.put(('Uninstall gluu', 'ONPROGRESS'))
                helm.uninstall_gluu()
                self.queue.put(('Uninstall nginx ingress', 'ONPROGRESS'))
                helm.uninstall_nginx_ingress()
                self.queue.put(('Uninstall gluu gateway db mode', 'ONPROGRESS'))
                helm.uninstall_gluu_gateway_dbmode()
                self.queue.put(('Uninstall gluu gateway ui', 'ONPROGRESS'))
                helm.uninstall_gluu_gateway_ui()
                logger.info("Please wait...")
                time.sleep(30)
                self.queue.put(('Uninstallation in progress', 'ONPROGRESS'))
                kustomize.uninstall()
                self.queue.put(('Uninstall kube-db', 'ONPROGRESS'))
                helm.uninstall_kubedb()

            elif target == "helm-uninstall-gg-dbmode":
                self.queue.put(('Uninstallation in progress', 'ONPROGRESS'))
                kustomize = Kustomize(self.timeout)
                kustomize.uninstall_postgres()
                helm = Helm()
                helm.uninstall_gluu_gateway_dbmode()
                helm.uninstall_gluu_gateway_ui()

            elif target == "helm-uninstall-gluu":
                helm = Helm()
                self.queue.put(('Uninstall in progress', 'ONPROGRESS'))
                helm.uninstall_gluu()

            self.queue.put(('Uninstall Completed', 'COMPLETED'))

            log_offset = Path("./setup.log.offset")
            if log_offset.exists():
                os.unlink("./setup.log.offset")
        except Exception as exc:
            if self.queue:
                self.queue.put(("ERROR", "", str(traceback.format_exc())))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())
                logger.debug(f"Uncaught error={exc}")
