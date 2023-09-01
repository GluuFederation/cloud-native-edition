"""
pygluu.kubernetes.terminal.prompt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to initialize all terminal prompts to
interact with user's inputs for terminal installations.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""

from pygluu.kubernetes.settings import SettingsHandler
from pygluu.kubernetes.terminal.confirmsettings import PromptConfirmSettings
from pygluu.kubernetes.terminal.volumes import PromptVolumes
from pygluu.kubernetes.terminal.gke import PromptGke
from pygluu.kubernetes.terminal.configuration import PromptConfiguration
from pygluu.kubernetes.terminal.jackrabbit import PromptJackrabbit
from pygluu.kubernetes.terminal.istio import PromptIstio
from pygluu.kubernetes.terminal.replicas import PromptReplicas
from pygluu.kubernetes.terminal.couchbase import PromptCouchbase
from pygluu.kubernetes.terminal.architecture import PromptArch
from pygluu.kubernetes.terminal.namespace import PromptNamespace
from pygluu.kubernetes.terminal.optionalservices import PromptOptionalServices
from pygluu.kubernetes.terminal.testenv import PromptTestEnvironment
from pygluu.kubernetes.terminal.aws import PromptAws
from pygluu.kubernetes.terminal.helpers import gather_ip
from pygluu.kubernetes.terminal.persistencebackend import PromptPersistenceBackend
from pygluu.kubernetes.terminal.ldap import PromptLdap
from pygluu.kubernetes.terminal.images import PromptImages
from pygluu.kubernetes.terminal.cache import PromptCache
from pygluu.kubernetes.terminal.backup import PromptBackup
from pygluu.kubernetes.terminal.license import PromptLicense
from pygluu.kubernetes.terminal.version import PromptVersion
from pygluu.kubernetes.terminal.sql import PromptSQL
from pygluu.kubernetes.terminal.google import PromptGoogle
from pygluu.kubernetes.terminal.doc_store import PromptDocStore


class Prompt:
    """Prompt is used for prompting users for input used in deploying Gluu.
    """

    def __init__(self):
        self.settings = SettingsHandler()

    def load_settings(self):
        self.settings = SettingsHandler()

    def license(self):
        self.load_settings()
        PromptLicense(self.settings)

    def versions(self):
        self.load_settings()
        PromptVersion(self.settings)

    def arch(self):
        self.load_settings()
        arch = PromptArch(self.settings)
        arch.prompt_arch()

    def namespace(self):
        self.load_settings()
        namespace = PromptNamespace(self.settings)
        namespace.prompt_gluu_namespace()

    def optional_services(self):
        self.load_settings()
        optional_services = PromptOptionalServices(self.settings)
        optional_services.prompt_optional_services()

    def jackrabbit(self):
        self.load_settings()
        jackrabbit = PromptJackrabbit(self.settings)
        jackrabbit.prompt_jackrabbit()

    def istio(self):
        self.load_settings()
        istio = PromptIstio(self.settings)
        istio.prompt_istio()

    def test_enviornment(self):
        self.load_settings()
        test_environment = PromptTestEnvironment(self.settings)
        if not self.settings.get("TEST_ENVIRONMENT") and \
                self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            test_environment.prompt_test_environment()

        if self.settings.get("DEPLOYMENT_ARCH") in ("eks", "gke", "do", "local", "aks"):
            if not self.settings.get("NODE_SSH_KEY"):
                test_environment.prompt_ssh_key()

    def network(self):
        if not self.settings.get("HOST_EXT_IP"):
            ip = gather_ip()
            self.load_settings()
            self.settings.set("HOST_EXT_IP", ip)

            if self.settings.get("DEPLOYMENT_ARCH") == "eks" and self.settings.get("USE_ISTIO_INGRESS") != "Y":
                aws = PromptAws(self.settings)
                aws.prompt_aws_lb()

    def gke(self):
        self.load_settings()
        if self.settings.get("DEPLOYMENT_ARCH") == "gke":
            gke = PromptGke(self.settings)
            gke.prompt_gke()

    def persistence_backend(self):
        self.load_settings()
        persistence_backend = PromptPersistenceBackend(self.settings)
        persistence_backend.prompt_persistence_backend()

    def ldap(self):
        self.load_settings()
        if self.settings.get("PERSISTENCE_BACKEND") == "hybrid":
            ldap = PromptLdap(self.settings)
            ldap.prompt_hybrid_ldap_held_data()

    def volumes(self):
        self.load_settings()
        volumes = PromptVolumes(self.settings)
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "ldap") or \
                self.settings.get("INSTALL_JACKRABBIT") == "Y":
            volumes.prompt_volumes()
        volumes.prompt_storage()

    def couchbase(self):
        self.load_settings()
        couchbase = PromptCouchbase(self.settings)
        if not self.settings.get("DEPLOY_MULTI_CLUSTER") and self.settings.get("PERSISTENCE_BACKEND") in (
                "hybrid", "couchbase") and self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            couchbase.prompt_couchbase_multi_cluster()
        if self.settings.get("PERSISTENCE_BACKEND") in ("hybrid", "couchbase"):
            couchbase.prompt_couchbase()

    def cache(self):
        self.load_settings()
        cache = PromptCache(self.settings)
        cache.prompt_cache_type()

    def backup(self):
        self.load_settings()
        if self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            backup = PromptBackup(self.settings)
            backup.prompt_backup()

    def configuration(self):
        self.load_settings()
        configuration = PromptConfiguration(self.settings)
        configuration.prompt_config()

    def images(self):
        self.load_settings()
        images = PromptImages(self.settings)
        images.prompt_image_name_tag()

    def replicas(self):
        self.load_settings()
        replicas = PromptReplicas(self.settings)
        replicas.prompt_replicas()

    def sql(self):
        self.load_settings()
        if self.settings.get("PERSISTENCE_BACKEND") == "sql":
            spanner = PromptSQL(self.settings)
            spanner.prompt_sql()

    def google(self):
        self.load_settings()
        if self.settings.get("PERSISTENCE_BACKEND") == "spanner":
            spanner = PromptGoogle(self.settings)
            spanner.prompt_google()

    def confirm_settings(self):
        self.load_settings()
        if self.settings.get("CONFIRM_PARAMS") != "Y":
            confirm_settings = PromptConfirmSettings(self.settings)
            confirm_settings.confirm_params()

    def prompt(self):
        """Main property: called to setup all prompts and returns prompts in settings file.

        :return:
        """
        self.license()
        self.versions()
        self.arch()
        self.namespace()
        self.optional_services()
        self.doc_store()
        self.istio()
        self.test_enviornment()
        self.network()
        self.gke()
        self.persistence_backend()
        self.ldap()
        self.volumes()
        self.sql()
        self.google()
        self.couchbase()
        self.cache()
        self.backup()
        self.configuration()
        self.images()
        self.replicas()
        self.volumes()
        self.confirm_settings()

    def doc_store(self):
        self.load_settings()

        pr = PromptDocStore(self.settings)
        pr.prompt_doc_store()

        if self.settings.get("DOCUMENT_STORE_TYPE") == "DB":
            self.settings.set("INSTALL_JACKRABBIT", "N")

        if self.settings.get("DOCUMENT_STORE_TYPE") == "JCA":
            self.jackrabbit()
