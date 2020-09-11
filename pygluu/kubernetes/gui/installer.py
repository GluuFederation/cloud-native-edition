import os
import threading
from pathlib import Path
from queue import Queue
from pygluu.kubernetes.helm import Helm
from pygluu.kubernetes.kustomize import Kustomize
from pygluu.kubernetes.settings import SettingsHandler


class InstallHandler(object):
    def __init__(self):
        self.install_type = None
        self.timeout = 120
        self.queue = Queue()
        self.settings = SettingsHandler()

    def run_install_kustomize(self):
        log_offset = Path("./setup.log.offset")
        if log_offset.exists():
            os.unlink('./setup.log.offset')

        t = threading.Thread(target=self.install_kustomize, args=(self.queue,))
        t.daemon = True
        t.start()

    def install_kustomize(self, q):
        q.put(('Preparing Installation', 'ONPROGRESS'))
        kustomize = Kustomize(self.timeout)
        kustomize.uninstall()

        if self.settings.get("INSTALL_REDIS") == "Y" or \
                self.settings.get("INSTALL_GLUU_GATEWAY") == "Y" or \
                self.settings.get("JACKRABBIT_CLUSTER") == "Y":

            q.put(('Installing kube-db', 'ONPROGRESS'))
            helm = Helm()
            helm.uninstall_kubedb()
            helm.install_kubedb()

        q.put(('Installation in progress', 'ONPROGRESS'))
        kustomize.install()
        q.put(('Installation Completed', 'COMPLETED'))
        os.remove('./setup.log.offset')
