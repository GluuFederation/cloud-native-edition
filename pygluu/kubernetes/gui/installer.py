import os
import sys
import traceback
import threading
import time
from pathlib import Path
from queue import Queue
from pygtail import Pygtail
from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.helm import Helm
from pygluu.kubernetes.helpers import get_logger
from pygluu.kubernetes.kustomize import Kustomize
from .extensions import gluu_settings

logger = get_logger("gluu-gui        ")


class InstallHandler(object):
    def __init__(self, target, timeout=120):
        self.target = target
        self.timeout = timeout
        self.queue = Queue()
        self.thread = None
        self.event = threading.Event()

    @staticmethod
    def initialize():
        # remove setup log offset and set new offset
        log_offset = Path("./setup.log.offset")
        if log_offset.exists():
            os.unlink('./setup.log.offset')
        Pygtail("./setup.log", paranoid=True).readlines()

    def run(self):
        self.initialize()
        try:
            func_target = getattr(self, self.target.replace("-", "_"))
            self.thread = threading.Thread(target=func_target)
            self.thread.daemon = True
            self.thread.start()
        except KeyboardInterrupt:
            self.event.set()
            sys.exit(1)

    def install(self):
        try:
            self.queue.put(('Preparing installation', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.uninstall()
            if gluu_settings.db.get("INSTALL_REDIS") == "Y" or \
                    gluu_settings.db.get("INSTALL_GLUU_GATEWAY") == "Y" or \
                    gluu_settings.db.get("JACKRABBIT_CLUSTER") == "Y":
                helm = Helm()
                helm.uninstall_kubedb()
                helm.install_kubedb()
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            kustomize.install()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def install_ldap_backup(self):
        try:
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.setup_backup_ldap()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def uninstall(self):
        try:
            logger.info("Removing all Gluu resources...")
            self.queue.put(('Uninstalling...', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.uninstall()
            if gluu_settings.db.get("INSTALL_REDIS") == "Y" or gluu_settings.db.get(
                    "INSTALL_GLUU_GATEWAY") == "Y":
                helm = Helm()
                helm.uninstall_kubedb()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def upgrade(self):
        try:
            # New feature in 4.2 compared to 4.1 and hence if enabled should make
            # sure kubedb is installed.
            self.queue.put(('Preparing upgrade...', 'ONPROGRESS'))
            if gluu_settings.db.get("JACKRABBIT_CLUSTER") == "Y":
                helm = Helm()
                helm.uninstall_kubedb()
                helm.install_kubedb()

            logger.info("Starting upgrade...")
            self.queue.put(('Upgrading...', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.upgrade()
            self.queue.put(('Upgrade is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def upgrade_values_yaml(self):
        try:
            # New feature in 4.2 compared to 4.1 and hence if enabled should make
            # sure kubedb is installed.
            helm = Helm()
            if gluu_settings.db.get("JACKRABBIT_CLUSTER") == "Y":
                helm.uninstall_kubedb()
                helm.install_kubedb()

            helm = Helm()
            logger.info("Patching values.yaml for helm upgrade...")
            self.queue.put(('Upgrading...', 'ONPROGRESS'))
            helm.analyze_global_values()
            logger.info(
                "Please find your patched values.yaml at the location ./helm/gluu/values.yaml."
                "Continue with the steps found at https://gluu.org/docs/gluu-server/4.2/upgrade/#helm")
            self.queue.put(('Upgrade is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def restore(self):
        try:
            self.queue.put(('Restoring...', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.copy_configs_before_restore()
            kustomize.uninstall(restore=True)
            kustomize.install(install_couchbase=False, restore=True)
            self.queue.put(('Restoring is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def install_couchbase(self):
        try:
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            couchbase = Couchbase()
            couchbase.install()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def install_couchbase_backup(self):
        try:
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            couchbase = Couchbase()
            couchbase.setup_backup_couchbase()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def uninstall_couchbase(self):
        try:
            self.queue.put(('Uninstalling...', 'ONPROGRESS'))
            couchbase = Couchbase()
            couchbase.uninstall()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def install_gg_dbmode(self):
        try:
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.install_gluu_gateway_dbmode()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def install_kubedb(self):
        try:
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            helm = Helm()
            helm.install_kubedb()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def uninstall_gg_dbmode(self):
        try:
            self.queue.put(('Uninstalling...', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.uninstall_kong()
            kustomize.uninstall_gluu_gateway_ui()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def helm_install(self):
        try:
            self.queue.put(('Preparing for installation', 'ONPROGRESS'))
            helm = Helm()
            if gluu_settings.db.get("INSTALL_REDIS") == "Y" or \
                    gluu_settings.db.get("INSTALL_GLUU_GATEWAY") == "Y" or \
                    gluu_settings.db.get("JACKRABBIT_CLUSTER") == "Y":
                helm.uninstall_kubedb()
                helm.install_kubedb()
            if gluu_settings.db.get("JACKRABBIT_CLUSTER") == "Y":
                kustomize = Kustomize(self.timeout)
                kustomize.deploy_postgres()
            if gluu_settings.db.get("INSTALL_REDIS") == "Y":
                kustomize = Kustomize(self.timeout)
                kustomize.uninstall_redis()
                kustomize.deploy_redis()
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            helm.install_gluu()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def helm_uninstall(self):
        try:
            kustomize = Kustomize(self.timeout)
            helm = Helm()
            self.queue.put(('Uninstalling', 'ONPROGRESS'))
            helm.uninstall_gluu()
            helm.uninstall_nginx_ingress()
            helm.uninstall_gluu_gateway_dbmode()
            helm.uninstall_gluu_gateway_ui()
            logger.info("Please wait...")
            time.sleep(30)
            kustomize.uninstall()
            helm.uninstall_kubedb()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def helm_install_gluu(self):
        try:
            helm = Helm()
            self.queue.put(('Preparing for installation', 'ONPROGRESS'))
            helm.uninstall_gluu()
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            helm.install_gluu(install_ingress=False)
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def helm_install_gg_mode(self):
        try:
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.patch_or_deploy_postgres()
            helm = Helm()
            helm.install_gluu_gateway_dbmode()
            helm.install_gluu_gateway_ui()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def helm_uninstall_gg_mode(self):
        try:
            self.queue.put(('Uninstalling...', 'ONPROGRESS'))
            kustomize = Kustomize(self.timeout)
            kustomize.uninstall_postgres()
            helm = Helm()
            helm.uninstall_gluu_gateway_dbmode()
            helm.uninstall_gluu_gateway_ui()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def helm_uninstall_gluu(self):
        try:
            self.queue.put(('Uninstalling...', 'ONPROGRESS'))
            helm = Helm()
            helm.uninstall_gluu()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())