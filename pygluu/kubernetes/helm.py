"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles Helm Gluu Chart
"""

from pathlib import Path
from .yamlparser import Parser
from .common import get_logger, exec_cmd, register_op_client
from .kubeapi import Kubernetes
from .couchbase import Couchbase
import time
import socket
import base64

logger = get_logger("gluu-helm          ")


class Helm(object):
    def __init__(self, settings):
        self.values_file = Path("./helm/gluu/values.yaml").resolve()
        self.settings = settings
        self.kubernetes = Kubernetes()
        self.ldap_backup_release_name = self.settings['GLUU_HELM_RELEASE_NAME'] + "-ldap-backup"

    def check_install_nginx_ingress(self, install_ingress=True):
        """
        Helm installs nginx ingress or checks to recieve and ip or address
        :param install_ingress:
        """
        if install_ingress:
            self.kubernetes.delete_custom_resource("virtualservers.k8s.nginx.org")
            self.kubernetes.delete_custom_resource("virtualserverroutes.k8s.nginx.org")
            self.kubernetes.delete_namespace(self.settings["NGINX_INGRESS_NAMESPACE"])
            self.kubernetes.create_namespace(name=self.settings["NGINX_INGRESS_NAMESPACE"])
            self.kubernetes.delete_cluster_role(
                self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller")
            self.kubernetes.delete_cluster_role_binding(
                self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller")
            exec_cmd("helm repo add stable https://kubernetes-charts.storage.googleapis.com")
            exec_cmd("helm repo update")
        command = "helm install {} stable/nginx-ingress --namespace={}".format(
            self.settings['NGINX_INGRESS_RELEASE_NAME'], self.settings["NGINX_INGRESS_NAMESPACE"])
        if self.settings["DEPLOYMENT_ARCH"] == "minikube":
            exec_cmd("minikube addons enable ingress")
        if self.settings["DEPLOYMENT_ARCH"] == "eks":
            lb_hostname = None
            if self.settings["AWS_LB_TYPE"] == "nlb":
                if install_ingress:
                    nlb_annotation = "--set controller.service.annotations={" \
                                     "'service.beta.kubernetes.io/aws-load-balancer-type':'nlb'} "
                    exec_cmd(command + nlb_annotation)
                while True:
                    try:
                        lb_hostname = self.kubernetes.read_namespaced_service(
                            name=self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller",
                            namespace=self.settings["NGINX_INGRESS_NAMESPACE"]).status.load_balancer.ingress[0].hostname
                        ip_static = socket.gethostbyname(str(lb_hostname))
                        if ip_static:
                            break
                    except (TypeError, AttributeError):
                        logger.info("Waiting for LB to receive an ip assignment from AWS")
                    time.sleep(10)
            else:
                if self.settings["USE_ARN"] == "Y":
                    if install_ingress:
                        arn_annotation = "'service.beta.kubernetes.io/aws-load-balancer-ssl-cert':'{}'" \
                            .format(self.settings["ARN_AWS_IAM"])
                        l7_annotation = "{" + \
                                        arn_annotation + \
                                        ", 'service.beta.kubernetes.io/aws-load-balancer-backend" \
                                        "-protocol':'http', " \
                                        "'service.beta.kubernetes.io/aws-load-balancer-ssl-ports" \
                                        "':'https', " \
                                        "'service.beta.kubernetes.io/aws-load-balancer-connection" \
                                        "-idle-timeout':'3600'} "
                        exec_cmd(command + "--set controller.service.annotations=" +
                                 l7_annotation)
                else:
                    if install_ingress:
                        exec_cmd(command)
            while True:
                try:
                    if lb_hostname:
                        break
                    lb_hostname = self.kubernetes.read_namespaced_service(
                        name=self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller",
                        namespace=self.settings["NGINX_INGRESS_NAMESPACE"]).status.load_balancer.ingress[0].hostname
                except (TypeError, AttributeError):
                    logger.info("Waiting for loadbalancer address..")
                    time.sleep(10)
            self.settings["LB_ADD"] = lb_hostname

        if self.settings["DEPLOYMENT_ARCH"] == "gke" or self.settings["DEPLOYMENT_ARCH"] == "aks":
            if install_ingress:
                exec_cmd(command)
            ip = None
            while True:
                try:
                    if ip:
                        break
                    ip = self.kubernetes.read_namespaced_service(
                        name=self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller",
                        namespace=self.settings["NGINX_INGRESS_NAMESPACE"]).status.load_balancer.ingress[0].ip
                except (TypeError, AttributeError):
                    logger.info("Waiting for the ip of the Loadbalancer")
                    time.sleep(10)
            logger.info(ip)
            self.settings["HOST_EXT_IP"] = ip

    def analyze_global_values(self):
        """
        Parses Gluu values.yaml with the input information from prompts
        """
        values_file_parser = Parser(self.values_file, True)
        values_file_parser["global"]["cloud"]["enabled"] = False
        if self.settings["DEPLOYMENT_ARCH"] == "minikube":
            provisioner = "k8s.io/minikube-hostpath"
        elif self.settings["DEPLOYMENT_ARCH"] == "eks":
            provisioner = "kubernetes.io/aws-ebs"
            values_file_parser["global"]["cloud"]["enabled"] = True
        elif self.settings["DEPLOYMENT_ARCH"] == "gke":
            provisioner = "kubernetes.io/gce-pd"
            values_file_parser["global"]["cloud"]["enabled"] = True
        elif self.settings["DEPLOYMENT_ARCH"] == "aks":
            provisioner = "kubernetes.io/azure-disk"
            values_file_parser["global"]["cloud"]["enabled"] = True
        else:
            provisioner = "microk8s.io/hostpath"
        values_file_parser["global"]["provisioner"] = provisioner
        values_file_parser["global"]["nginxNamespace"] = self.settings["NGINX_INGRESS_NAMESPACE"]
        values_file_parser["global"]["nginxIp"] = self.settings["HOST_EXT_IP"]
        values_file_parser["global"]["domain"] = self.settings["GLUU_FQDN"]
        values_file_parser["global"]["isDomainRegistered"] = "false"
        if self.settings["IS_GLUU_FQDN_REGISTERED"] == "Y":
            values_file_parser["global"]["isDomainRegistered"] = "true"
        if self.settings["GLUU_CACHE_TYPE"] == "REDIS":
            values_file_parser["global"]["gluuRedisUrl"] = self.settings["REDIS_URL"]
            values_file_parser["global"]["gluuRedisType"] = self.settings["REDIS_TYPE"]
            values_file_parser["global"]["gluuRedisUseSsl"] = self.settings["REDIS_USE_SSL"]
            values_file_parser["global"]["gluuRedisSslTruststore"] = self.settings["REDIS_SSL_TRUSTSTORE"]
            values_file_parser["global"]["gluuRedisSentinelGroup"] = self.settings["REDIS_SENTINEL_GROUP"]

        values_file_parser["global"]["lbAddr"] = self.settings["LB_ADD"]
        values_file_parser["global"]["gluuPersistenceType"] = self.settings["PERSISTENCE_BACKEND"]
        values_file_parser["global"]["gluuPersistenceLdapMapping"] = "default"
        values_file_parser["global"]["gluuPersistenceLdapMapping"] = self.settings["HYBRID_LDAP_HELD_DATA"]
        values_file_parser["global"]["gluuCouchbaseUrl"] = self.settings["COUCHBASE_URL"]
        values_file_parser["global"]["gluuCouchbaseUser"] = self.settings["COUCHBASE_USER"]
        values_file_parser["global"]["gluuCouchbaseCrt"] = self.settings["COUCHBASE_CRT"]
        values_file_parser["global"]["gluuCouchbasePass"] = self.settings["COUCHBASE_PASSWORD"]
        values_file_parser["global"]["oxauth"]["enabled"] = True
        values_file_parser["global"]["persistence"]["enabled"] = True
        values_file_parser["global"]["oxtrust"]["enabled"] = True
        values_file_parser["global"]["config"]["enabled"] = True
        values_file_parser["global"]["opendj"]["enabled"] = False

        if self.settings["INSTALL_JACKRABBIT"] == "Y":
            values_file_parser["global"]["jackrabbit"]["enabled"] = True
            values_file_parser["global"]["gluuJcaRmiUrl"] = True
            values_file_parser["global"]["gluuJcaUrl"] = True
            values_file_parser["global"]["gluuJcaUsername"] = True

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            values_file_parser["global"]["opendj"]["enabled"] = True

        values_file_parser["global"]["oxshibboleth"]["enabled"] = False
        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            values_file_parser["global"]["oxshibboleth"]["enabled"] = True
            values_file_parser["global"]["gluuSyncShibManifests"] = True

        values_file_parser["global"]["oxd-server"]["enabled"] = False
        if self.settings["ENABLE_OXD"] == "Y":
            values_file_parser["global"]["oxd-server"]["enabled"] = True

        values_file_parser["opendj"]["gluuRedisEnabled"] = False
        if self.settings["GLUU_CACHE_TYPE"] == "REDIS":
            values_file_parser["opendj"]["gluuRedisEnabled"] = True

        values_file_parser["global"]["nginx"]["enabled"] = True

        values_file_parser["global"]["cr-rotate"]["enabled"] = False
        if self.settings["ENABLE_CACHE_REFRESH"] == "Y":
            values_file_parser["global"]["cr-rotate"]["enabled"] = True

        values_file_parser["global"]["key-rotation"]["enabled"] = False
        if self.settings["ENABLE_KEY_ROTATE"] == "Y":
            values_file_parser["global"]["key-rotation"]["enabled"] = True

        values_file_parser["config"]["orgName"] = self.settings["ORG_NAME"]
        values_file_parser["config"]["email"] = self.settings["EMAIL"]
        values_file_parser["config"]["adminPass"] = self.settings["ADMIN_PW"]
        values_file_parser["config"]["ldapPass"] = self.settings["LDAP_PW"]
        values_file_parser["config"]["countryCode"] = self.settings["COUNTRY_CODE"]
        values_file_parser["config"]["state"] = self.settings["STATE"]
        values_file_parser["config"]["city"] = self.settings["CITY"]
        values_file_parser["opendj"]["gluuCacheType"] = self.settings["GLUU_CACHE_TYPE"]
        values_file_parser["opendj"]["replicas"] = self.settings["LDAP_REPLICAS"]
        values_file_parser["opendj"]["persistence"]["size"] = self.settings["LDAP_STORAGE_SIZE"]
        if self.settings["ENABLE_OXTRUST_API_BOOLEAN"] == "true":
            values_file_parser["persistence"]["configmap"]["gluuOxtrustApiEnabled"] = True
        if self.settings["ENABLE_OXTRUST_TEST_MODE_BOOLEAN"] == "true":
            values_file_parser["persistence"]["configmap"]["gluuOxtrustApiTestMode"] = True
        if self.settings["ENABLE_CASA_BOOLEAN"] == "true":
            values_file_parser["persistence"]["configmap"]["gluuCasaEnabled"] = True
            values_file_parser["global"]["gluuSyncCasaManifests"] = True

        if self.settings["ENABLE_OXPASSPORT_BOOLEAN"] == "true":
            values_file_parser["persistence"]["configmap"]["gluuPassportEnabled"] = True
        if self.settings["ENABLE_RADIUS_BOOLEAN"] == "true":
            values_file_parser["persistence"]["configmap"]["gluuRadiusEnabled"] = True
        if self.settings["ENABLE_SAML_BOOLEAN"] == "true":
            values_file_parser["persistence"]["configmap"]["gluuSamlEnabled"] = True

        values_file_parser["oxd-server"]["configmap"]["adminKeystorePassword"] = self.settings["OXD_SERVER_PW"]
        values_file_parser["oxd-server"]["configmap"]["applicationKeystorePassword"] = self.settings["OXD_SERVER_PW"]
        values_file_parser["oxpassport"]["resources"] = {}
        values_file_parser["nginx"]["ingress"]["enabled"] = True
        values_file_parser["nginx"]["ingress"]["hosts"] = [self.settings["GLUU_FQDN"]]
        values_file_parser["nginx"]["ingress"]["tls"][0]["hosts"] = [self.settings["GLUU_FQDN"]]
        values_file_parser["casa"]["image"]["repository"] = self.settings["CASA_IMAGE_NAME"]
        values_file_parser["casa"]["image"]["tag"] = self.settings["CASA_IMAGE_TAG"]
        values_file_parser["config"]["image"]["repository"] = self.settings["CONFIG_IMAGE_NAME"]
        values_file_parser["config"]["image"]["tag"] = self.settings["CONFIG_IMAGE_TAG"]
        values_file_parser["cr-rotate"]["image"]["repository"] = self.settings["CACHE_REFRESH_ROTATE_IMAGE_NAME"]
        values_file_parser["cr-rotate"]["image"]["tag"] = self.settings["CACHE_REFRESH_ROTATE_IMAGE_TAG"]
        values_file_parser["key-rotation"]["image"]["repository"] = self.settings["KEY_ROTATE_IMAGE_NAME"]
        values_file_parser["key-rotation"]["image"]["tag"] = self.settings["KEY_ROTATE_IMAGE_TAG"]
        values_file_parser["opendj"]["image"]["repository"] = self.settings["LDAP_IMAGE_NAME"]
        values_file_parser["opendj"]["image"]["tag"] = self.settings["LDAP_IMAGE_TAG"]
        values_file_parser["persistence"]["image"]["repository"] = self.settings["PERSISTENCE_IMAGE_NAME"]
        values_file_parser["persistence"]["image"]["tag"] = self.settings["PERSISTENCE_IMAGE_TAG"]
        values_file_parser["oxauth"]["image"]["repository"] = self.settings["OXAUTH_IMAGE_NAME"]
        values_file_parser["oxauth"]["image"]["tag"] = self.settings["OXAUTH_IMAGE_TAG"]
        values_file_parser["oxd-server"]["image"]["repository"] = self.settings["OXD_IMAGE_NAME"]
        values_file_parser["oxd-server"]["image"]["tag"] = self.settings["OXD_IMAGE_TAG"]
        values_file_parser["oxpassport"]["image"]["repository"] = self.settings["OXPASSPORT_IMAGE_NAME"]
        values_file_parser["oxpassport"]["image"]["tag"] = self.settings["OXPASSPORT_IMAGE_TAG"]
        values_file_parser["oxshibboleth"]["image"]["repository"] = self.settings["OXSHIBBOLETH_IMAGE_NAME"]
        values_file_parser["oxshibboleth"]["image"]["tag"] = self.settings["OXSHIBBOLETH_IMAGE_TAG"]
        values_file_parser["jackrabbit"]["image"]["repository"] = self.settings["JACKRABBIT_IMAGE_NAME"]
        values_file_parser["jackrabbit"]["image"]["tag"] = self.settings["JACKRABBIT_IMAGE_TAG"]
        values_file_parser["oxtrust"]["image"]["repository"] = self.settings["OXTRUST_IMAGE_NAME"]
        values_file_parser["oxtrust"]["image"]["tag"] = self.settings["OXTRUST_IMAGE_TAG"]
        values_file_parser["radius"]["image"]["repository"] = self.settings["RADIUS_IMAGE_NAME"]
        values_file_parser["radius"]["image"]["tag"] = self.settings["RADIUS_IMAGE_TAG"]
        values_file_parser.dump_it()

    def install_gluu(self, install_ingress=True):
        """
        Helm install Gluu
        :param install_ingress:
        """
        self.kubernetes.create_namespace(name=self.settings["GLUU_NAMESPACE"])
        if self.settings["PERSISTENCE_BACKEND"] != "ldap" and self.settings["INSTALL_COUCHBASE"] == "Y":
            couchbase_app = Couchbase(self.settings)
            couchbase_app.uninstall()
            couchbase_app = Couchbase(self.settings)
            couchbase_app.install()
        self.check_install_nginx_ingress(install_ingress)
        self.analyze_global_values()
        exec_cmd("helm install {} -f {} ./helm/gluu --namespace={}".format(
            self.settings['GLUU_HELM_RELEASE_NAME'], self.values_file, self.settings["GLUU_NAMESPACE"]))

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            values_file = Path("./helm/ldap-backup/values.yaml").resolve()
            values_file_parser = Parser(values_file, True)
            values_file_parser["ldapPass"] = self.settings["LDAP_PW"]
            values_file_parser.dump_it()

            exec_cmd("helm install {} -f ./helm/ldap-backup/values.yaml ./helm/ldap-backup --namespace={}".format(
                self.ldap_backup_release_name, self.settings["GLUU_NAMESPACE"]))

    def install_gluu_gateway_ui(self):
        self.kubernetes.create_namespace(name=self.settings["GLUU_GATEWAY_UI_NAMESPACE"])
        try:
            # Try to get gluu cert + key
            ssl_cert = self.kubernetes.read_namespaced_secret("gluu",
                                                              self.settings["GLUU_NAMESPACE"]).data["ssl_cert"]
            ssl_key = self.kubernetes.read_namespaced_secret("gluu",
                                                             self.settings["GLUU_NAMESPACE"]).data["ssl_key"]

            self.kubernetes.patch_or_create_namespaced_secret(name="tls-certificate",
                                                              namespace=self.settings["GLUU_GATEWAY_UI_NAMESPACE"],
                                                              literal="tls.crt",
                                                              value_of_literal=ssl_cert,
                                                              secret_type="kubernetes.io/tls",
                                                              second_literal="tls.key",
                                                              value_of_second_literal=ssl_key)

        except Exception:
            logger.error("Could not read Gluu secret. Please check config job pod logs. GG-UI will deploy but fail. "
                         "Please mount crt and key inside gg-ui deployment")
        encoded_gg_ui_pg_pass_bytes = base64.b64encode(self.settings["GLUU_GATEWAY_UI_PG_PASSWORD"].encode("utf-8"))
        encoded_gg_ui_pg_pass_string = str(encoded_gg_ui_pg_pass_bytes, "utf-8")
        oxd_server_url = "https://{}.{}.svc.cluster.local:8443".format(
            self.settings["OXD_APPLICATION_KEYSTORE_CN"], self.settings["GLUU_NAMESPACE"])

        self.kubernetes.patch_or_create_namespaced_secret(name="gg-ui-postgres-pass",
                                                          namespace=self.settings["GLUU_GATEWAY_UI_NAMESPACE"],
                                                          literal="DB_PASSWORD",
                                                          value_of_literal=encoded_gg_ui_pg_pass_string)
        values_file = Path("./helm/gluu-gateway-ui/values.yaml").resolve()
        values_file_parser = Parser(values_file, True)
        values_file_parser["dbUser"] = self.settings["GLUU_GATEWAY_UI_PG_USER"]
        values_file_parser["kongAdminUrl"] = "https://kong-admin.{}.svc.cluster.local:8444".format(
            self.settings["KONG_NAMESPACE"])
        values_file_parser["dbHost"] = self.settings["POSTGRES_URL"]
        values_file_parser["dbDatabase"] = self.settings["GLUU_GATEWAY_UI_DATABASE"]
        values_file_parser["oxdServerUrl"] = oxd_server_url
        # Register new client if one was not provided
        if not values_file_parser["oxdId"] or \
            not values_file_parser["clientId"] or \
            not values_file_parser["clientSecret"]:
            oxd_id, client_id, client_secret = register_op_client("konga-client",
                                                                  self.settings["GLUU_FQDN"],
                                                                  oxd_server_url)
            values_file_parser["oxdId"] = oxd_id
            values_file_parser["clientId"] = client_id
            values_file_parser["clientSecret"] = client_secret
        values_file_parser["opServerUrl"] = self.settings["GLUU_FQDN"]
        values_file_parser["ggHost"] = self.settings["GLUU_FQDN"] + "/gg-ui/"
        values_file_parser["ggUiRedirectUrlHost"] = self.settings["GLUU_FQDN"] + "/gg-ui/"

        exec_cmd("helm install {} -f ./helm/gluu-gateway-ui/values.yaml ./helm/gluu-gateway-ui --namespace={}".format(
            self.settings['GLUU_GATEWAY_UI_HELM_RELEASE_NAME'], self.settings["GLUU_GATEWAY_UI_NAMESPACE"]))

    def uninstall_gluu_gateway_ui(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings['GLUU_GATEWAY_UI_HELM_RELEASE_NAME'],
                                                        self.settings["GLUU_GATEWAY_UI_NAMESPACE"]))

    def uninstall_gluu(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings['GLUU_HELM_RELEASE_NAME'],
                                                        self.settings["GLUU_NAMESPACE"]))
        exec_cmd("helm delete {} --namespace={}".format(self.ldap_backup_release_name,
                                                        self.settings["GLUU_NAMESPACE"]))

    def uninstall_nginx_ingress(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings['NGINX_INGRESS_RELEASE_NAME'],
                                                        self.settings["NGINX_INGRESS_NAMESPACE"]))
