"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Installs Gluu
"""
# TODO: Delete this script as soon as the kubernetes python client fixes CRD issue
# from .installclient import install_kubernetes_client_11_0_0

# try:
#     from .kubeapi import Kubernetes
# except ImportError:
#     install_kubernetes_client_11_0_0()
# End of section to be removed. TODO
import argparse
import time
import sys
from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.terminal.prompt import Prompt
from pygluu.kubernetes.helpers import get_logger, copy_templates
from pygluu.kubernetes.helm import Helm
from pygluu.kubernetes.kustomize import Kustomize
from pygluu.kubernetes.settings import SettingsHandler

logger = get_logger("gluu-create        ")


def create_parser():
    """Create parser to handle arguments from CLI.
    :return:
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", dest="subparser_name")
    subparsers.add_parser("generate-settings", help="Generate settings.json to install "
                                                    "Gluu Cloud Native Edition non-interactively")
    subparsers.add_parser("install", help="Install Gluu Cloud Native Edition")
    subparsers.add_parser("install-no-wait", help="Install Gluu Cloud Native Edition. "
                                                  "There will be no wait time between installing services. "
                                                  "Pods may look like they are restarting but they will "
                                                  "be waiting for hierarchy "
                                                  "pods to be running")
    subparsers.add_parser("install-ldap-backup", help="Install ldap backup cronjob only.")
    subparsers.add_parser("install-kubedb", help="Install KubeDB for redis or postgres")
    subparsers.add_parser("install-gg-dbmode", help="Install Gluu Gateway with Postgres database")
    subparsers.add_parser("uninstall-gg-dbmode", help="Unnstall Gluu Gateway with Postgres database")
    subparsers.add_parser("restore", help="Install Gluu Cloud Native Edition with a "
                                          "running database and previous configuration")
    subparsers.add_parser("uninstall", help="Uninstall Gluu")
    subparsers.add_parser("upgrade", help="Upgrade Gluu Cloud Native Edition")
    subparsers.add_parser("upgrade-values-yaml", help="Upgrade Gluu Cloud Native Edition")
    subparsers.add_parser("install-couchbase", help="Install Couchbase only. Used with installation of Gluu with Helm")
    subparsers.add_parser("install-couchbase-backup", help="Install Couchbase backup only.")
    subparsers.add_parser("uninstall-couchbase", help="Uninstall Couchbase only.")
    subparsers.add_parser("helm-install", help="Install Gluu Cloud Native Edition using helm. "
                                               "This also installs the nginx-ingress chart")
    subparsers.add_parser("helm-uninstall", help="Uninstall Gluu Cloud Native Edition using helm. "
                                                 "This also uninstalls the nginx-ingress chart")
    subparsers.add_parser("helm-install-gg-dbmode", help="Install Gluu Gateway with Postgres database using helm")
    subparsers.add_parser("helm-uninstall-gg-dbmode", help="Install Gluu Gateway with Postgres database using helm")

    subparsers.add_parser("helm-install-gluu", help="Install Gluu Cloud Native Edition using helm. "
                                                    "This assumes nginx-ingress is installed")
    subparsers.add_parser("helm-uninstall-gluu", help="Uninstall Gluu Cloud Native Edition using helm. "
                                                      "This only uninstalls Gluu")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])

    if not args.subparser_name:
        parser.print_help()
        return
    copy_templates()
    prompts = Prompt()
    prompts.prompt()
    settings = SettingsHandler()

    timeout = 120
    if args.subparser_name == "install-no-wait":
        timeout = 0
    try:
        if args.subparser_name == "install" or args.subparser_name == "install-no-wait":
            kustomize = Kustomize(timeout)
            kustomize.uninstall()
            if settings.get("INSTALL_REDIS") == "Y" or \
                    settings.get("INSTALL_GLUU_GATEWAY") == "Y" or \
                    settings.get("JACKRABBIT_CLUSTER") == "Y":
                helm = Helm()
                helm.uninstall_kubedb()
                helm.install_kubedb()
            kustomize.install()

        if args.subparser_name == "install-ldap-backup":
            kustomize = Kustomize(timeout)
            kustomize.setup_backup_ldap()

        elif args.subparser_name == "uninstall":
            logger.info("Removing all Gluu resources...")
            kustomize = Kustomize(timeout)
            kustomize.uninstall()
            if settings.get("INSTALL_REDIS") == "Y" or settings.get("INSTALL_GLUU_GATEWAY") == "Y":
                helm = Helm()
                helm.uninstall_kubedb()

        elif args.subparser_name == "upgrade":
            from pygluu.kubernetes.terminal.upgrade import PromptUpgrade
            # New feature in 4.2 compared to 4.1 and hence if enabled should make sure kubedb is installed.
            if settings.get("JACKRABBIT_CLUSTER") == "Y":
                helm = Helm()
                helm.uninstall_kubedb()
                helm.install_kubedb()
            prompt_upgrade = PromptUpgrade(settings)
            logger.info("Starting upgrade...")
            prompt_upgrade.prompt_upgrade()
            kustomize = Kustomize(timeout)
            kustomize.upgrade()

        elif args.subparser_name == "upgrade-values-yaml":
            from pygluu.kubernetes.terminal.upgrade import PromptUpgrade
            # New feature in 4.2 compared to 4.1 and hence if enabled should make sure kubedb is installed.
            helm = Helm()
            if settings.get("JACKRABBIT_CLUSTER") == "Y":
                helm.uninstall_kubedb()
                helm.install_kubedb()
            prompt_upgrade = PromptUpgrade(settings)
            prompt_upgrade.prompt_upgrade()
            helm = Helm()
            logger.info("Patching values.yaml for helm upgrade...")
            helm.analyze_global_values()
            logger.info("Please find your patched values.yaml at the location ./helm/gluu/values.yaml."
                        "Continue with the steps found at https://gluu.org/docs/gluu-server/4.2/upgrade/#helm")

        elif args.subparser_name == "restore":
            kustomize = Kustomize(timeout)
            kustomize.copy_configs_before_restore()
            kustomize.uninstall(restore=True)
            kustomize.install(install_couchbase=False, restore=True)

        elif args.subparser_name == "install-couchbase":
            from pygluu.kubernetes.terminal.couchbase import PromptCouchbase
            prompt_couchbase = PromptCouchbase(settings)
            prompt_couchbase.prompt_couchbase()
            couchbase = Couchbase()
            couchbase.install()

        elif args.subparser_name == "install-couchbase-backup":
            from pygluu.kubernetes.terminal.couchbase import PromptCouchbase
            prompt_couchbase = PromptCouchbase(settings)
            prompt_couchbase.prompt_couchbase()
            couchbase = Couchbase()
            couchbase.setup_backup_couchbase()

        elif args.subparser_name == "uninstall-couchbase":
            from pygluu.kubernetes.terminal.couchbase import PromptCouchbase
            prompt_couchbase = PromptCouchbase(settings)
            prompt_couchbase.prompt_couchbase()
            couchbase = Couchbase()
            couchbase.uninstall()

        elif args.subparser_name == "install-gg-dbmode":
            from pygluu.kubernetes.terminal.gluugateway import PromptGluuGateway
            prompt_gluu_gateway = PromptGluuGateway(settings)
            prompt_gluu_gateway.prompt_gluu_gateway()
            kustomize = Kustomize(timeout)
            kustomize.install_gluu_gateway_dbmode()

        elif args.subparser_name == "install-kubedb":
            helm = Helm()
            helm.install_kubedb()

        elif args.subparser_name == "uninstall-gg-dbmode":
            kustomize = Kustomize(timeout)
            kustomize.uninstall_kong()
            kustomize.uninstall_gluu_gateway_ui()

        elif args.subparser_name == "generate-settings":
            logger.info("settings.json has been generated")

        elif args.subparser_name == "helm-install":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            helm = Helm()
            if settings.get("INSTALL_REDIS") == "Y" or \
                    settings.get("INSTALL_GLUU_GATEWAY") == "Y" or \
                    settings.get("JACKRABBIT_CLUSTER") == "Y":
                helm.uninstall_kubedb()
                helm.install_kubedb()
            if settings.get("JACKRABBIT_CLUSTER") == "Y":
                kustomize = Kustomize(timeout)
                kustomize.deploy_postgres()
            if settings.get("INSTALL_REDIS") == "Y":
                kustomize = Kustomize(timeout)
                kustomize.uninstall_redis()
                kustomize.deploy_redis()
            helm.install_gluu()

        elif args.subparser_name == "helm-uninstall":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            kustomize = Kustomize(timeout)
            helm = Helm()
            helm.uninstall_gluu()
            helm.uninstall_nginx_ingress()
            helm.uninstall_gluu_gateway_dbmode()
            helm.uninstall_gluu_gateway_ui()
            logger.info("Please wait...")
            time.sleep(30)
            kustomize.uninstall()
            helm.uninstall_kubedb()

        elif args.subparser_name == "helm-install-gluu":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            helm = Helm()
            helm.uninstall_gluu()
            helm.install_gluu(install_ingress=False)

        elif args.subparser_name == "helm-install-gg-dbmode":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            kustomize = Kustomize(timeout)
            kustomize.deploy_postgres()
            helm = Helm()
            helm.install_gluu_gateway_dbmode()
            helm.install_gluu_gateway_ui()

        elif args.subparser_name == "helm-uninstall-gg-dbmode":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            kustomize = Kustomize(timeout)
            kustomize.uninstall_postgres()
            helm = Helm()
            helm.uninstall_gluu_gateway_dbmode()
            helm.uninstall_gluu_gateway_ui()

        elif args.subparser_name == "helm-uninstall-gluu":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            helm = Helm()
            helm.uninstall_gluu()

    except KeyboardInterrupt:
        print("\n[I] Canceled by user; exiting ...")


if __name__ == "__main__":
    main()
