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
import sys
from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.terminal.prompt import Prompt
from pygluu.kubernetes.helpers import get_logger, copy_templates
from pygluu.kubernetes.helm import Helm
from pygluu.kubernetes.settings import SettingsHandler
from pygluu.kubernetes.redis import Redis
from pygluu.kubernetes.postgres import Postgres
from pygluu.kubernetes.mysql import MySQL

logger = get_logger("gluu-create        ")


def create_parser():
    """Create parser to handle arguments from CLI.
    :return:
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", dest="subparser_name")
    subparsers.add_parser("generate-settings", help="Generate settings.json to install "
                                                    "Gluu Cloud Native Edition non-interactively")
    subparsers.add_parser("install", help="Install Gluu Cloud Native Edition using helm. "
                                          "This also installs the nginx-ingress chart")
    subparsers.add_parser("uninstall", help="Uninstall Gluu Cloud Native Edition using helm. "
                                            "This also uninstalls the nginx-ingress chart")
    subparsers.add_parser("upgrade-values-yaml", help="Upgrade Gluu Cloud Native Edition")
    subparsers.add_parser("install-couchbase", help="Install Couchbase only. Used with installation of Gluu with Helm")
    subparsers.add_parser("install-couchbase-backup", help="Install Couchbase backup only.")
    subparsers.add_parser("uninstall-couchbase", help="Uninstall Couchbase only.")
    subparsers.add_parser("helm-install", help="Install Gluu Cloud Native Edition using helm. "
                                               "This also installs the nginx-ingress chart")
    subparsers.add_parser("helm-uninstall", help="Uninstall Gluu Cloud Native Edition using helm. "
                                                 "This also uninstalls the nginx-ingress chart")

    subparsers.add_parser("helm-install-gluu", help="Install Gluu Cloud Native Edition using helm. "
                                                    "This assumes nginx-ingress is installed")
    subparsers.add_parser("helm-uninstall-gluu", help="Uninstall Gluu Cloud Native Edition using helm. "
                                                      "This only uninstalls Gluu")
    subparsers.add_parser("version", help="Outputs version of pygluu installer.")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])

    if not args.subparser_name:
        parser.print_help()
        return

    if args.subparser_name == "version":
        from pygluu.kubernetes.version import __version__
        logger.info(f"pygluu installer version is : {__version__}")
        return

    copy_templates()
    prompts = Prompt()
    prompts.prompt()
    settings = SettingsHandler()
    try:
        if args.subparser_name == "install" or args.subparser_name == "helm-install":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            helm = Helm()
            if settings.get("INSTALL_POSTGRES") == "Y":
                postgres = Postgres()
                postgres.install_postgres()
            if settings.get("INSTALL_REDIS") == "Y":
                redis = Redis()
                redis.install_redis()
            if settings.get("GLUU_INSTALL_SQL") == "Y" and settings.get("GLUU_SQL_DB_DIALECT") == "mysql":
                sql = MySQL()
                sql.install_mysql()
            helm.install_gluu()

        elif args.subparser_name == "uninstall" or args.subparser_name == "helm-uninstall":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            helm = Helm()
            helm.uninstall_gluu()
            helm.uninstall_nginx_ingress()
            sql = MySQL()
            sql.uninstall_mysql()
            postgres = Postgres()
            postgres.uninstall_postgres()
            redis = Redis()
            redis.uninstall_redis()

        elif args.subparser_name == "upgrade-values-yaml":
            from pygluu.kubernetes.terminal.upgrade import PromptUpgrade
            prompt_upgrade = PromptUpgrade(settings)
            prompt_upgrade.prompt_upgrade()
            helm = Helm()
            logger.info("Patching values.yaml for helm upgrade...")
            helm.analyze_global_values()
            logger.info("Please find your patched values.yaml at the location ./helm/gluu/values.yaml."
                        "Continue with the steps found at https://gluu.org/docs/gluu-server/4.5/upgrade/#helm")

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

        elif args.subparser_name == "generate-settings":
            logger.info("settings.json has been generated")

        elif args.subparser_name == "helm-install-gluu":
            from pygluu.kubernetes.terminal.helm import PromptHelm
            prompt_helm = PromptHelm(settings)
            prompt_helm.prompt_helm()
            helm = Helm()
            helm.uninstall_gluu()
            helm.install_gluu(install_ingress=False)

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
