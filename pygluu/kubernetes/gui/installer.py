import os
import sys
import traceback
import threading
import time
from pathlib import Path
from queue import Queue
from pygtail import Pygtail
from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.gluu import Gluu
from pygluu.kubernetes.helpers import get_logger
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

    def install_ldap_backup(self):
        try:
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            gluu = Gluu()
            gluu.install_ldap_backup()
            self.queue.put(('Installation is complete', 'COMPLETED'))
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
            helm = Gluu()
            if gluu_settings.db.get("installer-settings.jackrabbit.clusterMode"):
                from pygluu.kubernetes.kubedb import Kubedb
                kubedb = Kubedb()
                kubedb.uninstall_kubedb()
                kubedb.install_kubedb()

            helm = Gluu()
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

    def install_kubedb(self):
        try:
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            from pygluu.kubernetes.kubedb import Kubedb
            kubedb = Kubedb()
            kubedb.uninstall_kubedb()
            kubedb.install_kubedb()
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
            from pygluu.kubernetes.terminal.helm import PromptHelm
            from pygluu.kubernetes.postgres import Postgres
            from pygluu.kubernetes.gluugateway import GluuGateway
            prompt_helm = PromptHelm(gluu_settings)
            prompt_helm.prompt_helm()
            postgres = Postgres()
            postgres.uninstall_postgres()
            gluugateway = GluuGateway()
            gluugateway.uninstall_gluu_gateway_dbmode()
            gluugateway.uninstall_gluu_gateway_ui()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def install(self):
        try:
            self.queue.put(('Preparing for installation', 'ONPROGRESS'))
            helm = Gluu()
            if gluu_settings.db.get("installer-settings.redis.install") or \
                    gluu_settings.db.get("installer-settings.gluuGateway.install") or \
                    gluu_settings.db.get("installer-settings.jackrabbit.clusterMode"):
                from pygluu.kubernetes.kubedb import Kubedb
                kubedb = Kubedb()
                kubedb.uninstall_kubedb()
                kubedb.install_kubedb()
            if gluu_settings.db.get("installer-settings.jackrabbit.clusterMode"):
                from pygluu.kubernetes.postgres import Postgres
                postgres = Postgres()
                postgres.install_postgres()
            if gluu_settings.db.get("installer-settings.redis.install"):
                from pygluu.kubernetes.redis import Redis
                redis = Redis()
                redis.uninstall_redis()
                redis.install_redis()
            self.queue.put(('Installation in progress', 'ONPROGRESS'))
            helm.install_gluu()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def uninstall(self):
        try:
            from pygluu.kubernetes.gluugateway import GluuGateway
            from pygluu.kubernetes.kubedb import Kubedb
            gluugateway = GluuGateway()
            helm = Gluu()
            self.queue.put(('Uninstalling', 'ONPROGRESS'))
            helm.uninstall_gluu()
            helm.uninstall_nginx_ingress()
            gluugateway.uninstall_gluu_gateway_dbmode()
            gluugateway.uninstall_gluu_gateway_ui()
            logger.info("Please wait...")
            time.sleep(30)
            kubedb = Kubedb()
            kubedb.uninstall_kubedb()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def helm_install_gluu(self):
        try:
            helm = Gluu()
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
            from pygluu.kubernetes.postgres import Postgres
            from pygluu.kubernetes.gluugateway import GluuGateway
            postgres = Postgres()
            postgres.patch_or_install_postgres()
            gluugateway = GluuGateway()
            gluugateway.install_gluu_gateway_dbmode()
            gluugateway.install_gluu_gateway_ui()
            self.queue.put(('Installation is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def uninstall_gg_mode(self):
        try:
            self.queue.put(('Uninstalling...', 'ONPROGRESS'))
            from pygluu.kubernetes.postgres import Postgres
            from pygluu.kubernetes.gluugateway import GluuGateway
            postgres = Postgres()
            postgres.uninstall_postgres()
            gluugateway = GluuGateway()
            gluugateway.uninstall_gluu_gateway_dbmode()
            gluugateway.uninstall_gluu_gateway_ui()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def uninstall_gluu(self):
        try:
            self.queue.put(('Uninstalling...', 'ONPROGRESS'))
            helm = Gluu()
            helm.uninstall_gluu()
            self.queue.put(('Uninstall is complete', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())