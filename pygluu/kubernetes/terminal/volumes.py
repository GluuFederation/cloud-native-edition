"""
pygluu.kubernetes.terminal.volumes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for volume terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

import click

from pygluu.kubernetes.helpers import get_logger

logger = get_logger("gluu-prompt-volumes")


class PromptVolumes:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings

    def prompt_volumes_identifier(self):
        """Prompts for Static volume IDs.
        """
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and \
                not self.settings.get("LDAP_STATIC_VOLUME_ID"):
            logger.info("EBS Volume ID example: vol-049df61146c4d7901")
            logger.info("Persistent Disk Name example: "
                        "gke-demoexamplegluu-e31985b-pvc-abe1a701-df81-11e9-a5fc-42010a8a00dd")
            self.settings.set("LDAP_STATIC_VOLUME_ID", click.prompt(
                "Please enter Persistent Disk Name or EBS Volume ID for LDAP"))

    def prompt_disk_uris(self):
        """Prompts for static volume Disk URIs (AKS)
        """
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and not self.settings.get(
                "LDAP_STATIC_DISK_URI"):
            logger.info("DiskURI example: /subscriptions/<subscriptionID>/resourceGroups/"
                        "MC_myAKSCluster_myAKSCluster_westus/providers/Microsoft.Compute/disks/myAKSDisk")
            self.settings.set("LDAP_STATIC_DISK_URI", click.prompt("Please enter the disk uri for LDAP"))

    def prompt_app_volume_type(self):
        """Prompts for volume type
        """
        vol_choice = 0
        if self.settings.get("DEPLOYMENT_ARCH") == "eks":
            print("|------------------------------------------------------------------|")
            print("|Amazon Web Services - Elastic Kubernetes Service (Amazon EKS)     |")
            print("|                    MultiAZ - Supported                           |")
            print("|------------------------------------------------------------------|")
            print("| [6]  volumes on host                                             |")
            print("| [7]  EBS volumes dynamically provisioned [default]               |")
            print("| [8]  EBS volumes statically provisioned                          |")
            vol_choice = click.prompt("What type of volume path", default=7)
        elif self.settings.get("DEPLOYMENT_ARCH") == "gke":
            print("|------------------------------------------------------------------|")
            print("|Google Cloud Engine - Google Kubernetes Engine                    |")
            print("|------------------------------------------------------------------|")
            print("| [11]  volumes on host                                            |")
            print("| [12]  Persistent Disk  dynamically provisioned [default]         |")
            print("| [13]  Persistent Disk  statically provisioned                    |")
            vol_choice = click.prompt("What type of volume path", default=12)
        elif self.settings.get("DEPLOYMENT_ARCH") == "aks":
            print("|------------------------------------------------------------------|")
            print("|Microsoft Azure                                                   |")
            print("|------------------------------------------------------------------|")
            print("| [16] volumes on host                                             |")
            print("| [17] Persistent Disk  dynamically provisioned                    |")
            print("| [18] Persistent Disk  statically provisioned                     |")
            vol_choice = click.prompt("What type of volume path", default=17)
        elif self.settings.get("DEPLOYMENT_ARCH") == "do":
            print("|------------------------------------------------------------------|")
            print("|Digital Ocean                                                     |")
            print("|------------------------------------------------------------------|")
            print("| [21] volumes on host                                             |")
            print("| [22] Persistent Disk  dynamically provisioned                    |")
            print("| [23] Persistent Disk  statically provisioned                     |")
            vol_choice = click.prompt("What type of volume path", default=22)
        elif self.settings.get("DEPLOYMENT_ARCH") == "local":
            print("|------------------------------------------------------------------|")
            print("|Local Deployment                                                  |")
            print("|------------------------------------------------------------------|")
            print("| [26] OpenEBS Local PV Hostpath                                   |")
            print("|------------------------------------------------------------------|")
            logger.info("OpenEBS must be installed before")
            vol_choice = click.prompt("What type of volume path", default=26)
        self.settings.set("APP_VOLUME_TYPE", vol_choice)

    def prompt_storage(self):
        """Prompt for LDAP storage size
        """
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") and not self.settings.get(
                "LDAP_STORAGE_SIZE"):
            self.settings.set("LDAP_STORAGE_SIZE", click.prompt("Size of ldap volume storage", default="4Gi"))

    def prompt_volumes(self):
        """Prompts for all info needed for volume creation on cloud or onpremise
        """
        if self.settings.get("DEPLOYMENT_ARCH") == "microk8s":
            self.settings.set("APP_VOLUME_TYPE", 1)

        elif self.settings.get("DEPLOYMENT_ARCH") == "minikube":
            self.settings.set("APP_VOLUME_TYPE", 2)

        if not self.settings.get("APP_VOLUME_TYPE"):
            self.prompt_app_volume_type()

        if self.settings.get("APP_VOLUME_TYPE") in (8, 13):
            self.prompt_volumes_identifier()

        if self.settings.get("APP_VOLUME_TYPE") == 18:
            self.prompt_disk_uris()

        if not self.settings.get("LDAP_JACKRABBIT_VOLUME") and \
                self.settings.get("DEPLOYMENT_ARCH") in ("aks", "eks", "gke"):
            logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
            logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
            logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
            self.settings.set("LDAP_JACKRABBIT_VOLUME", click.prompt("Please enter the volume type.", default="io1"))
