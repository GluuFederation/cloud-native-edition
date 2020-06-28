"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles Helm Gluu Chart
"""

from pathlib import Path
from .yamlparser import Parser
from .common import get_logger, exec_cmd
from .kubeapi import Kubernetes
from .couchbase import Couchbase
from ast import literal_eval
import time
import socket
import base64

logger = get_logger("gluu-helm          ")


def register_op_client(namespace, client_name, op_host, oxd_url):
    """
    Registers an op client using oxd.
    :param namespace:
    :param client_name:
    :param op_host:
    :param oxd_url:
    :return:
    """
    kubernetes = Kubernetes()
    logger.info("Registering a client : {}".format(client_name))
    oxd_id, client_id, client_secret = "", "", ""
    
    data = '{"redirect_uris": ["https://' + op_host + '/gg-ui/"], "op_host": "' + op_host + \
           '", "post_logout_redirect_uris": ["https://' + op_host + \
           '/gg-ui/"], "scope": ["openid", "oxd", "permission", "username"], ' \
           '"grant_types": ["authorization_code", "client_credentials"], "client_name": "' + client_name + '"}'

    exec_curl_command = ["curl", "-k", "-s", "--location", "--request", "POST",
                         "{}/register-site".format(oxd_url), "--header",
                         "Content-Type: application/json", "--data-raw",
                         data]
    try:
        client_registration_response = \
            kubernetes.connect_get_namespaced_pod_exec(exec_command=exec_curl_command,
                                                       app_label="app=oxauth",
                                                       namespace=namespace,
                                                       stdout=False)

        client_registration_response_dict = literal_eval(client_registration_response)
        oxd_id = client_registration_response_dict["oxd_id"]
        client_id = client_registration_response_dict["client_id"]
        client_secret = client_registration_response_dict["client_secret"]
    except (IndexError, Exception):
        manual_curl_command = " ".join(exec_curl_command)
        logger.error("Registeration of client : {} failed. Please do so manually by calling\n{}".format(
            client_name, manual_curl_command))
    return oxd_id, client_id, client_secret


class Helm(object):
    def __init__(self, settings):
        self.values_file = Path("./helm/gluu/values.yaml").resolve()
        self.settings = settings
        self.kubernetes = Kubernetes()
        self.ldap_backup_release_name = self.settings['GLUU_HELM_RELEASE_NAME'] + "-ldap-backup"
        if self.settings["DEPLOYMENT_ARCH"] == "gke":
            # Clusterrolebinding needs to be created for gke with CB or kubeDB installed
            if self.settings["INSTALL_REDIS"] == "Y" or \
                    self.settings["INSTALL_GLUU_GATEWAY"] == "Y" or \
                    self.settings["INSTALL_COUCHBASE"] == "Y":
                user_account, stderr, retcode = exec_cmd("gcloud config get-value core/account")
                user_account = str(user_account, "utf-8").strip()

                user, stderr, retcode = exec_cmd("whoami")
                user = str(user, "utf-8").strip()
                cluster_role_binding_name = "cluster-admin-{}".format(user)
                self.kubernetes.create_cluster_role_binding(cluster_role_binding_name=cluster_role_binding_name,
                                                            user_name=user_account,
                                                            cluster_role_name="cluster-admin")

    def wait_for_nginx_add(self):
        hostname_ip = None
        while True:
            try:
                if hostname_ip:
                    break
                if self.settings["DEPLOYMENT_ARCH"] == "eks":
                    hostname_ip = self.kubernetes.read_namespaced_service(
                        name=self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller",
                        namespace=self.settings["NGINX_INGRESS_NAMESPACE"]).status.load_balancer.ingress[0].hostname
                    self.settings["LB_ADD"] = hostname_ip
                    if self.settings["AWS_LB_TYPE"] == "nlb":
                        ip_static = socket.gethostbyname(str(hostname_ip))
                        if ip_static:
                            break
                elif self.settings["DEPLOYMENT_ARCH"] == "local":
                    self.settings["LB_ADD"] = self.settings['NGINX_INGRESS_RELEASE_NAME'] + \
                                              "-nginx-ingress-controller." + \
                                              self.settings["NGINX_INGRESS_NAMESPACE"] + \
                                              ".svc.cluster.local"
                    break
                else:
                    hostname_ip = self.kubernetes.read_namespaced_service(
                        name=self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller",
                        namespace=self.settings["NGINX_INGRESS_NAMESPACE"]).status.load_balancer.ingress[0].ip
                    self.settings["HOST_EXT_IP"] = hostname_ip
            except (TypeError, AttributeError):
                logger.info("Waiting for address..")
                time.sleep(10)

    def check_install_nginx_ingress(self, install_ingress=True):
        """
        Helm installs nginx ingress or checks to recieve and ip or address
        :param install_ingress:
        """
        if install_ingress:
            self.kubernetes.delete_custom_resource("virtualservers.k8s.nginx.org")
            self.kubernetes.delete_custom_resource("virtualserverroutes.k8s.nginx.org")
            self.kubernetes.delete_cluster_role("ingress-nginx-nginx-ingress")
            self.kubernetes.delete_cluster_role_binding("ingress-nginx-nginx-ingress")
            self.kubernetes.create_namespace(name=self.settings["NGINX_INGRESS_NAMESPACE"])
            self.kubernetes.delete_cluster_role(
                self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller")
            self.kubernetes.delete_cluster_role_binding(
                self.settings['NGINX_INGRESS_RELEASE_NAME'] + "-nginx-ingress-controller")
            try:
                exec_cmd("helm repo add stable https://kubernetes-charts.storage.googleapis.com")
                exec_cmd("helm repo update")
            except FileNotFoundError:
                logger.error("Helm v3 is not installed. Please install it to continue "
                             "https://helm.sh/docs/intro/install/")
                raise SystemExit(1)
        command = "helm install {} stable/nginx-ingress --namespace={}".format(
            self.settings['NGINX_INGRESS_RELEASE_NAME'], self.settings["NGINX_INGRESS_NAMESPACE"])
        if self.settings["DEPLOYMENT_ARCH"] == "minikube":
            exec_cmd("minikube addons enable ingress")
        if self.settings["DEPLOYMENT_ARCH"] == "eks":
            if self.settings["AWS_LB_TYPE"] == "nlb":
                if install_ingress:
                    nlb_annotation = "--set controller.service.annotations={" \
                                     "'service.beta.kubernetes.io/aws-load-balancer-type':'nlb'} "
                    exec_cmd(command + nlb_annotation)
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
            self.wait_for_nginx_add()

        if self.settings["DEPLOYMENT_ARCH"] == "gke" or \
                self.settings["DEPLOYMENT_ARCH"] == "aks" or \
                self.settings["DEPLOYMENT_ARCH"] == "do" or \
                self.settings["DEPLOYMENT_ARCH"] == "local":
            if install_ingress:
                exec_cmd(command)
            self.wait_for_nginx_add()

    def analyze_global_values(self):
        """
        Parses Gluu values.yaml with the input information from prompts
        """
        values_file_parser = Parser(self.values_file, True)
        if self.settings["DEPLOYMENT_ARCH"] == "minikube":
            provisioner = "k8s.io/minikube-hostpath"
        elif self.settings["DEPLOYMENT_ARCH"] == "eks":
            provisioner = "kubernetes.io/aws-ebs"
        elif self.settings["DEPLOYMENT_ARCH"] == "gke":
            provisioner = "kubernetes.io/gce-pd"
        elif self.settings["DEPLOYMENT_ARCH"] == "aks":
            provisioner = "kubernetes.io/azure-disk"
        elif self.settings["DEPLOYMENT_ARCH"] == "do":
            provisioner = "dobs.csi.digitalocean.com"
        elif self.settings["DEPLOYMENT_ARCH"] == "local":
            provisioner = "openebs.io/local"
        else:
            provisioner = "microk8s.io/hostpath"
        values_file_parser["global"]["provisioner"] = provisioner
        values_file_parser["global"]["nginxIp"] = self.settings["HOST_EXT_IP"]
        values_file_parser["global"]["domain"] = self.settings["GLUU_FQDN"]
        values_file_parser["global"]["isDomainRegistered"] = "false"
        if self.settings["IS_GLUU_FQDN_REGISTERED"] == "Y":
            values_file_parser["global"]["isDomainRegistered"] = "true"
        if self.settings["GLUU_CACHE_TYPE"] == "REDIS":
            values_file_parser["config"]["configmap"]["gluuRedisUrl"] = self.settings["REDIS_URL"]
            values_file_parser["config"]["configmap"]["gluuRedisType"] = self.settings["REDIS_TYPE"]
            values_file_parser["config"]["configmap"]["gluuRedisUseSsl"] = self.settings["REDIS_USE_SSL"]
            values_file_parser["config"]["configmap"]["gluuRedisSslTruststore"] = self.settings["REDIS_SSL_TRUSTSTORE"]
            values_file_parser["config"]["configmap"]["gluuRedisSentinelGroup"] = self.settings["REDIS_SENTINEL_GROUP"]
            values_file_parser["config"]["redisPass"] = self.settings["REDIS_PW"]
        if self.settings["DEPLOYMENT_ARCH"] == "microk8s" or self.settings["DEPLOYMENT_ARCH"] == "minikube" \
                or self.settings["TEST_ENVIRONMENT"] == "Y":
            values_file_parser["global"]["cloud"]["testEnviroment"] = True
        values_file_parser["config"]["configmap"]["lbAddr"] = self.settings["LB_ADD"]
        values_file_parser["global"]["gluuPersistenceType"] = self.settings["PERSISTENCE_BACKEND"]
        values_file_parser["config"]["configmap"]["gluuPersistenceType"] = self.settings["PERSISTENCE_BACKEND"]
        values_file_parser["config"]["configmap"]["gluuPersistenceLdapMapping"] = self.settings["HYBRID_LDAP_HELD_DATA"]
        if self.settings["PERSISTENCE_BACKEND"] != "ldap" and self.settings["INSTALL_COUCHBASE"] == "Y":
            values_file_parser["config"]["configmap"]["gluuCouchbaseUrl"] = self.settings["COUCHBASE_URL"]
            values_file_parser["config"]["configmap"]["gluuCouchbaseUser"] = self.settings["COUCHBASE_USER"]
            values_file_parser["config"]["configmap"]["gluuCouchbaseCrt"] = self.settings["COUCHBASE_CRT"]
            values_file_parser["config"]["configmap"]["gluuCouchbasePass"] = self.settings["COUCHBASE_PASSWORD"]
        values_file_parser["global"]["oxauth"]["enabled"] = True
        values_file_parser["global"]["persistence"]["enabled"] = True
        values_file_parser["global"]["oxtrust"]["enabled"] = True
        values_file_parser["global"]["config"]["enabled"] = True
        values_file_parser["global"]["opendj"]["enabled"] = False
        values_file_parser["global"]["fido2"]["enabled"] = False
        if self.settings["ENABLE_FIDO2"] == "Y":
            values_file_parser["global"]["fido2"]["enabled"] = True
        values_file_parser["global"]["scim"]["enabled"] = False
        if self.settings["ENABLE_SCIM"] == "Y":
            values_file_parser["global"]["scim"]["enabled"] = True
        if self.settings["INSTALL_JACKRABBIT"] == "Y":
            values_file_parser["global"]["jackrabbit"]["enabled"] = True
            values_file_parser["config"]["configmap"]["gluuJcaRmiUrl"] = self.settings["JACKRABBIT_URL"] + "/rmi"
            values_file_parser["config"]["configmap"]["gluuJcaUrl"] = self.settings["JACKRABBIT_URL"]
            values_file_parser["config"]["configmap"]["gluuJcaUsername"] = self.settings["JACKRABBIT_USER"]

        if self.settings["PERSISTENCE_BACKEND"] == "hybrid" or \
                self.settings["PERSISTENCE_BACKEND"] == "ldap":
            values_file_parser["global"]["opendj"]["enabled"] = True

        values_file_parser["global"]["oxshibboleth"]["enabled"] = False
        if self.settings["ENABLE_OXSHIBBOLETH"] == "Y":
            values_file_parser["global"]["oxshibboleth"]["enabled"] = True
            values_file_parser["config"]["configmap"]["gluuSyncShibManifests"] = True

        values_file_parser["global"]["oxd-server"]["enabled"] = False
        if self.settings["ENABLE_OXD"] == "Y":
            values_file_parser["global"]["oxd-server"]["enabled"] = True
            values_file_parser["config"]["configmap"]["gluuOxdApplicationCertCn"] = \
                self.settings["OXD_APPLICATION_KEYSTORE_CN"]
            values_file_parser["config"]["configmap"]["gluuOxdAdminCertCn"] = self.settings["OXD_ADMIN_KEYSTORE_CN"]

        values_file_parser["opendj"]["gluuRedisEnabled"] = False
        if self.settings["GLUU_CACHE_TYPE"] == "REDIS":
            values_file_parser["opendj"]["gluuRedisEnabled"] = True

        values_file_parser["global"]["nginx-ingress"]["enabled"] = True

        values_file_parser["global"]["cr-rotate"]["enabled"] = False
        if self.settings["ENABLE_CACHE_REFRESH"] == "Y":
            values_file_parser["global"]["cr-rotate"]["enabled"] = True

        values_file_parser["global"]["oxauth-key-rotation"]["enabled"] = False
        if self.settings["ENABLE_OXAUTH_KEY_ROTATE"] == "Y":
            values_file_parser["global"]["oxauth-key-rotation"]["enabled"] = True
            values_file_parser["oxauth-key-rotation"]["keysLife"] = self.settings["OXAUTH_KEYS_LIFE"]

        values_file_parser["config"]["orgName"] = self.settings["ORG_NAME"]
        values_file_parser["config"]["email"] = self.settings["EMAIL"]
        values_file_parser["config"]["adminPass"] = self.settings["ADMIN_PW"]
        values_file_parser["config"]["ldapPass"] = self.settings["LDAP_PW"]
        values_file_parser["config"]["countryCode"] = self.settings["COUNTRY_CODE"]
        values_file_parser["config"]["state"] = self.settings["STATE"]
        values_file_parser["config"]["city"] = self.settings["CITY"]
        values_file_parser["config"]["configmap"]["gluuCacheType"] = self.settings["GLUU_CACHE_TYPE"]
        values_file_parser["opendj"]["replicas"] = self.settings["LDAP_REPLICAS"]
        values_file_parser["opendj"]["persistence"]["size"] = self.settings["LDAP_STORAGE_SIZE"]
        if self.settings["ENABLE_OXTRUST_API_BOOLEAN"] == "true":
            values_file_parser["config"]["configmap"]["gluuOxtrustApiEnabled"] = True
        if self.settings["ENABLE_OXTRUST_TEST_MODE_BOOLEAN"] == "true":
            values_file_parser["config"]["configmap"]["gluuOxtrustApiTestMode"] = True
        if self.settings["ENABLE_CASA_BOOLEAN"] == "true":
            values_file_parser["config"]["configmap"]["gluuCasaEnabled"] = True
            values_file_parser["config"]["configmap"]["gluuSyncCasaManifests"] = True

        if self.settings["ENABLE_OXPASSPORT_BOOLEAN"] == "true":
            values_file_parser["config"]["configmap"]["gluuPassportEnabled"] = True
        if self.settings["ENABLE_RADIUS_BOOLEAN"] == "true":
            values_file_parser["config"]["configmap"]["gluuRadiusEnabled"] = True
        if self.settings["ENABLE_SAML_BOOLEAN"] == "true":
            values_file_parser["config"]["configmap"]["gluuSamlEnabled"] = True

        values_file_parser["oxpassport"]["resources"] = {}
        values_file_parser["nginx-ingress"]["ingress"]["enabled"] = True
        values_file_parser["nginx-ingress"]["ingress"]["hosts"] = [self.settings["GLUU_FQDN"]]
        values_file_parser["nginx-ingress"]["ingress"]["tls"][0]["hosts"] = [self.settings["GLUU_FQDN"]]
        values_file_parser["casa"]["image"]["repository"] = self.settings["CASA_IMAGE_NAME"]
        values_file_parser["casa"]["image"]["tag"] = self.settings["CASA_IMAGE_TAG"]
        values_file_parser["config"]["image"]["repository"] = self.settings["CONFIG_IMAGE_NAME"]
        values_file_parser["config"]["image"]["tag"] = self.settings["CONFIG_IMAGE_TAG"]
        values_file_parser["cr-rotate"]["image"]["repository"] = self.settings["CACHE_REFRESH_ROTATE_IMAGE_NAME"]
        values_file_parser["cr-rotate"]["image"]["tag"] = self.settings["CACHE_REFRESH_ROTATE_IMAGE_TAG"]
        values_file_parser["oxauth-key-rotation"]["image"]["repository"] = self.settings["CERT_MANAGER_IMAGE_NAME"]
        values_file_parser["oxauth-key-rotation"]["image"]["tag"] = self.settings["CERT_MANAGER_IMAGE_TAG"]
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
        try:
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
        except FileNotFoundError:
            logger.error("Helm v3 is not installed. Please install it to continue "
                         "https://helm.sh/docs/intro/install/")
            raise SystemExit(1)

    def install_gluu_gateway_ui(self):
        self.uninstall_gluu_gateway_ui()
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

        except (KeyError, Exception):
            logger.error("Could not read Gluu secret. Please check config job pod logs. GG-UI will deploy but fail. "
                         "Please mount crt and key inside gg-ui deployment")
        oxd_server_url = "https://{}.{}.svc.cluster.local:8443".format(
            self.settings["OXD_APPLICATION_KEYSTORE_CN"], self.settings["GLUU_NAMESPACE"])
        values_file = Path("./helm/gluu-gateway-ui/values.yaml").resolve()
        values_file_parser = Parser(values_file, True)
        values_file_parser["global"]["isDomainRegistered"] = "false"
        if self.settings["IS_GLUU_FQDN_REGISTERED"] == "Y":
            values_file_parser["global"]["isDomainRegistered"] = "true"
        if self.settings["DEPLOYMENT_ARCH"] == "microk8s" or self.settings["DEPLOYMENT_ARCH"] == "minikube":
            values_file_parser["cloud"]["enabled"] = False
        values_file_parser["cloud"]["provider"] = self.settings["DEPLOYMENT_ARCH"]
        values_file_parser["dbUser"] = self.settings["GLUU_GATEWAY_UI_PG_USER"]
        values_file_parser["kongAdminUrl"] = "https://{}-kong-admin.{}.svc.cluster.local:8444".format(
            self.settings["KONG_HELM_RELEASE_NAME"], self.settings["KONG_NAMESPACE"])
        values_file_parser["dbHost"] = self.settings["POSTGRES_URL"]
        values_file_parser["dbDatabase"] = self.settings["GLUU_GATEWAY_UI_DATABASE"]
        values_file_parser["oxdServerUrl"] = oxd_server_url
        # Register new client if one was not provided
        if not values_file_parser["oxdId"] or \
                not values_file_parser["clientId"] or \
                not values_file_parser["clientSecret"]:
            oxd_id, client_id, client_secret = register_op_client(self.settings["GLUU_NAMESPACE"],
                                                                  "konga-client",
                                                                  self.settings["GLUU_FQDN"],
                                                                  oxd_server_url)
            values_file_parser["oxdId"] = oxd_id
            values_file_parser["clientId"] = client_id
            values_file_parser["clientSecret"] = client_secret
        values_file_parser["loadBalancerIp"] = self.settings["HOST_EXT_IP"]
        values_file_parser["dbPassword"] = self.settings["GLUU_GATEWAY_UI_PG_PASSWORD"]
        values_file_parser["opServerUrl"] = "https://" + self.settings["GLUU_FQDN"]
        values_file_parser["ggHost"] = self.settings["GLUU_FQDN"] + "/gg-ui/"
        values_file_parser["ggUiRedirectUrlHost"] = self.settings["GLUU_FQDN"] + "/gg-ui/"
        values_file_parser.dump_it()
        exec_cmd("helm install {} -f ./helm/gluu-gateway-ui/values.yaml ./helm/gluu-gateway-ui --namespace={}".format(
            self.settings['GLUU_GATEWAY_UI_HELM_RELEASE_NAME'], self.settings["GLUU_GATEWAY_UI_NAMESPACE"]))

    def install_gluu_gateway_dbmode(self):
        self.uninstall_gluu_gateway_dbmode()
        self.kubernetes.create_namespace(name=self.settings["KONG_NAMESPACE"])
        encoded_kong_pass_bytes = base64.b64encode(self.settings["KONG_PG_PASSWORD"].encode("utf-8"))
        encoded_kong_pass_string = str(encoded_kong_pass_bytes, "utf-8")
        self.kubernetes.patch_or_create_namespaced_secret(name="kong-postgres-pass",
                                                          namespace=self.settings["KONG_NAMESPACE"],
                                                          literal="KONG_PG_PASSWORD",
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
                 "--set env.pg_password.valueFrom.secretKeyRef.key=KONG_PG_PASSWORD "
                 "--set env.pg_host={} "
                 "--set admin.enabled=true "
                 "--set admin.type=ClusterIP "
                 "--namespace={}".format(self.settings["KONG_HELM_RELEASE_NAME"],
                                         self.settings["GLUU_GATEWAY_IMAGE_NAME"],
                                         self.settings["GLUU_GATEWAY_IMAGE_TAG"],
                                         self.settings["KONG_PG_USER"],
                                         self.settings["POSTGRES_URL"],
                                         self.settings["KONG_NAMESPACE"]))

    def install_kubedb(self):
        self.uninstall_kubedb()
        self.kubernetes.create_namespace(name="gluu-kubedb")
        try:
            exec_cmd("helm repo add appscode https://charts.appscode.com/stable/")
            exec_cmd("helm repo update")
            exec_cmd("helm install kubedb-operator appscode/kubedb  --version v0.13.0-rc.0 "
                     "--namespace gluu-kubedb")
            self.kubernetes.check_pods_statuses("gluu-kubedb", "app=kubedb")
            exec_cmd("helm install kubedb-catalog appscode/kubedb-catalog  --version v0.13.0-rc.0 "
                     "--namespace gluu-kubedb")
        except FileNotFoundError:
            logger.error("Helm v3 is not installed. Please install it to continue "
                         "https://helm.sh/docs/intro/install/")
            raise SystemExit(1)

    def uninstall_gluu_gateway_dbmode(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings['KONG_HELM_RELEASE_NAME'],
                                                        self.settings["KONG_NAMESPACE"]))

    def uninstall_gluu_gateway_ui(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings['GLUU_GATEWAY_UI_HELM_RELEASE_NAME'],
                                                        self.settings["GLUU_GATEWAY_UI_NAMESPACE"]))

    def uninstall_kubedb(self):
        logger.info("Deleting KubeDB...This may take a little while.")
        try:
            exec_cmd("helm repo add appscode https://charts.appscode.com/stable/")
            exec_cmd("helm repo update")
            exec_cmd("helm delete kubedb-operator --namespace gluu-kubedb")
            exec_cmd("helm delete kubedb-catalog --namespace gluu-kubedb")
            time.sleep(20)
        except FileNotFoundError:
            logger.error("Helm v3 is not installed. Please install it to continue "
                         "https://helm.sh/docs/intro/install/")
            raise SystemExit(1)

    def uninstall_gluu(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings['GLUU_HELM_RELEASE_NAME'],
                                                        self.settings["GLUU_NAMESPACE"]))
        exec_cmd("helm delete {} --namespace={}".format(self.ldap_backup_release_name,
                                                        self.settings["GLUU_NAMESPACE"]))

    def uninstall_nginx_ingress(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings['NGINX_INGRESS_RELEASE_NAME'],
                                                        self.settings["NGINX_INGRESS_NAMESPACE"]))
