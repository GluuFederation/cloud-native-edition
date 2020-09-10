"""
pygluu.kubernetes.terminal.common
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers for terminal prompt classes

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

import click
from pygluu.kubernetes.helpers import get_logger

logger = get_logger("gluu-prompt-common")


def confirm_yesno(text, *args, **kwargs):
    """Like ``click.confirm`` but returns ``Y`` or ``N`` character
    instead of boolean.
    """
    default = "[N]"
    # Default is always N unless default is set in kwargs
    if "default" in kwargs and kwargs["default"]:
        default = "[Y]"

    confirmed = click.confirm(f"{text} {default}", *args, **kwargs)
    return "Y" if confirmed else "N"


def gather_ip():
    """Attempts to detect and return ip automatically.
    Also set node names, zones, and addresses in a cloud deployment.

    :return:
    """
    from pygluu.kubernetes.kubeapi import Kubernetes
    from pygluu.kubernetes.settings import SettingsHandler
    import ipaddress
    kubernetes = Kubernetes()
    settings = SettingsHandler()
    logger.info("Determining OS type and attempting to gather external IP address")
    ip = ""

    # detect IP address automatically (if possible)
    try:
        node_ip_list = []
        node_zone_list = []
        node_name_list = []
        node_list = kubernetes.list_nodes().items

        for node in node_list:
            node_name = node.metadata.name
            node_addresses = kubernetes.read_node(name=node_name).status.addresses
            if settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube"):
                for add in node_addresses:
                    if add.type == "InternalIP":
                        ip = add.address
                        node_ip_list.append(ip)
            else:
                for add in node_addresses:
                    if add.type == "ExternalIP":
                        ip = add.address
                        node_ip_list.append(ip)
                # Digital Ocean does not provide zone support yet
                if settings.get("DEPLOYMENT_ARCH") not in ("do", "local"):
                    node_zone = node.metadata.labels["failure-domain.beta.kubernetes.io/zone"]
                    node_zone_list.append(node_zone)
                node_name_list.append(node_name)

        settings.set("NODES_NAMES", node_name_list)
        settings.set("NODES_ZONES", node_zone_list)
        settings.set("NODES_IPS", node_ip_list)

        if settings.get("DEPLOYMENT_ARCH") in ("eks", "gke", "do", "local", "aks"):
            #  Assign random IP. IP will be changed by either the update ip script, GKE external ip or nlb ip
            return "22.22.22.22"

    except Exception as e:
        logger.error(e)
        # prompt for user-inputted IP address
        logger.warning("Cannot determine IP address")
        ip = click.prompt("Please input the host's external IP address")

    if click.confirm(f"Is this the correct external IP address: {ip}", default=True):
        return ip

    while True:
        ip = click.prompt("Please input the host's external IP address")
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError as exc:
            # raised if IP is invalid
            logger.warning(f"Cannot determine IP address; reason={exc}")
