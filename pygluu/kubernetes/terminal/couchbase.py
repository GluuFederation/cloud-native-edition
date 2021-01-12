"""
pygluu.kubernetes.terminal.couchbase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for couchbase terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

from pathlib import Path
import shutil
import base64

import click
from pygluu.kubernetes.helpers import get_logger, prompt_password
from pygluu.kubernetes.terminal.backup import PromptBackup
from pygluu.kubernetes.terminal.architecture import PromptArch
from pygluu.kubernetes.terminal.helpers import confirm_yesno, gather_ip
from pygluu.kubernetes.terminal.namespace import PromptNamespace
logger = get_logger("gluu-prompt-couchbase")


class PromptCouchbase:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self, settings):
        self.settings = settings
        self.backup = PromptBackup(self.settings)
        self.arch = PromptArch(self.settings)
        self.namespace = PromptNamespace(self.settings)

    def prompt_couchbase(self):
        self.arch.prompt_arch()
        self.namespace.prompt_gluu_namespace()

        if self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            self.backup.prompt_backup()

        if not self.settings.get("HOST_EXT_IP"):
            ip = gather_ip
            self.settings.set("HOST_EXT_IP", ip)

        if not self.settings.get("INSTALL_COUCHBASE"):
            logger.info("For the following prompt  if placed [N] the couchbase is assumed to be"
                        " installed or remotely provisioned")
            self.settings.set("INSTALL_COUCHBASE", confirm_yesno("Install Couchbase", default=True))

        if self.settings.get("INSTALL_COUCHBASE") == "N":
            if not self.settings.get("COUCHBASE_CRT"):
                print("Place the Couchbase certificate authority certificate in a file called couchbase.crt at "
                      "the same location as the installation script.")
                print("This can also be found in your couchbase UI Security > Root Certificate")
                _ = input("Hit 'enter' or 'return' when ready.")
                with open(Path("./couchbase.crt")) as content_file:
                    ca_crt = content_file.read()
                    encoded_ca_crt_bytes = base64.b64encode(ca_crt.encode("utf-8"))
                    encoded_ca_crt_string = str(encoded_ca_crt_bytes, "utf-8")
                self.settings.set("COUCHBASE_CRT", encoded_ca_crt_string)
        else:
            self.settings.set("COUCHBASE_CRT", "")

        self.prompt_override_couchbase_files()

        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube"):
            self.settings.set("COUCHBASE_USE_LOW_RESOURCES", "Y")

        if not self.settings.get("COUCHBASE_USE_LOW_RESOURCES"):
            self.settings.set("COUCHBASE_USE_LOW_RESOURCES", confirm_yesno(
                "Setup CB nodes using low resources for demo purposes"))

        if self.settings.get("COUCHBASE_USE_LOW_RESOURCES") == "N" and \
                self.settings.get("COUCHBASE_CLUSTER_FILE_OVERRIDE") == "N" and \
                self.settings.get("INSTALL_COUCHBASE") == "Y":
            self.prompt_couchbase_calculator()

        if not self.settings.get("COUCHBASE_NAMESPACE"):
            self.settings.set("COUCHBASE_NAMESPACE", click.prompt("Please enter a namespace for CB objects.",
                                                                  default="cbns"))

        if not self.settings.get("COUCHBASE_CLUSTER_NAME"):
            self.settings.set("COUCHBASE_CLUSTER_NAME", click.prompt("Please enter a cluster name.", default="cbgluu"))

        if not self.settings.get("COUCHBASE_URL"):
            self.settings.set("COUCHBASE_URL", click.prompt(
                "Please enter  couchbase (remote or local) URL base name",
                default=f"{self.settings.get('COUCHBASE_CLUSTER_NAME')}.{self.settings.get('COUCHBASE_NAMESPACE')}.svc"
                        f".cluster.local",
            ))

        if not self.settings.get("COUCHBASE_BUCKET_PREFIX"):
            self.settings.set("COUCHBASE_BUCKET_PREFIX", click.prompt(
                "Please enter a  prefix name for all couchbase gluu buckets",
                default="gluu"
            ))

        if not self.settings.get("COUCHBASE_INDEX_NUM_REPLICA"):
            self.settings.set("COUCHBASE_INDEX_NUM_REPLICA", click.prompt(
                "Please enter the number of replicas per index created. "
                "Please note that the number of index nodes must be one greater than the number of replicas. "
                "That means if your couchbase cluster only has 2 "
                "index nodes you cannot place the number of replicas to be higher than 1.",
                default="0",
            ))

        if not self.settings.get("COUCHBASE_SUPERUSER"):
            self.settings.set("COUCHBASE_SUPERUSER", click.prompt("Please enter couchbase superuser username.",
                                                                  default="admin"))

        if not self.settings.get("COUCHBASE_SUPERUSER_PASSWORD"):
            self.settings.set("COUCHBASE_SUPERUSER_PASSWORD", prompt_password("Couchbase superuser"))

        if not self.settings.get("COUCHBASE_USER"):
            self.settings.set("COUCHBASE_USER", click.prompt("Please enter gluu couchbase username.", default="gluu"))

        if not self.settings.get("COUCHBASE_PASSWORD"):
            self.settings.set("COUCHBASE_PASSWORD", prompt_password("Couchbase Gluu user"))

        self.find_couchbase_certs_or_set_san_cn()

    def prompt_override_couchbase_files(self):
        if not self.settings.get("COUCHBASE_CLUSTER_FILE_OVERRIDE"):
            self.settings.set("COUCHBASE_CLUSTER_FILE_OVERRIDE", confirm_yesno(
                "Override couchbase-cluster.yaml with a custom couchbase-cluster.yaml",
            ))

        if self.settings.get("COUCHBASE_CLUSTER_FILE_OVERRIDE") == "Y":
            try:
                shutil.copy(Path("./couchbase-cluster.yaml"), Path("./couchbase/couchbase-cluster.yaml"))
                shutil.copy(Path("./couchbase-buckets.yaml"), Path("./couchbase/couchbase-buckets.yaml"))
                shutil.copy(Path("./couchbase-ephemeral-buckets.yaml"),
                            Path("./couchbase/couchbase-ephemeral-buckets.yaml"))

            except FileNotFoundError:
                logger.error("An override option has been chosen but there is a missing couchbase file that "
                             "could not be found at the current path. Please place the override files under the name"
                             " couchbase-cluster.yaml, couchbase-buckets.yaml, and couchbase-ephemeral-buckets.yaml"
                             " in the same directory pygluu-kubernetes.pyz exists ")
                raise SystemExit(1)

    def find_couchbase_certs_or_set_san_cn(self):
        """Finds couchbase certs inside couchbase_crts-keys folder and if not existent sets couchbase SAN and prompts
        for couchbase common name.
        """
        custom_cb_ca_crt = Path("./couchbase_crts_keys/ca.crt")
        custom_cb_crt = Path("./couchbase_crts_keys/chain.pem")
        custom_cb_key = Path("./couchbase_crts_keys/pkey.key")
        if not custom_cb_ca_crt.exists() or not custom_cb_crt.exists() and not custom_cb_key.exists():
            if not self.settings.get('COUCHBASE_SUBJECT_ALT_NAME'):
                self.settings.set('COUCHBASE_SUBJECT_ALT_NAME', [
                    "*.{}".format(self.settings.get("COUCHBASE_CLUSTER_NAME")),
                    "*.{}.{}".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                     self.settings.get("COUCHBASE_NAMESPACE")),
                    "*.{}.{}.svc".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                         self.settings.get("COUCHBASE_NAMESPACE")),
                    "*.{}.{}.svc.cluster.local".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                                       self.settings.get("COUCHBASE_NAMESPACE")),
                    "{}-srv".format(self.settings.get("COUCHBASE_CLUSTER_NAME")),
                    "{}-srv.{}".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                       self.settings.get("COUCHBASE_NAMESPACE")),
                    "{}-srv.{}.svc".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                           self.settings.get("COUCHBASE_NAMESPACE")),
                    "*.{}-srv.{}.svc.cluster.local".format(self.settings.get("COUCHBASE_CLUSTER_NAME"),
                                                         self.settings.get("COUCHBASE_NAMESPACE")),
                    "localhost"
                ])
            if not self.settings.get("COUCHBASE_CN"):
                self.settings.set("COUCHBASE_CN", click.prompt("Enter Couchbase certificate common name.",
                                                               default="Couchbase CA"))

    def prompt_couchbase_calculator(self):
        """Attempt to Calculate resources needed
        """
        if not self.settings.get("NUMBER_OF_EXPECTED_USERS"):
            self.settings.set("NUMBER_OF_EXPECTED_USERS", click.prompt("Please enter the number of expected users "
                                                                       "[alpha]", default="1000000"))

        if not self.settings.get("USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW"):
            self.settings.set("USING_RESOURCE_OWNER_PASSWORD_CRED_GRANT_FLOW", confirm_yesno(
                "Will you be using the resource owner password credential grant flow [alpha]", default=True,
            ))

        if not self.settings.get("USING_CODE_FLOW"):
            self.settings.set("USING_CODE_FLOW", confirm_yesno("Will you be using the code flow [alpha]", default=True))

        if not self.settings.get("USING_SCIM_FLOW"):
            self.settings.set("USING_SCIM_FLOW", confirm_yesno("Will you be using the SCIM flow [alpha]", default=True))

        if not self.settings.get("EXPECTED_TRANSACTIONS_PER_SEC"):
            self.settings.set("EXPECTED_TRANSACTIONS_PER_SEC", click.prompt("Expected transactions per second [alpha]",
                                                                            default=2000))

        # couchbase-cluster.yaml specs
        if not self.settings.get("COUCHBASE_DATA_NODES"):
            self.settings.set("COUCHBASE_DATA_NODES", click.prompt(
                "Please enter the number of data nodes. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_INDEX_NODES"):
            self.settings.set("COUCHBASE_INDEX_NODES", click.prompt(
                "Please enter the number of index nodes. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_QUERY_NODES"):
            self.settings.set("COUCHBASE_QUERY_NODES", click.prompt(
                "Please enter the number of query nodes. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES"):
            self.settings.set("COUCHBASE_SEARCH_EVENTING_ANALYTICS_NODES", click.prompt(
                "Please enter the number of search, eventing and analytics nodes. [alpha] (auto-calculated)",
                default="",
            ))

        if not self.settings.get("COUCHBASE_GENERAL_STORAGE"):
            self.settings.set("COUCHBASE_GENERAL_STORAGE", click.prompt(
                "Please enter the general storage size used for couchbase. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_DATA_STORAGE"):
            self.settings.set("COUCHBASE_DATA_STORAGE", click.prompt(
                "Please enter the data node storage size used for couchbase. [alpha] (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_INDEX_STORAGE"):
            self.settings.set("COUCHBASE_INDEX_STORAGE", click.prompt(
                "Please enter the index node storage size used for couchbase. (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_QUERY_STORAGE"):
            self.settings.set("COUCHBASE_QUERY_STORAGE", click.prompt(
                "Please enter the query node storage size used for couchbase. (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_ANALYTICS_STORAGE"):
            self.settings.set("COUCHBASE_ANALYTICS_STORAGE", click.prompt(
                "Please enter the analytics node storage size used for couchbase. (auto-calculated)", default="",
            ))

        if not self.settings.get("COUCHBASE_VOLUME_TYPE"):
            logger.info("GCE GKE Options ('pd-standard', 'pd-ssd')")
            logger.info("AWS EKS Options ('gp2', 'io1', 'st1', 'sc1')")
            logger.info("Azure Options ('Standard_LRS', 'Premium_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS')")
            self.settings.set("COUCHBASE_VOLUME_TYPE", click.prompt("Please enter the volume type.", default="io1"))

    def prompt_couchbase_multi_cluster(self):
        """Prompts for couchbase multi cluster
        """
        print("|------------------------------------------------------------------|")
        print("|         Is this a multi-cloud/region setup[N] ? [Y/N]            |")
        print("|------------------------------------------------------------------|")
        print("|                             Notes                                |")
        print("|------------------------------------------------------------------|")
        print("If you are planning for a multi-cloud/region setup and this is the first cluster answer N or"
              " leave blank. You will answer Y for the second and more cluster setup   ")
        print("|------------------------------------------------------------------|")
        self.settings.set("DEPLOY_MULTI_CLUSTER", confirm_yesno("Is this a multi-cloud/region setup"))
