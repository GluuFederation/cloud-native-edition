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
from .extensions import gluu_settings
from pygluu.kubernetes.redis import Redis
from pygluu.kubernetes.postgres import Postgres
from pygluu.kubernetes.mysql import MySQL

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

    def upgrade(self):
        try:
            logger.info("Starting upgrade...")
            self.queue.put(('Upgrading...', 'ONPROGRESS'))

            self.queue.put(('helm upgrade process is still under dev. Nothing happened.', 'COMPLETED'))
        except SystemExit:
            if self.queue:
                self.queue.put(("Oops! Something went wrong", "ERROR"))
            else:
                logger.error("***** Error caught in main loop *****")
                logger.error(traceback.format_exc())

    def upgrade_values_yaml(self):
        try:
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

    def helm_install(self):
        try:
            self.queue.put(('Preparing for installation', 'ONPROGRESS'))
            helm = Helm()
            if gluu_settings.db.get("INSTALL_POSTGRES") == "Y":
                postgres = Postgres()
                postgres.install_postgres()

            if gluu_settings.db.get("INSTALL_REDIS") == "Y":
                redis = Redis()
                redis.install_redis()
            if gluu_settings.db.get("GLUU_INSTALL_SQL") == "Y" \
                    and gluu_settings.db.get("GLUU_SQL_DB_DIALECT") == "mysql":
                sql = MySQL()
                sql.install_mysql()
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
            helm = Helm()
            self.queue.put(('Uninstalling', 'ONPROGRESS'))
            helm.uninstall_gluu()
            helm.uninstall_nginx_ingress()
            logger.info("Please wait...")
            time.sleep(30)
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