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
from pygluu.kubernetes.settings import SettingsHandler
import time
import socket
import base64
import secrets

logger = get_logger("gluu-helm          ")


class Helm(object):
    def __init__(self):
        self.values_file = Path("./helm/gluu/values.yaml").resolve()
        self.settings = SettingsHandler()
        self.kubernetes = Kubernetes()
        self.ldap_backup_release_name = self.settings.get('GLUU_HELM_RELEASE_NAME') + "-ldap-backup"
        if self.settings.get("DEPLOYMENT_ARCH") == "gke":
            # Clusterrolebinding needs to be created for gke with CB
            if self.settings.get("INSTALL_REDIS") == "Y" or \
                    self.settings.get("INSTALL_COUCHBASE") == "Y":
                user_account, stderr, retcode = exec_cmd("gcloud config get-value core/account")
                user_account = str(user_account, "utf-8").strip()

                user, stderr, retcode = exec_cmd("whoami")
                user = str(user, "utf-8").strip()
                cluster_role_binding_name = "cluster-admin-{}".format(user)
                self.kubernetes.create_cluster_role_binding(cluster_role_binding_name=cluster_role_binding_name,
                                                            user_name=user_account,
                                                            cluster_role_name="cluster-admin")

    def redeploy_gluu_to_load_alb(self):
        prompt = input("Please input the DNS of the Application load balancer found on AWS UI Loadbalancer page: ")
        lb_hostname = prompt
        self.settings.set("LB_ADD", lb_hostname)
        self.analyze_global_values()
        exec_cmd("helm upgrade {} -f {} ./helm/gluu --timeout 10m0s --namespace={}".format(
            self.settings.get('GLUU_HELM_RELEASE_NAME'), self.values_file, self.settings.get("GLUU_NAMESPACE")))

    def wait_for_nginx_add(self):
        hostname_ip = None
        while True:
            try:
                if hostname_ip:
                    break
                if self.settings.get("DEPLOYMENT_ARCH") == "eks":
                    hostname_ip = self.kubernetes.read_namespaced_service(
                        name=self.settings.get('NGINX_INGRESS_RELEASE_NAME') + "-ingress-nginx-controller",
                        namespace=self.settings.get("NGINX_INGRESS_NAMESPACE")).status.load_balancer.ingress[0].hostname
                    self.settings.set("LB_ADD", hostname_ip)
                    if self.settings.get("AWS_LB_TYPE") == "nlb":
                        try:
                            ip_static = socket.gethostbyname(str(hostname_ip))
                            if ip_static:
                                break
                        except socket.gaierror:
                            logger.info("Address has not recieved an ip yet.")
                elif self.settings.get("DEPLOYMENT_ARCH") == "local":
                    self.settings.set("LB_ADD", self.settings.get('NGINX_INGRESS_RELEASE_NAME') +
                                      "-nginx-ingress-controller." + self.settings.get("NGINX_INGRESS_NAMESPACE") +
                                      ".svc.cluster.local")
                    break
                else:
                    hostname_ip = self.kubernetes.read_namespaced_service(
                        name=self.settings.get('NGINX_INGRESS_RELEASE_NAME') + "-ingress-nginx-controller",
                        namespace=self.settings.get("NGINX_INGRESS_NAMESPACE")).status.load_balancer.ingress[0].ip
                    self.settings.set("HOST_EXT_IP", hostname_ip)
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
            self.kubernetes.create_namespace(name=self.settings.get("NGINX_INGRESS_NAMESPACE"),
                                             labels={"app": "ingress-nginx"})
            self.kubernetes.delete_cluster_role(
                self.settings.get('NGINX_INGRESS_RELEASE_NAME') + "-nginx-ingress-controller")
            self.kubernetes.delete_cluster_role_binding(
                self.settings.get('NGINX_INGRESS_RELEASE_NAME') + "-nginx-ingress-controller")
            try:
                exec_cmd("helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx")
                exec_cmd("helm repo add stable https://charts.helm.sh/stable")
                exec_cmd("helm repo update")
            except FileNotFoundError:
                logger.error("Helm v3 is not installed. Please install it to continue "
                             "https://helm.sh/docs/intro/install/")
                raise SystemExit(1)
        command = "helm install {} ingress-nginx/ingress-nginx --namespace={} ".format(
            self.settings.get('NGINX_INGRESS_RELEASE_NAME'), self.settings.get("NGINX_INGRESS_NAMESPACE"))
        if self.settings.get("DEPLOYMENT_ARCH") == "minikube":
            exec_cmd("minikube addons enable ingress")
        if self.settings.get("DEPLOYMENT_ARCH") == "eks":
            if self.settings.get("AWS_LB_TYPE") == "nlb":
                if install_ingress:
                    nlb_override_values_file = Path("./nginx/aws/aws-nlb-override-values.yaml").resolve()
                    nlb_values = " --values {}".format(nlb_override_values_file)
                    exec_cmd(command + nlb_values)
            else:
                if self.settings.get("USE_ARN") == "Y":
                    if install_ingress:
                        elb_override_values_file = Path("./nginx/aws/aws-elb-override-values.yaml").resolve()
                        elb_file_parser = Parser(elb_override_values_file, True)
                        elb_file_parser["controller"]["service"]["annotations"].update(
                            {"service.beta.kubernetes.io/aws-load-balancer-ssl-cert": self.settings.get("ARN_AWS_IAM")})
                        elb_file_parser["controller"]["config"]["proxy-real-ip-cidr"] = self.settings.get("VPC_CIDR")
                        elb_file_parser.dump_it()
                        elb_values = " --values {}".format(elb_override_values_file)
                        exec_cmd(command + elb_values)
                else:
                    if install_ingress:
                        exec_cmd(command)

        if self.settings.get("DEPLOYMENT_ARCH") in ("gke", "aks", "do"):
            if install_ingress:
                cloud_override_values_file = Path("./nginx/cloud/cloud-override-values.yaml").resolve()
                cloud_values = " --values {}".format(cloud_override_values_file)
                exec_cmd(command + cloud_values)
        if self.settings.get("DEPLOYMENT_ARCH") == "local":
            if install_ingress:
                baremetal_override_values_file = Path("./nginx/baremetal/baremetal-override-values.yaml").resolve()
                baremetal_values = " --values {}".format(baremetal_override_values_file)
                exec_cmd(command + baremetal_values)
        if self.settings.get("DEPLOYMENT_ARCH") not in ("microk8s", "minikube"):
            logger.info("Waiting for nginx-ingress to be prepared...")
            time.sleep(60)
            self.wait_for_nginx_add()

    def analyze_global_values(self):
        """
        Parses Gluu values.yaml with the input information from prompts
        """
        values_file_parser = Parser(self.values_file, True)
        if self.settings.get("DEPLOYMENT_ARCH") == "minikube":
            provisioner = "k8s.io/minikube-hostpath"
        elif self.settings.get("DEPLOYMENT_ARCH") == "eks":
            provisioner = "kubernetes.io/aws-ebs"
        elif self.settings.get("DEPLOYMENT_ARCH") == "gke":
            provisioner = "kubernetes.io/gce-pd"
        elif self.settings.get("DEPLOYMENT_ARCH") == "aks":
            provisioner = "kubernetes.io/azure-disk"
        elif self.settings.get("DEPLOYMENT_ARCH") == "do":
            provisioner = "dobs.csi.digitalocean.com"
        elif self.settings.get("DEPLOYMENT_ARCH") == "local":
            provisioner = "openebs.io/local"
        else:
            provisioner = "microk8s.io/hostpath"
        if self.settings.get("AWS_LB_TYPE") == "alb":
            values_file_parser["global"]["alb"]["ingress"]["additionalAnnotations"]["alb.ingress.kubernetes.io/certificate-arn"] = \
                self.settings.get("ARN_AWS_IAM")
            if not self.settings.get("ARN_AWS_IAM"):
                del values_file_parser["global"]["alb"]["ingress"]["additionalAnnotations"]["alb.ingress.kubernetes.io/certificate-arn"]
        values_file_parser["global"]["storageClass"]["provisioner"] = provisioner
        values_file_parser["global"]["lbIp"] = self.settings.get("HOST_EXT_IP")
        values_file_parser["global"]["domain"] = self.settings.get("GLUU_FQDN")
        values_file_parser["global"]["isDomainRegistered"] = "false"
        if self.settings.get("IS_GLUU_FQDN_REGISTERED") == "Y":
            values_file_parser["global"]["isDomainRegistered"] = "true"
        if self.settings.get("GLUU_CACHE_TYPE") == "REDIS":
            values_file_parser["config"]["configmap"]["gluuRedisUrl"] = self.settings.get("REDIS_URL")
            values_file_parser["config"]["configmap"]["gluuRedisType"] = self.settings.get("REDIS_TYPE")
            values_file_parser["config"]["configmap"]["gluuRedisUseSsl"] = self.settings.get("REDIS_USE_SSL")
            values_file_parser["config"]["configmap"]["gluuRedisSslTruststore"] = \
                self.settings.get("REDIS_SSL_TRUSTSTORE")
            values_file_parser["config"]["configmap"]["gluuRedisSentinelGroup"] = \
                self.settings.get("REDIS_SENTINEL_GROUP")
            values_file_parser["config"]["redisPass"] = self.settings.get("REDIS_PW")
        if self.settings.get("DEPLOYMENT_ARCH") in ("microk8s", "minikube") \
                or self.settings.get("TEST_ENVIRONMENT") == "Y":
            values_file_parser["global"]["cloud"]["testEnviroment"] = True
        if self.settings.get("DEPLOYMENT_ARCH") == "microk8s":
            values_file_parser["nginx-ingress"]["ingress"]["ingressClassName"] = "public"
        values_file_parser["config"]["configmap"]["lbAddr"] = self.settings.get("LB_ADD")
        values_file_parser["global"]["gluuPersistenceType"] = self.settings.get("PERSISTENCE_BACKEND")
        values_file_parser["config"]["configmap"]["gluuPersistenceType"] = self.settings.get("PERSISTENCE_BACKEND")
        values_file_parser["config"]["configmap"]["gluuPersistenceLdapMapping"] = \
            self.settings.get("HYBRID_LDAP_HELD_DATA")
        if self.settings.get("PERSISTENCE_BACKEND") in ("couchbase", "hybrid"):
            values_file_parser["config"]["configmap"]["gluuCouchbaseUrl"] = self.settings.get("COUCHBASE_URL")
            values_file_parser["config"]["configmap"]["gluuCouchbaseUser"] = self.settings.get("COUCHBASE_USER")
            values_file_parser["config"]["configmap"]["gluuCouchbaseBucketPrefix"] = self.settings.get(
                "COUCHBASE_BUCKET_PREFIX")
            values_file_parser["config"]["configmap"]["gluuCouchbaseIndexNumReplica"] = self.settings.get(
                "COUCHBASE_INDEX_NUM_REPLICA")
            values_file_parser["config"]["configmap"]["gluuCouchbaseSuperUser"] = \
                self.settings.get("COUCHBASE_SUPERUSER")
            values_file_parser["config"]["configmap"]["gluuCouchbaseCrt"] = self.settings.get("COUCHBASE_CRT")
            values_file_parser["config"]["configmap"]["gluuCouchbasePass"] = self.settings.get("COUCHBASE_PASSWORD")
            values_file_parser["config"]["configmap"]["gluuCouchbaseSuperUserPass"] = \
                self.settings.get("COUCHBASE_SUPERUSER_PASSWORD")

        if self.settings.get("PERSISTENCE_BACKEND") == "sql":
            values_file_parser["config"]["configmap"]["cnSqlDbDialect"] = \
                self.settings.get("GLUU_SQL_DB_DIALECT")
            values_file_parser["config"]["configmap"]["cnSqlDbPort"] = \
                self.settings.get("GLUU_SQL_DB_PORT")
            values_file_parser["config"]["configmap"]["cnSqlDbHost"] = \
                self.settings.get("GLUU_SQL_DB_HOST")
            values_file_parser["config"]["configmap"]["cnSqlDbName"] = \
                self.settings.get("GLUU_SQL_DB_NAME")
            values_file_parser["config"]["configmap"]["cnSqlDbUser"] = \
                self.settings.get("GLUU_SQL_DB_USER")
            values_file_parser["config"]["configmap"]["cnSqldbUserPassword"] = \
                self.settings.get("GLUU_SQL_DB_PASSWORD")

        if self.settings.get("PERSISTENCE_BACKEND") == "spanner":
            values_file_parser["config"]["configmap"]["cnGoogleSpannerEmulatorHost"] = \
                self.settings.get("SPANNER_EMULATOR_HOST")
            values_file_parser["config"]["configmap"]["cnGoogleSpannerInstanceId"] = \
                self.settings.get("GOOGLE_SPANNER_INSTANCE_ID")
            values_file_parser["config"]["configmap"]["cnGoogleSpannerDatabaseId"] = \
                self.settings.get("GOOGLE_SPANNER_DATABASE_ID")
            values_file_parser["config"]["configmap"]["cnGoogleProjectId"] = \
                self.settings.get("GOOGLE_PROJECT_ID")

        if self.settings.get("PERSISTENCE_BACKEND") == "spanner" or \
                self.settings.get("USE_GOOGLE_SECRET_MANAGER") == "Y":
            values_file_parser["config"]["configmap"]["cnGoogleServiceAccount"] = \
                self.settings.get("GOOGLE_SERVICE_ACCOUNT_BASE64")
        values_file_parser["global"]["oxauth"]["enabled"] = True
        values_file_parser["global"]["persistence"]["enabled"] = True
        values_file_parser["global"]["oxtrust"]["enabled"] = True
        values_file_parser["global"]["config"]["enabled"] = True
        values_file_parser["global"]["opendj"]["enabled"] = False
        values_file_parser["global"]["fido2"]["enabled"] = False
        if self.settings.get("ENABLE_FIDO2") == "Y":
            values_file_parser["global"]["fido2"]["enabled"] = True
            values_file_parser["fido2"]["replicas"] = self.settings.get("FIDO2_REPLICAS")
            values_file_parser["nginx-ingress"]["ingress"]["fido2ConfigEnabled"] = True
            values_file_parser["nginx-ingress"]["ingress"]["fido2Enabled"] = True
            values_file_parser["global"]["alb"]["ingress"]["fido2ConfigEnabled"] = True
            values_file_parser["global"]["alb"]["ingress"]["fido2Enabled"] = True
        # Remove legacy setting after moving to next version
        if self.settings.get("NGINX_LEGACY") == "Y":
            values_file_parser["nginx-ingress"]["ingress"]["legacy"] = True
        values_file_parser["global"]["scim"]["enabled"] = False
        if self.settings.get("ENABLE_SCIM") == "Y":
            values_file_parser["global"]["scim"]["enabled"] = True
            values_file_parser["config"]["configmap"]["gluuScimProtectionMode"] = \
                self.settings.get("GLUU_SCIM_PROTECTION_MODE")
            values_file_parser["scim"]["replicas"] = self.settings.get("SCIM_REPLICAS")
            values_file_parser["nginx-ingress"]["ingress"]["scimConfigEnabled"] = True
            values_file_parser["nginx-ingress"]["ingress"]["scimEnabled"] = True
            values_file_parser["global"]["alb"]["ingress"]["scimConfigEnabled"] = True
            values_file_parser["global"]["alb"]["ingress"]["scimEnabled"] = True
        if self.settings.get("INSTALL_JACKRABBIT") == "Y":
            values_file_parser["global"]["jackrabbit"]["enabled"] = True
            values_file_parser["config"]["configmap"]["gluuJackrabbitUrl"] = self.settings.get("JACKRABBIT_URL")
            values_file_parser["jackrabbit"]["secrets"]["gluuJackrabbitAdminPass"] = \
                self.settings.get("JACKRABBIT_ADMIN_PASSWORD")
            values_file_parser["jackrabbit"]["secrets"]["gluuJackrabbitPostgresPass"] = \
                self.settings.get("JACKRABBIT_PG_PASSWORD")
        if self.settings.get("USE_ISTIO_INGRESS") == "Y":
            values_file_parser["nginx-ingress"]["ingress"]["enabled"] = False
            values_file_parser["global"]["istio"]["ingress"] = True
            values_file_parser["global"]["istio"]["enabled"] = True
            values_file_parser["global"]["istio"]["namespace"] = self.settings.get("ISTIO_SYSTEM_NAMESPACE")
        elif self.settings.get("AWS_LB_TYPE") == "alb":
            values_file_parser["nginx-ingress"]["ingress"]["enabled"] = False
            values_file_parser["global"]["alb"]["ingress"]["enabled"] = True
        else:
            values_file_parser["nginx-ingress"]["ingress"]["enabled"] = True
            values_file_parser["nginx-ingress"]["ingress"]["hosts"] = [self.settings.get("GLUU_FQDN")]
            values_file_parser["nginx-ingress"]["ingress"]["tls"][0]["hosts"] = [self.settings.get("GLUU_FQDN")]
        if self.settings.get("USE_ISTIO") == "Y":
            values_file_parser["global"]["istio"]["enabled"] = True
        if self.settings.get("ENABLE_OXTRUST_API_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["gluuOxtrustApiEnabled"] = True
        if self.settings.get("ENABLE_OXTRUST_TEST_MODE_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["gluuOxtrustApiTestMode"] = True
        values_file_parser["global"]["gluuJackrabbitCluster"] = "false"
        values_file_parser["jackrabbit"]["clusterId"] = "first"
        if self.settings.get("JACKRABBIT_CLUSTER") == "Y":
            values_file_parser["jackrabbit"]["clusterId"] = ""
            values_file_parser["global"]["gluuJackrabbitCluster"] = "true"
            values_file_parser["config"]["configmap"]["gluuJackrabbitAdminId"] = \
                self.settings.get("JACKRABBIT_ADMIN_ID")
            values_file_parser["config"]["configmap"]["gluuJackrabbitPostgresUser"] = \
                self.settings.get("JACKRABBIT_PG_USER")
            values_file_parser["config"]["configmap"]["gluuJackrabbitPostgresDatabaseName"] = \
                self.settings.get("JACKRABBIT_DATABASE")
            values_file_parser["config"]["configmap"]["gluuJackrabbitPostgresHost"] = \
                self.settings.get("POSTGRES_URL")
            values_file_parser["config"]["configmap"]["gluuJackrabbitPostgresUser"] = \
                self.settings.get("JACKRABBIT_PG_USER")

        if self.settings.get("PERSISTENCE_BACKEND") == "hybrid" or \
                self.settings.get("PERSISTENCE_BACKEND") == "ldap":
            values_file_parser["global"]["opendj"]["enabled"] = True
            # ALPHA-FEATURE: Multi cluster ldap replication
            if self.settings.get("GLUU_LDAP_MULTI_CLUSTER") == "Y":
                values_file_parser["opendj"]["multiCluster"]["enabled"] = True
                values_file_parser["opendj"]["multiCluster"]["serfAdvertiseAddrSuffix"] = \
                    self.settings.get("GLUU_LDAP_ADVERTISE_ADDRESS_SUFFIX")
                serf_key = base64.b64encode(secrets.token_bytes()).decode()
                values_file_parser["opendj"]["multiCluster"]["serfKey"] = serf_key
                values_file_parser["opendj"]["multiCluster"]["serfPeers"] = \
                    self.settings.get("GLUU_LDAP_SERF_PEERS")
                if self.settings.get("GLUU_LDAP_SECONDARY_CLUSTER") == "Y":
                    values_file_parser["global"]["persistence"]["enabled"] = False
                values_file_parser["opendj"]["multiCluster"]["replicaCount"] = \
                    self.settings.get("GLUU_LDAP_MULTI_CLUSTER_REPLICAS")
                values_file_parser["opendj"]["multiCluster"]["clusterId"] = \
                    self.settings.get("GLUU_LDAP_MULTI_CLUSTER_CLUSTER_ID")
        values_file_parser["global"]["oxshibboleth"]["enabled"] = False
        if self.settings.get("ENABLE_OXSHIBBOLETH") == "Y":
            values_file_parser["global"]["oxshibboleth"]["enabled"] = True
            values_file_parser["config"]["configmap"]["gluuSyncShibManifests"] = True

        values_file_parser["global"]["oxd-server"]["enabled"] = False
        if self.settings.get("ENABLE_OXD") == "Y":
            values_file_parser["global"]["oxd-server"]["enabled"] = True
            values_file_parser["config"]["configmap"]["gluuOxdApplicationCertCn"] = \
                self.settings.get("OXD_APPLICATION_KEYSTORE_CN")
            values_file_parser["config"]["configmap"]["gluuOxdAdminCertCn"] = self.settings.get("OXD_ADMIN_KEYSTORE_CN")
            values_file_parser["oxd-server"]["replicas"] = self.settings.get("OXD_SERVER_REPLICAS")

        values_file_parser["opendj"]["gluuRedisEnabled"] = False
        if self.settings.get("GLUU_CACHE_TYPE") == "REDIS":
            values_file_parser["opendj"]["gluuRedisEnabled"] = True

        values_file_parser["global"]["nginx-ingress"]["enabled"] = True

        values_file_parser["global"]["cr-rotate"]["enabled"] = False
        if self.settings.get("ENABLE_CACHE_REFRESH") == "Y":
            values_file_parser["global"]["cr-rotate"]["enabled"] = True

        values_file_parser["global"]["oxauth-key-rotation"]["enabled"] = False
        if self.settings.get("ENABLE_OXAUTH_KEY_ROTATE") == "Y":
            values_file_parser["global"]["oxauth-key-rotation"]["enabled"] = True
            values_file_parser["oxauth-key-rotation"]["keysLife"] = self.settings.get("OXAUTH_KEYS_LIFE")

        values_file_parser["config"]["orgName"] = self.settings.get("ORG_NAME")
        values_file_parser["config"]["email"] = self.settings.get("EMAIL")
        values_file_parser["config"]["adminPass"] = self.settings.get("ADMIN_PW")
        values_file_parser["config"]["ldapPass"] = self.settings.get("LDAP_PW")
        values_file_parser["config"]["countryCode"] = self.settings.get("COUNTRY_CODE")
        values_file_parser["config"]["state"] = self.settings.get("STATE")
        values_file_parser["config"]["city"] = self.settings.get("CITY")
        values_file_parser["config"]["configmap"]["gluuCacheType"] = self.settings.get("GLUU_CACHE_TYPE")
        values_file_parser["opendj"]["replicas"] = self.settings.get("LDAP_REPLICAS")
        values_file_parser["opendj"]["persistence"]["size"] = self.settings.get("LDAP_STORAGE_SIZE")
        if self.settings.get("ENABLE_OXTRUST_API_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["gluuOxtrustApiEnabled"] = True
        if self.settings.get("ENABLE_OXTRUST_TEST_MODE_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["gluuOxtrustApiTestMode"] = True
        if self.settings.get("ENABLE_CASA_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["gluuCasaEnabled"] = True
            values_file_parser["config"]["configmap"]["gluuSyncCasaManifests"] = True
            values_file_parser["nginx-ingress"]["ingress"]["casaEnabled"] = True
            values_file_parser["global"]["alb"]["ingress"]["casaEnabled"] = True

        if self.settings.get("ENABLE_OXPASSPORT_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["gluuPassportEnabled"] = True
            values_file_parser["nginx-ingress"]["ingress"]["passportEnabled"] = True
            values_file_parser["global"]["alb"]["ingress"]["passportEnabled"] = True
        if self.settings.get("ENABLE_SAML_BOOLEAN") == "true":
            values_file_parser["config"]["configmap"]["gluuSamlEnabled"] = True
            values_file_parser["nginx-ingress"]["ingress"]["shibEnabled"] = True
            values_file_parser["global"]["alb"]["ingress"]["shibEnabled"] = True

        if self.settings.get("MIGRATION_ENABLED") == "Y":
            values_file_parser["global"]["persistence"]["enabled"] = False
            values_file_parser["config"]["migration"]["migrationDir"] = self.settings.get("MIGRATION_DIR")
            values_file_parser["config"]["migration"]["migrationDataFormat"] = \
                self.settings.get("MIGRATION_DATA_FORMAT")
        values_file_parser["casa"]["image"]["repository"] = self.settings.get("CASA_IMAGE_NAME")
        values_file_parser["casa"]["image"]["tag"] = self.settings.get("CASA_IMAGE_TAG")
        values_file_parser["casa"]["replicas"] = self.settings.get("CASA_REPLICAS")
        values_file_parser["fido2"]["image"]["repository"] = self.settings.get("FIDO2_IMAGE_NAME")
        values_file_parser["fido2"]["image"]["tag"] = self.settings.get("FIDO2_IMAGE_TAG")
        values_file_parser["fido2"]["replicas"] = self.settings.get("FIDO2_REPLICAS")
        values_file_parser["scim"]["image"]["repository"] = self.settings.get("SCIM_IMAGE_NAME")
        values_file_parser["scim"]["image"]["tag"] = self.settings.get("SCIM_IMAGE_TAG")
        values_file_parser["scim"]["replicas"] = self.settings.get("SCIM_REPLICAS")
        values_file_parser["config"]["image"]["repository"] = self.settings.get("CONFIG_IMAGE_NAME")
        values_file_parser["config"]["image"]["tag"] = self.settings.get("CONFIG_IMAGE_TAG")
        values_file_parser["cr-rotate"]["image"]["repository"] = self.settings.get("CACHE_REFRESH_ROTATE_IMAGE_NAME")
        values_file_parser["cr-rotate"]["image"]["tag"] = self.settings.get("CACHE_REFRESH_ROTATE_IMAGE_TAG")
        values_file_parser["oxauth-key-rotation"]["image"]["repository"] = self.settings.get("CERT_MANAGER_IMAGE_NAME")
        values_file_parser["oxauth-key-rotation"]["image"]["tag"] = self.settings.get("CERT_MANAGER_IMAGE_TAG")
        values_file_parser["opendj"]["image"]["repository"] = self.settings.get("LDAP_IMAGE_NAME")
        values_file_parser["opendj"]["image"]["tag"] = self.settings.get("LDAP_IMAGE_TAG")
        values_file_parser["persistence"]["image"]["repository"] = self.settings.get("PERSISTENCE_IMAGE_NAME")
        values_file_parser["persistence"]["image"]["tag"] = self.settings.get("PERSISTENCE_IMAGE_TAG")
        values_file_parser["oxauth"]["image"]["repository"] = self.settings.get("OXAUTH_IMAGE_NAME")
        values_file_parser["oxauth"]["image"]["tag"] = self.settings.get("OXAUTH_IMAGE_TAG")
        values_file_parser["oxauth"]["replicas"] = self.settings.get("OXAUTH_REPLICAS")
        values_file_parser["oxd-server"]["image"]["repository"] = self.settings.get("OXD_IMAGE_NAME")
        values_file_parser["oxd-server"]["image"]["tag"] = self.settings.get("OXD_IMAGE_TAG")
        values_file_parser["oxpassport"]["image"]["repository"] = self.settings.get("OXPASSPORT_IMAGE_NAME")
        values_file_parser["oxpassport"]["image"]["tag"] = self.settings.get("OXPASSPORT_IMAGE_TAG")
        values_file_parser["oxpassport"]["replicas"] = self.settings.get("OXPASSPORT_REPLICAS")
        values_file_parser["oxshibboleth"]["image"]["repository"] = self.settings.get("OXSHIBBOLETH_IMAGE_NAME")
        values_file_parser["oxshibboleth"]["image"]["tag"] = self.settings.get("OXSHIBBOLETH_IMAGE_TAG")
        values_file_parser["oxshibboleth"]["replicas"] = self.settings.get("OXSHIBBOLETH_REPLICAS")
        values_file_parser["jackrabbit"]["image"]["repository"] = self.settings.get("JACKRABBIT_IMAGE_NAME")
        values_file_parser["jackrabbit"]["image"]["tag"] = self.settings.get("JACKRABBIT_IMAGE_TAG")
        values_file_parser["oxtrust"]["image"]["repository"] = self.settings.get("OXTRUST_IMAGE_NAME")
        values_file_parser["oxtrust"]["image"]["tag"] = self.settings.get("OXTRUST_IMAGE_TAG")
        values_file_parser["oxtrust"]["replicas"] = self.settings.get("OXTRUST_REPLICAS")

        # append container registry credentials name
        ctr_registry_cred_name = self.settings.get("CONTAINER_REGISTRY_SECRET_NAME")
        if ctr_registry_cred_name:
            for comp in [
                "casa",
                "fido2",
                "scim",
                "config",
                "cr-rotate",
                "oxauth-key-rotation",
                "opendj",
                "persistence",
                "oxauth",
                "oxd-server",
                "oxpassport",
                "oxshibboleth",
                "jackrabbit",
                "oxtrust",
            ]:
                # collect all creds and remove name matches ctr_registry_cred_name
                # to avoid duplication
                creds = [
                    cred for cred in values_file_parser[comp]["image"]["pullSecrets"]
                    if cred["name"] != ctr_registry_cred_name
                ]
                creds.append({"name": ctr_registry_cred_name})

                # example of generated yaml
                #
                # oxauth:
                #   image:
                #     pullSecrets:
                #       - name: regcred
                values_file_parser[comp]["image"]["pullSecrets"] = creds

        # add custom salt
        values_file_parser["config"]["salt"] = self.settings.get("SALT") or ""

        # document store
        values_file_parser["config"]["configmap"]["gluuDocumentStoreType"] = self.settings.get("DOCUMENT_STORE_TYPE") or "DB"

        values_file_parser.dump_it()

    def install_gluu(self, install_ingress=True):
        """
        Helm install Gluu
        :param install_ingress:
        """
        labels = {"app": "gluu"}
        if self.settings.get("USE_ISTIO") == "Y":
            labels = {"app": "gluu", "istio-injection": "enabled"}
        self.kubernetes.create_namespace(name=self.settings.get("GLUU_NAMESPACE"), labels=labels)
        if self.settings.get("PERSISTENCE_BACKEND") != "ldap" and self.settings.get("INSTALL_COUCHBASE") == "Y":
            couchbase_app = Couchbase()
            couchbase_app.uninstall()
            couchbase_app = Couchbase()
            couchbase_app.install()
            self.settings = SettingsHandler()
        if self.settings.get("AWS_LB_TYPE") != "alb" and self.settings.get("USE_ISTIO_INGRESS") != "Y":
            self.check_install_nginx_ingress(install_ingress)
        if self.settings.get("IS_GLUU_FQDN_REGISTERED") != "Y" and self.settings.get("AWS_LB_TYPE") == "alb":
            self.settings.set("LB_ADD", "im.going.tochange")
        self.analyze_global_values()
        try:
            exec_cmd("helm install {} -f {} ./helm/gluu --timeout 10m0s --namespace={}".format(
                self.settings.get('GLUU_HELM_RELEASE_NAME'), self.values_file, self.settings.get("GLUU_NAMESPACE")))

        except FileNotFoundError:
            logger.error("Helm v3 is not installed. Please install it to continue "
                         "https://helm.sh/docs/intro/install/")
            raise SystemExit(1)
        if self.settings.get("IS_GLUU_FQDN_REGISTERED") != "Y" and self.settings.get("AWS_LB_TYPE") == "alb":
            time.sleep(10)
            self.redeploy_gluu_to_load_alb()

    def uninstall_gluu(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings.get('GLUU_HELM_RELEASE_NAME'),
                                                        self.settings.get("GLUU_NAMESPACE")))
        exec_cmd("helm delete {} --namespace={}".format(self.ldap_backup_release_name,
                                                        self.settings.get("GLUU_NAMESPACE")))

    def uninstall_nginx_ingress(self):
        exec_cmd("helm delete {} --namespace={}".format(self.settings.get('NGINX_INGRESS_RELEASE_NAME'),
                                                        self.settings.get("NGINX_INGRESS_NAMESPACE")))
