import os
import requests
from pathlib import Path
from collections import OrderedDict
from pygluu.kubernetes.helpers import get_logger
logger = get_logger("gluu-gui")


def determine_ip_nodes():
    """Attempts to detect and return ip automatically.
    Also set node names, zones, and addresses in a cloud deployment.

    :return:
    """
    from pygluu.kubernetes.kubeapi import Kubernetes
    from .extensions import gluu_settings
    kubernetes = Kubernetes()
    logger.info("Determining OS type and attempting to gather external IP address")

    data = {}
    # detect IP address automatically (if possible)
    try:
        node_ip_list = []
        node_zone_list = []
        node_name_list = []
        node_list = kubernetes.list_nodes().items

        for node in node_list:
            node_name = node.metadata.name
            node_addresses = kubernetes.read_node(name=node_name).status.addresses
            if gluu_settings.db.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube"):
                for add in node_addresses:
                    if add.type == "InternalIP":
                        data["ip"] = ip = add.address
                        node_ip_list.append(ip)
            else:
                for add in node_addresses:
                    if add.type == "ExternalIP":
                        data["ip"] = ip = add.address
                        node_ip_list.append(ip)
                # Digital Ocean does not provide zone support yet
                if gluu_settings.db.get("DEPLOYMENT_ARCH") not in ("do", "local"):
                    node_zone = node.metadata.labels["failure-domain.beta.kubernetes.io/zone"]
                    node_zone_list.append(node_zone)
                node_name_list.append(node_name)

        data["NODES_NAMES"] = node_name_list
        data["NODES_ZONES"] = node_zone_list
        data["NODES_IPS"] = node_ip_list

        if gluu_settings.db.get("DEPLOYMENT_ARCH") in ("eks", "gke", "do", "local", "aks"):
            #  Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
            data["ip"] = "22.22.22.22"
        return data
    except Exception as e:

        logger.error(e)
        # prompt for user-inputted IP address
        logger.warning("Cannot determine IP address")
        # return a fail safe
        return {
            "ip": "127.0.0.1",
            "NODES_NAMES": [],
            "NODES_ZONES": [],
            "NODES_IPS": []
        }


def is_couchbase_pkg_exist():
    couchbase_tar_pattern = "couchbase-autonomous-operator-kubernetes_*.tar.gz"
    directory = Path('.')
    try:
        couchbase_tar_file = list(directory.glob(couchbase_tar_pattern))[0]
        if "_1." in str(couchbase_tar_file.resolve()):
            # Package found but incorrect and should appear as incorrect in the GUI. Option to add url and push download and track that download before moving to next step.
            False

    except IndexError:
        # Package is not  found.
        return False
    else:
        return True


def download_couchbase_pkg(url):
    dest_folder = Path('./')
    filename = url.split('/')[-1]
    file_path = os.path.join(dest_folder, filename)
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=None):
                f.write(chunk)
        r.close()
    return filename


class WizardHandler(object):
    def __init__(self):
        self.steps = self.default_steps
        self.current_step = None
        self.nextstep = None
        self.finalstep = 'wizard.setting_summary'

    @property
    def default_steps(self):
        default_steps = OrderedDict({
            'license': {
                "title": "License",
                "endpoint": "wizard.agreement"
            },
            'version': {
                "title": "Gluu version",
                "endpoint": "wizard.gluu_version"
            },
            'deployment': {
                "title": "Deployment architecture",
                "endpoint": "wizard.deployment_arch"
            },
            'namespace': {
                "title": "Gluu namespace",
                "endpoint": "wizard.gluu_namespace"
            },
            'services': {
                "title": "Optional Services",
                "endpoint": "wizard.optional_services"
            },
            'jackrabbit': {
                "title": "Install jackrabbit",
                "endpoint": "wizard.install_jackrabbit"
            },
            'istio': {
                "title": "Install Istio",
                "endpoint": "wizard.install_istio"
            },
            'environment': {
                "title": "Environment Setting",
                "endpoint": "wizard.environment"
            },
            'persistence_backend': {
                "title": "Persistence backend",
                "endpoint": "wizard.persistence_backend"
            },
            'volumes': {
                "title": "Volumes",
                "endpoint": "wizard.volumes"
            },
            'couchbase_multicluster': {
                "title": "Couchbase multi cluster",
                "endpoint": "wizard.couchbase_multi_cluster"
            },
            'couchbase': {
                "title": "Couchbase",
                "endpoint": "wizard.couchbase"
            },
            'couchbase_calculator': {
                "title": "Couchbase calculator",
                "endpoint": "wizard.couchbase_calculator"
            },
            'sql': {
                "title": "RDBMS",
                "endpoint": "wizard.sql"
            },
            'google': {
                "title": "Google",
                "endpoint": "wizard.google"
            },
            'cache': {
                "title": "Cache type",
                "endpoint": "wizard.cache_type"
            },
            'backup': {
                "title": "Backup",
                "endpoint": "wizard.backup"
            },
            'configuration': {
                "title": "Configuration",
                "endpoint": "wizard.configuration"
            },
            'images': {
                "title": "Images",
                "endpoint": "wizard.images"
            },
            'replicas': {
                "title": "Replicas",
                "endpoint": "wizard.replicas"
            }
        })
        return default_steps

    def helm_steps(self):
        """
        Populating wizard steps for helm install
        :return:
        """
        self.steps = self.default_steps
        self.steps.update({
            'helm_config': {
                "title": "Helm Configuration",
                "endpoint": "wizard.helm_config"
            }
        })
        return self.steps

    def normal_steps(self):
        self.steps = self.default_steps

    def upgrade_steps(self):
        """
        Populating wizard steps for upgrade version
        :return:
        """
        self.steps = self.default_steps
        self.steps.update({
            'upgrade': {
                "title": "Upgrade Version",
                "endpoint": "wizard.upgrade"
            }
        })
        self.steps.move_to_end('images')
        return self.steps

    def step_number(self):
        """
        Get step number or index
        :return:
        """
        keys = list(self.steps.keys())
        index = keys.index(self.current_step)
        return index + 1

    def next_step(self):
        """
        get next step endpoint
        :return:
        """
        try:
            keys = list(self.steps.keys())
            index = keys.index(self.current_step) + 1
            return self.steps[keys[index]]['endpoint']
        except IndexError:
            return self.finalstep

    def prev_step(self):
        """
        get previous step endpoint
        :return:
        """
        keys = list(self.steps.keys())
        index = keys.index(self.current_step) - 1
        return self.steps[keys[index]]['endpoint']
