"""
 License terms and conditions:
 https://www.gluu.org/license/enterprise-edition/
"""
# TODO: Delete this script as soon as the kubernetes python client fixes CRD issue

from .yamlparser import get_logger
from pathlib import Path
import subprocess
import os
import tarfile

logger = get_logger("python-k8-installer")


# TODO: remove this section once fixed by kubernetes
def subprocess_cmd(command):
    """Execute command"""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout


def install_kubernetes_client_11_0_0():
    logger.warning("https://github.com/kubernetes-client/python/issues/1022"
                   " We have provided an in-house workaround for the issue regarding  building CRDs with"
                   " kubernetes client. This workaround will be removed once resolved by kubernetes")
    kubernetes_package = os.path.join(os.path.dirname(__file__), "templates/kubernetesv11.0.0.tar.gz")
    kubernetes_package_setup = os.path.join(os.path.dirname(__file__), "kubernetes-client/kubernetesv11.0.0/setup.py")
    extract_kubernetes_client_tar(kubernetes_package)
    curdir = os.getcwd()
    working_directory_kubernetes_client = os.path.join(os.path.dirname(__file__), "kubernetes-client/kubernetesv11.0.0")
    os.chdir(working_directory_kubernetes_client)
    logger.info("Installing Kubernetes python client...")
    subprocess_cmd("sudo python3 {} install".format(kubernetes_package_setup))
    os.chdir(curdir)


def extract_kubernetes_client_tar(tar_file):
    kubernetes_extract_folder = os.path.join(os.path.dirname(__file__), "kubernetes-client")
    extract_folder = Path(kubernetes_extract_folder)
    # logger.info("Extracting {} in {} ".format(tar_file, extract_folder))
    tr = tarfile.open(tar_file)
    tr.extractall(path=extract_folder)
    tr.close()
# TODO: End  of section to be removed
