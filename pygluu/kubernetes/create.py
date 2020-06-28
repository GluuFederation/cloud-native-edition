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
from .couchbase import Couchbase
from .prompt import Prompt
from .common import get_logger, copy_templates
from .helm import Helm
from .kustomize import Kustomize
# TODO: Remove the following as soon as the update secret is moved to backend
from .updatesecrets import modify_secret
from .gui import app

# End of section to be removed. TODO

logger = get_logger("gluu-create        ")


def create_parser():
    """Create parser to handle arguments from CLI.
    :return:
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", dest="subparser_name")
    subparsers.add_parser("generate-settings", help="Generate settings.json to install "
                                                    "Gluu Enterprise Edition non-interactively")
    subparsers.add_parser("gui-install", help="Install Gluu Enterprise Edition interactive web. ")
    subparsers.add_parser("install", help="Install Gluu Enterprise Edition")
    subparsers.add_parser("install-no-wait", help="Install Gluu Enterprise Edition. "
                                                  "There will be no wait time between installing services. "
                                                  "Pods may look like they are restarting but they will "
                                                  "be waiting for hierarchy "
                                                  "pods to be running")
    subparsers.add_parser("install-ldap-backup", help="Install ldap backup cronjob only.")
    subparsers.add_parser("install-gg-dbmode", help="Install Gluu Gateway with Postgres database")
    subparsers.add_parser("uninstall-gg-dbmode", help="Unnstall Gluu Gateway with Postgres database")
    subparsers.add_parser("restore", help="Install Gluu Enterprise Edition with a "
                                          "running database and previous configuration")
    subparsers.add_parser("uninstall", help="Uninstall Gluu")
    subparsers.add_parser("upgrade", help="Upgrade Gluu Enterprise Edition")
    subparsers.add_parser("install-couchbase", help="Install Couchbase only. Used with installation of Gluu with Helm")
    subparsers.add_parser("install-couchbase-backup", help="Install Couchbase backup only.")
    subparsers.add_parser("uninstall-couchbase", help="Uninstall Couchbase only.")
    subparsers.add_parser("helm-install", help="Install Gluu Enterprise Edition using helm. "
                                               "This also installs the nginx-ingress chart")
    subparsers.add_parser("helm-uninstall", help="Uninstall Gluu Enterprise Edition using helm. "
                                                 "This also uninstalls the nginx-ingress chart")
    subparsers.add_parser("helm-install-gg-dbmode", help="Install Gluu Gateway with Postgres database using helm")
    subparsers.add_parser("helm-uninstall-gg-dbmode", help="Install Gluu Gateway with Postgres database using helm")

    subparsers.add_parser("helm-install-gluu", help="Install Gluu Enterprise Edition using helm. "
                                                    "This assumes nginx-ingress is installed")
    subparsers.add_parser("helm-uninstall-gluu", help="Uninstall Gluu Enterprise Edition using helm. "
                                                      "This only uninstalls Gluu")
    # TODO: Remove the following as soon as the update secret is moved to backend
    subparsers.add_parser("update-secret", help="Update Gluu secret. Often used to update certificates and keys. ")
    # End of section to be removed. TODO
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])

    if not args.subparser_name:
        parser.print_help()
        return
    # TODO: Remove the following as soon as the update secret is moved to backend
    if args.subparser_name == "update-secret":
        modify_secret()
        return
    # End of section to be removed. TODO
    copy_templates()

    # Not sure if we intercept the gui installation from here
    if args.subparser_name == "gui-install":
        app.run(host='0.0.0.0', port=5000, debug=True)
        return

    prompts = Prompt()
    settings = prompts.check_settings_and_prompt

    timeout = 120
    if args.subparser_name == "install-no-wait":
        timeout = 0
    try:
        if args.subparser_name == "install" or args.subparser_name == "install-no-wait":
            kustomize = Kustomize(settings, timeout)
            kustomize.uninstall()
            if settings["INSTALL_REDIS"] == "Y" or settings["INSTALL_GLUU_GATEWAY"] == "Y":
                helm = Helm(settings)
                helm.uninstall_kubedb()
                helm.install_kubedb()
            kustomize.install()

        if args.subparser_name == "install-ldap-backup":
            kustomize = Kustomize(settings, timeout)
            kustomize.setup_backup_ldap()

        elif args.subparser_name == "uninstall":
            logger.info("Removing all Gluu resources...")
            kustomize = Kustomize(settings, timeout)
            kustomize.uninstall()
            if settings["INSTALL_REDIS"] == "Y" or settings["INSTALL_GLUU_GATEWAY"] == "Y":
                helm = Helm(settings)
                helm.uninstall_kubedb()

        elif args.subparser_name == "upgrade":
            logger.info("Starting upgrade...")
            settings = prompts.prompt_upgrade
            kustomize = Kustomize(settings, timeout)
            kustomize.upgrade()

        elif args.subparser_name == "restore":
            kustomize = Kustomize(settings, timeout)
            kustomize.copy_configs_before_restore()
            kustomize.uninstall(restore=True)
            kustomize.install(install_couchbase=False, restore=True)

        elif args.subparser_name == "install-couchbase":
            settings = prompts.prompt_couchbase
            couchbase = Couchbase(settings)
            couchbase.install()

        elif args.subparser_name == "install-couchbase-backup":
            settings = prompts.prompt_couchbase
            couchbase = Couchbase(settings)
            couchbase.setup_backup_couchbase()

        elif args.subparser_name == "uninstall-couchbase":
            settings = prompts.prompt_couchbase
            couchbase = Couchbase(settings)
            couchbase.uninstall()

        elif args.subparser_name == "install-gg-dbmode":
            kustomize = Kustomize(settings, timeout)
            prompts.prompt_gluu_gateway()
            kustomize.install_gluu_gateway_dbmode()

        elif args.subparser_name == "uninstall-gg-dbmode":
            kustomize = Kustomize(settings, timeout)
            kustomize.uninstall_postgres()
            kustomize.uninstall_kong()
            kustomize.uninstall_gluu_gateway_ui()

        elif args.subparser_name == "generate-settings":
            logger.info("settings.json has been generated")

        elif args.subparser_name == "helm-install":
            settings = prompts.prompt_helm
            helm = Helm(settings)
            if settings["INSTALL_REDIS"] == "Y" or settings["INSTALL_GLUU_GATEWAY"] == "Y":
                helm.uninstall_kubedb()
                helm.install_kubedb()
            if settings["INSTALL_REDIS"] == "Y":
                kustomize = Kustomize(settings, timeout)
                kustomize.uninstall_redis()
                kustomize.deploy_redis()
            helm.install_gluu()

        elif args.subparser_name == "helm-uninstall":
            settings = prompts.prompt_helm
            kustomize = Kustomize(settings, timeout)
            helm = Helm(settings)
            helm.uninstall_gluu()
            helm.uninstall_nginx_ingress()
            helm.uninstall_gluu_gateway_dbmode()
            helm.uninstall_gluu_gateway_ui()
            logger.info("Please wait...")
            time.sleep(30)
            kustomize.uninstall()
            helm.uninstall_kubedb()

        elif args.subparser_name == "helm-install-gluu":
            settings = prompts.prompt_helm
            helm = Helm(settings)
            helm.uninstall_gluu()
            helm.install_gluu(install_ingress=False)

        elif args.subparser_name == "helm-install-gg-dbmode":
            kustomize = Kustomize(settings, timeout)
            kustomize.deploy_postgres()
            settings = prompts.prompt_helm
            helm = Helm(settings)
            helm.install_gluu_gateway_dbmode()
            helm.install_gluu_gateway_ui()

        elif args.subparser_name == "helm-uninstall-gg-dbmode":
            kustomize = Kustomize(settings, timeout)
            kustomize.uninstall_postgres()
            settings = prompts.prompt_helm
            helm = Helm(settings)
            helm.uninstall_gluu_gateway_dbmode()
            helm.uninstall_gluu_gateway_ui()

        elif args.subparser_name == "helm-uninstall-gluu":
            settings = prompts.prompt_helm
            helm = Helm(settings)
            helm.uninstall_gluu()

    except KeyboardInterrupt:
        print("\n[I] Canceled by user; exiting ...")


if __name__ == "__main__":
    main()
