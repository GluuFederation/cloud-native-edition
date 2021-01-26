"""
pygluu.kubernetes.helm
~~~~~~~~~~~~~~~~~~~~~~

 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
 Handles Helm Gluu Chart
"""

from pathlib import Path
from pygluu.kubernetes.yamlparser import Parser
from pygluu.kubernetes.helpers import get_logger, exec_cmd
from pygluu.kubernetes.kubeapi import Kubernetes
from pygluu.kubernetes.couchbase import Couchbase
from pygluu.kubernetes.settings import ValuesHandler
import time
import socket
import base64
import secrets

logger = get_logger("gluu-helm          ")


class Gluu(object):
    def __init__(self):
        self.values_file = Path("./helm/gluu/values.yaml").resolve()
        self.upgrade_values_file = Path("./helm/gluu-upgrade/values.yaml").resolve()
        self.settings = ValuesHandler()
        self.kubernetes = Kubernetes()
        self.ldap_backup_release_name = self.settings.get("installer-settings.releaseName") + "-ldap-backup"
        if self.settings.get("CN_DEPLOYMENT_ARCH") == "gke":
            # Clusterrolebinding needs to be created for gke with CB or kubeDB installed
            if self.settings.get("config.configmap.cnCacheType") == "REDIS" or \
                    self.settings.get("CN_INSTALL_GLUU_GATEWAY") == "Y" or \
                    self.settings.get("CN_INSTALL_COUCHBASE") == "Y":
                user_account, stderr, retcode = exec_cmd("gcloud config get-value core/account")
                user_account = str(user_account, "utf-8").strip()

                user, stderr, retcode = exec_cmd("whoami")
                user = str(user, "utf-8").strip()
                cluster_role_binding_name = "cluster-admin-{}".format(user)
                self.kubernetes.create_cluster_role_binding(cluster_role_binding_name=cluster_role_binding_name,
                                                            user_name=user_account,
                                                            cluster_role_name="cluster-admin")

    def prepare_alb(self):
        ingress_parser = Parser("./alb/ingress.yaml", "Ingress")
        ingress_parser["spec"]["rules"][0]["host"] = self.settings.get("CN_FQDN")
        ingress_parser["metadata"]["annotations"]["alb.ingress.kubernetes.io/certificate-arn"] = \
            self.settings.get("CN_ARN_AWS_IAM")
        if not self.settings.get("CN_ARN_AWS_IAM"):
            del ingress_parser["metadata"]["annotations"]["alb.ingress.kubernetes.io/certificate-arn"]

        for path in ingress_parser["spec"]["rules"][0]["http"]["paths"]:
            service_name = path["backend"]["serviceName"]
            if self.settings.get("ENABLE_CASA") != "Y" and service_name == "casa":
                path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
                del ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index]

            if self.settings.get("ENABLE_OXSHIBBOLETH") != "Y" and service_name == "oxshibboleth":
                path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
                del ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index]

            if self.settings.get("ENABLE_OXPASSPORT") != "Y" and service_name == "oxpassport":
                path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
                del ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index]

            if self.settings.get("CN_INSTALL_GLUU_GATEWAY") != "Y" and service_name == "gg-kong-ui":
                path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
                del ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index]
        ingress_parser.dump_it()

    def deploy_alb(self):
        alb_ingress = Path("./alb/ingress.yaml")
        self.kubernetes.create_objects_from_dict(alb_ingress, self.settings.get("CN_NAMESPACE"))
        if self.settings.get("CN_IS_CN_FQDN_REGISTERED") != "Y":
            prompt = input("Please input the DNS of the Application load balancer  created found on AWS UI: ")
            lb_hostname = prompt
            while True:
                try:
                    if lb_hostname:
                        break
                    lb_hostname = self.kubernetes.read_namespaced_ingress(
                        name="gluu", namespace="gluu").status.load_balancer.ingress[0].hostname
                except TypeError:
                    logger.info("Waiting for loadbalancer address..")
                    time.sleep(10)
            self.settings.set("CN_LB_ADD", lb_hostname)

    def wait_for_nginx_add(self):
        hostname_ip = None
        while True:
            try:
                if hostname_ip:
                    break
                if self.settings.get("CN_DEPLOYMENT_ARCH") == "eks":
                    hostname_ip = self.kubernetes.read_namespaced_service(
                        name=self.settings.get('CN_NGINX_INGRESS_RELEASE_NAME') + "-ingress-nginx-controller",
                        namespace=self.settings.get("CN_NGINX_INGRESS_NAMESPACE")).status.load_balancer.ingress[
                        0].hostname
                    self.settings.set("CN_LB_ADD", hostname_ip)
                    if self.settings.get("CN_AWS_LB_TYPE") == "nlb":
                        try:
                            ip_static = socket.gethostbyname(str(hostname_ip))
                            if ip_static:
                                break
                        except socket.gaierror:
                            logger.info("Address has not received an ip yet.")
                elif self.settings.get("CN_DEPLOYMENT_ARCH") == "local":
                    self.settings.set("CN_LB_ADD", self.settings.get('CN_NGINX_INGRESS_RELEASE_NAME') +
                                      "-nginx-ingress-controller." + self.settings.get("CN_NGINX_INGRESS_NAMESPACE") +
                                      ".svc.cluster.local")
                    break
                else:
                    hostname_ip = self.kubernetes.read_namespaced_service(
                        name=self.settings.get('CN_NGINX_INGRESS_RELEASE_NAME') + "-ingress-nginx-controller",
                        namespace=self.settings.get("CN_NGINX_INGRESS_NAMESPACE")).status.load_balancer.ingress[0].ip
                    self.settings.set("CN_HOST_EXT_IP", hostname_ip)
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
            self.kubernetes.create_namespace(name=self.settings.get("CN_NGINX_INGRESS_NAMESPACE"),
                                             labels={"app": "ingress-nginx"})
            self.kubernetes.delete_cluster_role(
                self.settings.get('CN_NGINX_INGRESS_RELEASE_NAME') + "-nginx-ingress-controller")
            self.kubernetes.delete_cluster_role_binding(
                self.settings.get('CN_NGINX_INGRESS_RELEASE_NAME') + "-nginx-ingress-controller")
            try:
                exec_cmd("helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx")
                exec_cmd("helm repo add stable https://charts.helm.sh/stable")
                exec_cmd("helm repo update")
            except FileNotFoundError:
                logger.error("Helm v3 is not installed. Please install it to continue "
                             "https://helm.sh/docs/intro/install/")
                raise SystemExit(1)
        command = "helm install {} ingress-nginx/ingress-nginx --namespace={} ".format(
            self.settings.get('CN_NGINX_INGRESS_RELEASE_NAME'), self.settings.get("CN_NGINX_INGRESS_NAMESPACE"))
        if self.settings.get("CN_DEPLOYMENT_ARCH") == "minikube":
            exec_cmd("minikube addons enable ingress")
        if self.settings.get("CN_DEPLOYMENT_ARCH") == "eks":
            if self.settings.get("CN_AWS_LB_TYPE") == "nlb":
                if install_ingress:
                    nlb_override_values_file = Path("./nginx/aws/aws-nlb-override-values.yaml").resolve()
                    nlb_values = " --values {}".format(nlb_override_values_file)
                    exec_cmd(command + nlb_values)
            else:
                if self.settings.get("CN_USE_ARN") == "Y":
                    if install_ingress:
                        elb_override_values_file = Path("./nginx/aws/aws-elb-override-values.yaml").resolve()
                        elb_file_parser = Parser(elb_override_values_file, True)
                        elb_file_parser["controller"]["service"]["annotations"].update(
                            {"service.beta.kubernetes.io/aws-load-balancer-ssl-cert": self.settings.get(
                                "CN_ARN_AWS_IAM")})
                        elb_file_parser["controller"]["config"]["proxy-real-ip-cidr"] = self.settings.get("CN_VPC_CIDR")
                        elb_file_parser.dump_it()
                        elb_values = " --values {}".format(elb_override_values_file)
                        exec_cmd(command + elb_values)
                else:
                    if install_ingress:
                        exec_cmd(command)

        if self.settings.get("CN_DEPLOYMENT_ARCH") in ("gke", "aks", "do"):
            if install_ingress:
                cloud_override_values_file = Path("./nginx/cloud/cloud-override-values.yaml").resolve()
                cloud_values = " --values {}".format(cloud_override_values_file)
                exec_cmd(command + cloud_values)
        if self.settings.get("CN_DEPLOYMENT_ARCH") == "local":
            if install_ingress:
                baremetal_override_values_file = Path("./nginx/baremetal/baremetal-override-values.yaml").resolve()
                baremetal_values = " --values {}".format(baremetal_override_values_file)
                exec_cmd(command + baremetal_values)
        if self.settings.get("CN_DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            logger.info("Waiting for nginx to be prepared...")
            time.sleep(60)
            self.wait_for_nginx_add()

    def analyze_global_values(self):
        """
        Parses Gluu values.yaml with the input information from prompts
        """
        values_file_parser = Parser(self.values_file, True)
        if self.settings.get("CN_DEPLOYMENT_ARCH") == "minikube":
            provisioner = "k8s.io/minikube-hostpath"
        elif self.settings.get("CN_DEPLOYMENT_ARCH") == "eks":
            provisioner = "kubernetes.io/aws-ebs"
        elif self.settings.get("CN_DEPLOYMENT_ARCH") == "gke":
            provisioner = "kubernetes.io/gce-pd"
        elif self.settings.get("CN_DEPLOYMENT_ARCH") == "aks":
            provisioner = "kubernetes.io/azure-disk"
        elif self.settings.get("CN_DEPLOYMENT_ARCH") == "do":
            provisioner = "dobs.csi.digitalocean.com"
        elif self.settings.get("CN_DEPLOYMENT_ARCH") == "local":
            provisioner = "openebs.io/local"
        else:
            provisioner = "microk8s.io/hostpath"
        values_file_parser["global"]["storageClass"]["provisioner"] = provisioner
        values_file_parser["global"]["lbIp"] = self.settings.get("CN_HOST_EXT_IP")
        values_file_parser["global"]["domain"] = self.settings.get("CN_FQDN")
        values_file_parser["global"]["isDomainRegistered"] = "false"
        if self.settings.get("CN_IS_CN_FQDN_REGISTERED") == "Y":
            values_file_parser["global"]["isDomainRegistered"] = "true"
        if self.settings.get("CN_CACHE_TYPE") == "REDIS":
            values_file_parser["config"]["configmap"]["cnRedisUrl"] = self.settings.get("CN_REDIS_URL")
            values_file_parser["config"]["configmap"]["cnRedisType"] = self.settings.get("CN_REDIS_TYPE")
            values_file_parser["config"]["configmap"]["cnRedisUseSsl"] = self.settings.get("CN_REDIS_USE_SSL")
            values_file_parser["config"]["configmap"]["cnRedisSslTruststore"] = \
                self.settings.get("CN_REDIS_SSL_TRUSTSTORE")
            values_file_parser["config"]["configmap"]["cnRedisSentinelGroup"] = \
                self.settings.get("CN_REDIS_SENTINEL_GROUP")
            values_file_parser["config"]["redisPass"] = self.settings.get("CN_REDIS_PW")
        if self.settings.get("CN_DEPLOYMENT_ARCH") in ("microk8s", "minikube") \
                or self.settings.get("CN_TEST_ENVIRONMENT") == "Y":
            values_file_parser["global"]["cloud"]["testEnviroment"] = True
        values_file_parser["config"]["configmap"]["lbAddr"] = self.settings.get("CN_LB_ADD")
        values_file_parser["global"]["cnPersistenceType"] = self.settings.get("CN_PERSISTENCE_BACKEND")
        values_file_parser["config"]["configmap"]["cnPersistenceType"] = self.settings.get("CN_PERSISTENCE_BACKEND")
        values_file_parser["config"]["configmap"]["cnPersistenceLdapMapping"] = \
            self.settings.get("CN_HYBRID_LDAP_HELD_DATA")
        if self.settings.get("CN_PERSISTENCE_BACKEND") != "ldap":
            values_file_parser["config"]["configmap"]["cnCouchbaseUrl"] = self.settings.get("CN_COUCHBASE_URL")
            values_file_parser["config"]["configmap"]["cnCouchbaseUser"] = self.settings.get("CN_COUCHBASE_USER")
            values_file_parser["config"]["configmap"]["cnCouchbaseIndexNumReplica"] = self.settings.get(
                "CN_COUCHBASE_INDEX_NUM_REPLICA")
            values_file_parser["config"]["configmap"]["cnCouchbaseBucketPrefix"] = self.settings.get(
                "CN_COUCHBASE_BUCKET_PREFIX")
            values_file_parser["config"]["configmap"]["cnCouchbaseSuperUser"] = \
                self.settings.get("CN_COUCHBASE_SUPERUSER")
            values_file_parser["config"]["configmap"]["cnCouchbaseCrt"] = self.settings.get("CN_COUCHBASE_CRT")
            values_file_parser["config"]["configmap"]["cnCouchbasePass"] = self.settings.get("CN_COUCHBASE_PASSWORD")
            values_file_parser["config"]["configmap"]["cnCouchbaseSuperUserPass"] = \
                self.settings.get("CN_COUCHBASE_SUPERUSER_PASSWORD")
        values_file_parser["global"]["auth-server"]["enabled"] = True
        values_file_parser["global"]["persistence"]["enabled"] = True
        values_file_parser["global"]["config"]["enabled"] = True
        values_file_parser["global"]["opendj"]["enabled"] = False
        values_file_parser["global"]["fido2"]["enabled"] = False
        if self.settings.get("ENABLE_FIDO2") == "Y":
            values_file_parser["global"]["fido2"]["enabled"] = True
            values_file_parser["fido2"]["replicas"] = self.settings.get("FIDO2_REPLICAS")
        values_file_parser["global"]["scim"]["enabled"] = False
        if self.settings.get("ENABLE_SCIM") == "Y":
            values_file_parser["global"]["scim"]["enabled"] = True
            values_file_parser["scim"]["replicas"] = self.settings.get("SCIM_REPLICAS")

        if self.settings.get("ENABLE_CONFIG_API") == "Y":
            values_file_parser["global"]["config-api"]["enabled"] = True

        if self.settings.get("CN_INSTALL_JACKRABBIT") == "Y":
            values_file_parser["global"]["jackrabbit"]["enabled"] = True
            values_file_parser["config"]["configmap"]["cnJackrabbitUrl"] = self.settings.get("CN_JACKRABBIT_URL")
            values_file_parser["jackrabbit"]["secrets"]["cnJackrabbitAdminPass"] = \
                self.settings.get("CN_JACKRABBIT_ADMIN_PASSWORD")
            values_file_parser["jackrabbit"]["secrets"]["cnJackrabbitPostgresPass"] = \
                self.settings.get("CN_JACKRABBIT_PG_PASSWORD")
        if self.settings.get("CN_USE_ISTIO_INGRESS") == "Y":
            values_file_parser["global"]["istio"]["ingress"] = True
            values_file_parser["global"]["istio"]["enabled"] = True
            values_file_parser["global"]["istio"]["namespace"] = self.settings.get("CN_ISTIO_SYSTEM_NAMESPACE")
        elif self.settings.get("CN_AWS_LB_TYPE") == "alb":
            values_file_parser["global"]["alb"]["ingress"] = True
        else:
            values_file_parser["nginx-ingress"]["ingress"]["enabled"] = True
            values_file_parser["nginx-ingress"]["ingress"]["hosts"] = [self.settings.get("CN_FQDN")]
            values_file_parser["nginx-ingress"]["ingress"]["tls"][0]["hosts"] = [self.settings.get("CN_FQDN")]
        if self.settings.get("CN_USE_ISTIO") == "Y":
            values_file_parser["global"]["istio"]["enabled"] = True

        values_file_parser["global"]["cnJackrabbitCluster"] = "false"
        if self.settings.get("CN_JACKRABBIT_CLUSTER") == "Y":
            values_file_parser["global"]["cnJackrabbitCluster"] = "true"
            values_file_parser["config"]["configmap"]["cnJackrabbitAdminId"] = \
                self.settings.get("CN_JACKRABBIT_ADMIN_ID")
            values_file_parser["config"]["configmap"]["cnJackrabbitPostgresUser"] = \
                self.settings.get("CN_JACKRABBIT_PG_USER")
            values_file_parser["config"]["configmap"]["cnJackrabbitPostgresDatabaseName"] = \
                self.settings.get("CN_JACKRABBIT_DATABASE")
            values_file_parser["config"]["configmap"]["cnJackrabbitPostgresHost"] = \
                self.settings.get("CN_POSTGRES_URL")
            values_file_parser["config"]["configmap"]["cnJackrabbitPostgresUser"] = \
                self.settings.get("CN_JACKRABBIT_PG_USER")

        if self.settings.get("CN_PERSISTENCE_BACKEND") == "hybrid" or \
                self.settings.get("CN_PERSISTENCE_BACKEND") == "ldap":
            values_file_parser["global"]["opendj"]["enabled"] = True
            # ALPHA-FEATURE: Multi cluster ldap replication
            if self.settings.get("CN_LDAP_MULTI_CLUSTER") == "Y":
                values_file_parser["opendj"]["multiCluster"]["enabled"] = True
                values_file_parser["opendj"]["multiCluster"]["serfAdvertiseAddr"] = \
                    self.settings.get("CN_LDAP_ADVERTISE_ADDRESS")
                serf_key = base64.b64encode(secrets.token_bytes()).decode()
                values_file_parser["opendj"]["multiCluster"]["serfKey"] = serf_key
                values_file_parser["opendj"]["multiCluster"]["serfPeers"] = \
                    self.settings.get("CN_LDAP_SERF_PEERS")
                if self.settings.get("CN_LDAP_SECONDARY_CLUSTER") == "Y":
                    values_file_parser["global"]["persistence"]["enabled"] = False
                values_file_parser["opendj"]["ports"]["tcp-ldaps"]["nodePort"] = \
                    int(self.settings.get("CN_LDAP_ADVERTISE_LDAPS_PORT"))

                values_file_parser["opendj"]["ports"]["tcp-repl"]["port"] = \
                    int(self.settings.get("CN_LDAP_ADVERTISE_REPLICATION_PORT"))
                values_file_parser["opendj"]["ports"]["tcp-repl"]["targetPort"] = \
                    int(self.settings.get("CN_LDAP_ADVERTISE_REPLICATION_PORT"))
                values_file_parser["opendj"]["ports"]["tcp-repl"]["nodePort"] = \
                    int(self.settings.get("CN_LDAP_ADVERTISE_REPLICATION_PORT"))

                values_file_parser["opendj"]["ports"]["tcp-admin"]["port"] = \
                    int(self.settings.get("CN_LDAP_ADVERTISE_ADMIN_PORT"))
                values_file_parser["opendj"]["ports"]["tcp-admin"]["targetPort"] = \
                    int(self.settings.get("CN_LDAP_ADVERTISE_ADMIN_PORT"))
                values_file_parser["opendj"]["ports"]["tcp-admin"]["nodePort"] = \
                    int(self.settings.get("CN_LDAP_ADVERTISE_ADMIN_PORT"))

                values_file_parser["opendj"]["ports"]["tcp-serf"]["nodePort"] = \
                    int(self.settings.get("CN_LDAP_SERF_PORT"))
                values_file_parser["opendj"]["ports"]["udp-serf"]["nodePort"] = \
                    int(self.settings.get("CN_LDAP_SERF_PORT"))

        values_file_parser["global"]["oxshibboleth"]["enabled"] = False
        if self.settings.get("ENABLE_OXSHIBBOLETH") == "Y":
            values_file_parser["global"]["oxshibboleth"]["enabled"] = True
            values_file_parser["config"]["configmap"]["cnSyncShibManifests"] = True

        values_file_parser["global"]["client-api"]["enabled"] = False
        if self.settings.get("ENABLE_CLIENT_API") == "Y":
            values_file_parser["global"]["client-api"]["enabled"] = True
            values_file_parser["config"]["configmap"]["jansClientApiApplicationCertCn"] = \
                self.settings.get("CN_CLIENT_API_APPLICATION_KEYSTORE_CN")
            values_file_parser["config"]["configmap"]["jansClientApiAdminCertCn"] = self.settings.get(
                "CN_CLIENT_API_ADMIN_KEYSTORE_CN")
            values_file_parser["client-api"]["replicas"] = self.settings.get("CLIENT_API_REPLICAS")

        values_file_parser["opendj"]["cnRedisEnabled"] = False
        if self.settings.get("CN_CACHE_TYPE") == "REDIS":
            values_file_parser["opendj"]["cnRedisEnabled"] = True

        values_file_parser["global"]["nginx-ingress"]["enabled"] = True

        values_file_parser["global"]["cr-rotate"]["enabled"] = False
        if self.settings.get("ENABLE_CACHE_REFRESH") == "Y":
            values_file_parser["global"]["cr-rotate"]["enabled"] = True

        values_file_parser["global"]["auth-server-key-rotation"]["enabled"] = False
        if self.settings.get("ENABLE_AUTH_SERVER_KEY_ROTATE") == "Y":
            values_file_parser["global"]["auth-server-key-rotation"]["enabled"] = True
            values_file_parser["auth-server-key-rotation"]["keysLife"] = self.settings.get("AUTH_SERVER_KEYS_LIFE")

        values_file_parser["config"]["orgName"] = self.settings.get("CN_ORG_NAME")
        values_file_parser["config"]["email"] = self.settings.get("CN_EMAIL")
        values_file_parser["config"]["adminPass"] = self.settings.get("CN_ADMIN_PASSWORD")
        values_file_parser["config"]["ldapPass"] = self.settings.get("CN_LDAP_PASSWORD")
        values_file_parser["config"]["countryCode"] = self.settings.get("CN_COUNTRY_CODE")
        values_file_parser["config"]["state"] = self.settings.get("CN_STATE")
        values_file_parser["config"]["city"] = self.settings.get("CN_CITY")
        values_file_parser["config"]["configmap"]["cnCacheType"] = self.settings.get("CN_CACHE_TYPE")
        values_file_parser["opendj"]["replicas"] = self.settings.get("LDAP_REPLICAS")
        values_file_parser["opendj"]["persistence"]["size"] = self.settings.get("LDAP_STORAGE_SIZE")
        if self.settings.get("ENABLE_OXTRUST_API_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["cnOxtrustApiEnabled"] = True
        if self.settings.get("ENABLE_OXTRUST_TEST_MODE_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["cnOxtrustApiTestMode"] = True
        if self.settings.get("ENABLE_CASA_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["cnCasaEnabled"] = True
            values_file_parser["config"]["configmap"]["cnSyncCasaManifests"] = True

        if self.settings.get("ENABLE_OXPASSPORT_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["cnPassportEnabled"] = True
        if self.settings.get("ENABLE_RADIUS_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["cnRadiusEnabled"] = True
        if self.settings.get("ENABLE_SAML_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["cnSamlEnabled"] = True

        values_file_parser["oxpassport"]["resources"] = {}
        values_file_parser["casa"]["image"]["repository"] = self.settings.get("CASA_IMAGE_NAME")
        values_file_parser["casa"]["image"]["tag"] = self.settings.get("CASA_IMAGE_TAG")
        values_file_parser["casa"]["replicas"] = self.settings.get("CASA_REPLICAS")
        values_file_parser["config"]["image"]["repository"] = self.settings.get("CONFIG_IMAGE_NAME")
        values_file_parser["config"]["image"]["tag"] = self.settings.get("CONFIG_IMAGE_TAG")
        values_file_parser["cr-rotate"]["image"]["repository"] = self.settings.get("CACHE_REFRESH_ROTATE_IMAGE_NAME")
        values_file_parser["cr-rotate"]["image"]["tag"] = self.settings.get("CACHE_REFRESH_ROTATE_IMAGE_TAG")
        values_file_parser["auth-server-key-rotation"]["image"]["repository"] = self.settings.get(
            "CERT_MANAGER_IMAGE_NAME")
        values_file_parser["auth-server-key-rotation"]["image"]["tag"] = self.settings.get("CERT_MANAGER_IMAGE_TAG")
        values_file_parser["opendj"]["image"]["repository"] = self.settings.get("LDAP_IMAGE_NAME")
        values_file_parser["opendj"]["image"]["tag"] = self.settings.get("LDAP_IMAGE_TAG")
        values_file_parser["persistence"]["image"]["repository"] = self.settings.get("PERSISTENCE_IMAGE_NAME")
        values_file_parser["persistence"]["image"]["tag"] = self.settings.get("PERSISTENCE_IMAGE_TAG")
        values_file_parser["auth-server"]["image"]["repository"] = self.settings.get("AUTH_SERVER_IMAGE_NAME")
        values_file_parser["auth-server"]["image"]["tag"] = self.settings.get("AUTH_SERVER_IMAGE_TAG")
        values_file_parser["client-api"]["image"]["repository"] = self.settings.get("CLIENT_API_IMAGE_NAME")
        values_file_parser["client-api"]["image"]["tag"] = self.settings.get("CLIENT_API_IMAGE_TAG")
        values_file_parser["auth-server"]["replicas"] = self.settings.get("AUTH_SERVER_REPLICAS")
        values_file_parser["oxpassport"]["image"]["repository"] = self.settings.get("OXPASSPORT_IMAGE_NAME")
        values_file_parser["oxpassport"]["image"]["tag"] = self.settings.get("OXPASSPORT_IMAGE_TAG")
        values_file_parser["oxpassport"]["replicas"] = self.settings.get("OXPASSPORT_REPLICAS")
        values_file_parser["oxshibboleth"]["image"]["repository"] = self.settings.get("OXSHIBBOLETH_IMAGE_NAME")
        values_file_parser["oxshibboleth"]["image"]["tag"] = self.settings.get("OXSHIBBOLETH_IMAGE_TAG")
        values_file_parser["oxshibboleth"]["replicas"] = self.settings.get("OXSHIBBOLETH_REPLICAS")
        values_file_parser["jackrabbit"]["image"]["repository"] = self.settings.get("JACKRABBIT_IMAGE_NAME")
        values_file_parser["jackrabbit"]["image"]["tag"] = self.settings.get("JACKRABBIT_IMAGE_TAG")
        values_file_parser["radius"]["image"]["repository"] = self.settings.get("RADIUS_IMAGE_NAME")
        values_file_parser["radius"]["image"]["tag"] = self.settings.get("RADIUS_IMAGE_TAG")
        values_file_parser["radius"]["replicas"] = self.settings.get("RADIUS_REPLICAS")
        values_file_parser.dump_it()

    def install_gluu(self, install_ingress=True):
        """
        Helm install Gluu
        :param install_ingress:
        """
        labels = {"app": "gluu"}
        if self.settings.get("CN_USE_ISTIO") == "Y":
            labels = {"app": "gluu", "istio-injection": "enabled"}
        self.kubernetes.create_namespace(name=self.settings.get("CN_NAMESPACE"), labels=labels)
        if self.settings.get("CN_PERSISTENCE_BACKEND") != "ldap" and self.settings.get("CN_INSTALL_COUCHBASE") == "Y":
            couchbase_app = Couchbase()
            couchbase_app.uninstall()
            couchbase_app = Couchbase()
            couchbase_app.install()
            self.settings = ValuesHandler()
        if self.settings.get("CN_AWS_LB_TYPE") == "alb":
            self.prepare_alb()
            self.deploy_alb()
        if self.settings.get("CN_AWS_LB_TYPE") != "alb" and self.settings.get("CN_USE_ISTIO_INGRESS") != "Y":
            self.check_install_nginx_ingress(install_ingress)
        self.analyze_global_values()
        try:
            exec_cmd("helm install {} -f {} ./helm/gluu --namespace={}".format(
                self.settings.get('CN_HELM_RELEASE_NAME'), self.values_file, self.settings.get("CN_NAMESPACE")))

            if self.settings.get("CN_PERSISTENCE_BACKEND") == "hybrid" or \
                    self.settings.get("CN_PERSISTENCE_BACKEND") == "ldap":
                self.install_ldap_backup()

        except FileNotFoundError:
            logger.error("Helm v3 is not installed. Please install it to continue "
                         "https://helm.sh/docs/intro/install/")
            raise SystemExit(1)

    def install_ldap_backup(self):
        values_file = Path("./helm/ldap-backup/values.yaml").resolve()
        values_file_parser = Parser(values_file, True)
        values_file_parser["ldapPass"] = self.settings.get("LDAP_PW")
        if self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            values_file_parser["gluuLdapSchedule"] = self.settings.get("LDAP_BACKUP_SCHEDULE")
        if self.settings.get("CM_LDAP_MULTI_CLUSTER") == "Y":
            values_file_parser["multiCluster"]["enabled"] = True
            values_file_parser["multiCluster"]["ldapAdvertiseAdminPort"] = \
                self.settings.get("CN_LDAP_ADVERTISE_ADMIN_PORT")
            values_file_parser["multiCluster"]["ldapAdvertiseAdminPort"] = \
                self.settings.get("CN_LDAP_ADVERTISE_ADMIN_PORT")
            values_file_parser["multiCluster"]["serfAdvertiseAddr"] = \
                self.settings.get("CN_LDAP_ADVERTISE_ADDRESS")[:-6]
        values_file_parser["ldapPass"] = self.settings.get("CN_LDAP_PASSWORD")
        values_file_parser.dump_it()
        exec_cmd("helm install {} -f ./helm/ldap-backup/values.yaml ./helm/ldap-backup --namespace={}".format(
            self.ldap_backup_release_name, self.settings.get("CN_NAMESPACE")))

    def upgrade_gluu(self):
        values_file_parser = Parser(self.upgrade_values_file, True)
        values_file_parser["domain"] = self.settings.get("CN_FQDN")
        values_file_parser["cnCacheType"] = self.settings.get("CN_CACHE_TYPE")
        values_file_parser["cnCouchbaseUrl"] = self.settings.get("CN_COUCHBASE_URL")
        values_file_parser["cnCouchbaseUser"] = self.settings.get("CN_COUCHBASE_USER")
        values_file_parser["cnCouchbaseSuperUser"] = self.settings.get("CN_COUCHBASE_SUPERUSER")
        values_file_parser["cnPersistenceLdapMapping"] = self.settings.get("CN_HYBRID_LDAP_HELD_DATA")
        values_file_parser["cnPersistenceType"] = self.settings.get("CN_PERSISTENCE_BACKEND")
        values_file_parser["source"] = self.settings.get("CN_VERSION")
        values_file_parser["target"] = self.settings.get("CN_UPGRADE_TARGET_VERSION")
        values_file_parser.dump_it()
        exec_cmd("helm install {} -f {} ./helm/gluu-upgrade --namespace={}".format(
            self.settings.get('CN_HELM_RELEASE_NAME'), self.values_file, self.settings.get("CN_NAMESPACE")))

    def uninstall_gluu(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings.get('CN_HELM_RELEASE_NAME'),
                                                        self.settings.get("CN_NAMESPACE")))
        exec_cmd("helm delete {} --namespace={}".format(self.ldap_backup_release_name,
                                                        self.settings.get("CN_NAMESPACE")))

    def uninstall_nginx_ingress(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings.get('CN_NGINX_INGRESS_RELEASE_NAME'),
                                                        self.settings.get("CN_NGINX_INGRESS_NAMESPACE")))
