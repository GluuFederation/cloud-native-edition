"""
pygluu.kubernetes.gluugateway
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles Gluu Gateway and Gluu Gateway UI
"""

from pathlib import Path
from pygluu.kubernetes.yamlparser import Parser
from pygluu.kubernetes.helpers import get_logger, exec_cmd
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.settings import ValuesHandler
from ast import literal_eval
import base64

logger = get_logger("gluu-gateway       ")


def register_op_client(namespace, client_name, op_host, client_api_url, release_name):
    """Registers an op client using client_api.

    :param namespace:
    :param client_name:
    :param op_host:
    :param client_api_url:
    :param release_name:
    :return:
    """
    kubernetes = Kubernetes()
    logger.info("Registering a client : {}".format(client_name))
    client_api_id, client_id, client_secret = "", "", ""

    data = '{"redirect_uris": ["https://' + op_host + '/gg-ui/"], "op_host": "' + op_host + \
           '", "post_logout_redirect_uris": ["https://' + op_host + \
           '/gg-ui/"], "scope": ["openid", "oxd", "permission", "username"], ' \
           '"grant_types": ["authorization_code", "client_credentials"], "client_name": "' + client_name + '"}'

    exec_curl_command = ["curl", "-k", "-s", "--location", "--request", "POST",
                         "{}/register-site".format(client_api_url), "--header",
                         "Content-Type: application/json", "--data-raw",
                         data]
    try:
        client_registration_response = \
            kubernetes.connect_get_namespaced_pod_exec(exec_command=exec_curl_command,
                                                       app_label="app=auth-server",
                                                       container=release_name + "-auth-server",
                                                       namespace=namespace,
                                                       stdout=False)

        client_registration_response_dict = literal_eval(client_registration_response)
        client_api_id = client_registration_response_dict["client_api_id"]
        client_id = client_registration_response_dict["client_id"]
        client_secret = client_registration_response_dict["client_secret"]
    except (IndexError, Exception):
        exec_curl_command = ["curl", "-k", "-s", "--location", "--request", "POST",
                             "{}/register-site".format(client_api_url), "--header",
                             "'Content-Type: application/json'", "--data-raw",
                             "'" + data + "'"]
        manual_curl_command = " ".join(exec_curl_command)
        logger.error("Registration of client : {} failed. Please do so manually by calling\n{}".format(
            client_name, manual_curl_command))
    return client_api_id, client_id, client_secret


class GluuGateway(object):
    def __init__(self):
        self.settings = ValuesHandler()
        self.kubernetes = Kubernetes()
        if "gke" in self.settings.get("installer-settings.volumeProvisionStrategy") == "gke":
            # Clusterrolebinding needs to be created for gke with CB or kubeDB installed
            user_account, stderr, retcode = exec_cmd("gcloud config get-value core/account")
            user_account = str(user_account, "utf-8").strip()

            user, stderr, retcode = exec_cmd("whoami")
            user = str(user, "utf-8").strip()
            cluster_role_binding_name = "cluster-admin-{}".format(user)
            self.kubernetes.create_cluster_role_binding(cluster_role_binding_name=cluster_role_binding_name,
                                                        user_name=user_account,
                                                        cluster_role_name="cluster-admin")

    def install_gluu_gateway_ui(self):
        self.uninstall_gluu_gateway_ui()
        self.kubernetes.create_namespace(name=self.settings.get("installer-settings.gluuGateway.uI.namespace"),
                                         labels={"APP_NAME": "gluu-gateway-ui"})
        try:
            # Try to get gluu cert + key
            ssl_cert = self.kubernetes.read_namespaced_secret("gluu",
                                                              self.settings.get("installer-settings.namespace")).data["ssl_cert"]
            ssl_key = self.kubernetes.read_namespaced_secret("gluu",
                                                             self.settings.get("installer-settings.namespace")).data["ssl_key"]

            self.kubernetes.patch_or_create_namespaced_secret(name="tls-certificate",
                                                              namespace=self.settings.get("installer-settings.gluuGateway.uI.namespace"),
                                                              literal="tls.crt",
                                                              value_of_literal=ssl_cert,
                                                              secret_type="kubernetes.io/tls",
                                                              second_literal="tls.key",
                                                              value_of_second_literal=ssl_key)

        except (KeyError, Exception):
            logger.error("Could not read Gluu secret. Please check config job pod logs. GG-UI will deploy but fail. "
                         "Please mount crt and key inside gg-ui deployment")
        client_api_server_url = "https://{}.{}.svc.cluster.local:8443".format(
            self.settings.get("client-api.service.clientApiServerServiceName"), self.settings.get("installer-settings.namespace"))
        values_file = Path("./helm/gluu-gateway-ui/values.yaml").resolve()
        values_file_parser = Parser(values_file, True)
        values_file_parser["cloud"]["isDomainRegistered"] = "false"
        if self.settings.get("global.isFqdnRegistered"):
            values_file_parser["cloud"]["isDomainRegistered"] = "true"
        if self.settings.get("global.storageClass.provisioner") in \
                ("microk8s.io/hostpath", "k8s.io/minikube-hostpath"):
            values_file_parser["cloud"]["enabled"] = False
        if "aws" in self.settings.get("installer-settings.volumeProvisionStrategy"):
            values_file_parser["cloud"]["provider"] = "eks"
        values_file_parser["dbUser"] = self.settings.get("installer-settings.gluuGateway.uI.postgresUser")
        values_file_parser["kongAdminUrl"] = "https://{}-kong-admin.{}.svc.cluster.local:8444".format(
            self.settings.get("installer-settings.kong.releaseName"), self.settings.get("installer-settings.kong.namespace"))
        values_file_parser["dbHost"] = self.settings.get("config.configmap.cnJackrabbitPostgresHost")
        values_file_parser["dbDatabase"] = self.settings.get("installer-settings.gluuGateway.uI.postgresDatabaseName")
        values_file_parser["clientApiServerUrl"] = client_api_server_url
        values_file_parser["image"]["repository"] = self.settings.get("GLUU_GATEWAY_UI_IMAGE_NAME")
        values_file_parser["image"]["tag"] = self.settings.get("GLUU_GATEWAY_UI_IMAGE_TAG")
        values_file_parser["loadBalancerIp"] = self.settings.get("global.lbIp")
        values_file_parser["dbPassword"] = self.settings.get("installer-settings.gluuGateway.uI.postgresPassword")
        values_file_parser["opServerUrl"] = "https://" + self.settings.get("global.fqdn")
        values_file_parser["ggHost"] = self.settings.get("global.fqdn") + "/gg-ui/"
        values_file_parser["ggUiRedirectUrlHost"] = self.settings.get("global.fqdn") + "/gg-ui/"
        # Register new client if one was not provided
        if not values_file_parser["clientApiId"] or \
                not values_file_parser["clientId"] or \
                not values_file_parser["clientSecret"]:
            client_api_id, client_id, client_secret = register_op_client(self.settings.get("installer-settings.namespace"),
                                                                         "konga-client",
                                                                         self.settings.get("global.fqdn"),
                                                                         client_api_server_url,
                                                                         self.settings.get('installer-settings.releaseName'))
            if not client_api_id:
                values_file_parser.dump_it()
                logger.error("Due to a failure in konga client registration the installation has stopped."
                             " Please register as suggested above manually and enter the values returned"
                             " for clientApiId, clientId, "
                             "and clientSecret inside ./helm/gluu-gateway-ui/values.yaml then run "
                             "helm install {} -f ./helm/gluu-gateway-ui/values.yaml ./helm/gluu-gateway-ui "
                             "--namespace={}".format(
                    self.settings.get('installer-settings.gluuGateway.uI.releaseName'),
                    self.settings.get("installer-settings.gluuGateway.uI.namespace")))
                raise SystemExit(1)
            values_file_parser["clientApiId"] = client_api_id
            values_file_parser["clientId"] = client_id
            values_file_parser["clientSecret"] = client_secret

        values_file_parser.dump_it()
        exec_cmd("helm install {} -f ./helm/gluu-gateway-ui/values.yaml ./helm/gluu-gateway-ui --namespace={}".format(
            self.settings.get('installer-settings.gluuGateway.uI.releaseName'),
            self.settings.get("installer-settings.gluuGateway.uI.namespace")))

    def install_gluu_gateway_dbmode(self):
        self.uninstall_gluu_gateway_dbmode()
        self.kubernetes.create_namespace(name=self.settings.get("installer-settings.gluuGateway.kong.namespace"),
                                         labels={"app": "ingress-kong"})
        encoded_kong_pass_bytes = base64.b64encode(self.settings.get("installer-settings.gluuGateway.kong.postgresPassword").encode("utf-8"))
        encoded_kong_pass_string = str(encoded_kong_pass_bytes, "utf-8")
        self.kubernetes.patch_or_create_namespaced_secret(name="kong-postgres-pass",
                                                          namespace=self.settings.get("installer-settings.gluuGateway.kong.namespace"),
                                                          literal="CN_KONG_PG_PASSWORD",
                                                          value_of_literal=encoded_kong_pass_string)
        exec_cmd("helm repo add kong https://charts.konghq.com")
        exec_cmd("helm repo update")
        exec_cmd("helm install {} kong/kong "
                 "--set ingressController.installCRDs=false "
                 "--set image.repository={} "
                 "--set image.tag={} "
                 "--set env.database=postgres "
                 "--set env.pg_user={} "
                 "--set env.pg_password.valueFrom.secretKeyRef.name=kong-postgres-pass "
                 "--set env.pg_password.valueFrom.secretKeyRef.key=CN_KONG_PG_PASSWORD "
                 "--set env.pg_host={} "
                 "--set admin.enabled=true "
                 "--set admin.type=ClusterIP "
                 "--namespace={}".format(self.settings.get("installer-settings.gluuGateway.kong.releaseName"),
                                         self.settings.get("installer-settings.gluuGateway.kong.image.repository"),
                                         self.settings.get("installer-settings.gluuGateway.kong.image.tag"),
                                         self.settings.get("installer-settings.gluuGateway.kong.postgresUser"),
                                         self.settings.get("config.configmap.cnJackrabbitPostgresHost"),
                                         self.settings.get("installer-settings.gluuGateway.kong.namespace")))

    def uninstall_gluu_gateway_dbmode(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings.get('installer-settings.gluuGateway.kong.releaseName'),
                                                        self.settings.get("installer-settings.gluuGateway.kong.namespace")))

    def uninstall_gluu_gateway_ui(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings.get('installer-settings.gluuGateway.uI.releaseName'),
                                                        self.settings.get("installer-settings.gluuGateway.uI.namespace")))

    def uninstall_kong(self):
        logger.info("Removing gluu gateway kong...")
        self.kubernetes.delete_job(self.settings.get("installer-settings.gluuGateway.kong.namespace"), "app=kong-migration-job")
        self.kubernetes.delete_custom_resource("kongconsumers.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("kongcredentials.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("kongingresses.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("kongplugins.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("tcpingresses.configuration.konghq.com")
        self.kubernetes.delete_custom_resource("kongclusterplugins.configuration.konghq.com")
        self.kubernetes.delete_cluster_role("kong-ingress-clusterrole")
        self.kubernetes.delete_service_account("kong-serviceaccount", self.settings.get("installer-settings.gluuGateway.kong.namespace"))
        self.kubernetes.delete_cluster_role_binding("kong-ingress-clusterrole-nisa-binding")
        self.kubernetes.delete_config_map_using_name("kong-server-blocks", self.settings.get("installer-settings.gluuGateway.kong.namespace"))
        self.kubernetes.delete_service("kong-proxy", self.settings.get("installer-settings.gluuGateway.kong.namespace"))
        self.kubernetes.delete_service("kong-validation-webhook", self.settings.get("installer-settings.gluuGateway.kong.namespace"))
        self.kubernetes.delete_service("kong-admin", self.settings.get("installer-settings.gluuGateway.kong.namespace"))
        self.kubernetes.delete_deployment_using_name("ingress-kong", self.settings.get("installer-settings.gluuGateway.kong.namespace"))
