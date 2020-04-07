"""
 License terms and conditions:
 https://www.gluu.org/license/enterprise-edition/
"""

from kubernetes import client, config, utils
from kubernetes.stream import stream
from .yamlparser import Parser, get_logger
import sys
import time
from pathlib import Path
import subprocess
import shutil
import os

logger = get_logger("gluu-kubernetes-api")


# TODO: remove this function once fixed by kubernetes
def fix_kubernetes_client_11_0_0b2():
    shiv_dir = Path(os.path.expanduser("~/.shiv"))
    try:
        def get_immediate_subdirectories(a_dir=shiv_dir):
            return [name for name in os.listdir(a_dir)
                    if os.path.isdir(os.path.join(a_dir, name))]

        all_shiv_dirs = get_immediate_subdirectories()
        for directory in all_shiv_dirs:
            bug_file = Path(shiv_dir + "/" + directory +
                            "/site-packages/kubernetes/client/models/v1beta1_custom_resource_definition_status.py")

            with open(bug_file, 'r+') as fh:
                lines = fh.readlines()
                for line in lines:
                    if "if conditions is None:" in line:
                        fh.seek(0)
                        lines.insert(lines.index(line), '        conditions = 1\n')
                        fh.writelines(lines)
                        break

            with open(bug_file, "r+") as fh:
                lines = fh.readlines()
                fh.seek(0)
                for line in lines:
                    if "if conditions is None:" not in line and \
                            "Invalid value for `conditions`, must not be `None`" not in line:
                        fh.write(line)
                fh.truncate()

    except Exception:
        logger.warning("Installation might fail due to a bug inside the ~/.shiv/*/"
                       "site-packages/kubernetes/client/models/v1beta1_custom_resource_definition_status.py "
                       "to fix this please open that file and set conditions = 1 above line 101")


# TODO: remove this function once fixed by kubernetes
fix_kubernetes_client_11_0_0b2()


def subprocess_cmd(command):
    """Execute command"""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    return proc_stdout


def check_microk8s_kube_config_file():
    kube_config_file_location = Path(os.path.expanduser("~/.kube/config"))

    if not kube_config_file_location.exists():
        kube_dir = os.path.dirname(kube_config_file_location)

        if not os.path.exists(kube_dir):
            os.makedirs(kube_dir)

        try:
            shutil.copy(Path("/var/snap/microk8s/current/credentials/client.config"), kube_config_file_location)
        except FileNotFoundError:
            logger.error("No Kubernetes config file found at ~/.kube/config")


class Kubernetes(object):
    def __init__(self):
        check_microk8s_kube_config_file()
        config_loaded = False
        try:
            config.load_incluster_config()
            config_loaded = True
        except config.config_exception.ConfigException:
            logger.warning("Unable to load in-cluster configuration; trying to load from Kube config file")
            try:
                config.load_kube_config()
                config_loaded = True
            except (IOError, config.config_exception.ConfigException) as exc:
                logger.warning("Unable to load Kube config; reason={}".format(exc))

        if not config_loaded:
            logger.error("Unable to load in-cluster or Kube config")
            sys.exit(1)

        self.api_client = client.ApiClient()
        self.custom_def_cli = client.CustomObjectsApi()
        self.core_cli = client.CoreV1Api()
        self.apps_cli = client.AppsV1Api()
        self.jobs_cli = client.BatchV1Api()
        self.rbac_cli = client.RbacAuthorizationV1Api()
        self.network_cli = client.NetworkingV1beta1Api()
        self.extenstion_cli = client.ExtensionsV1beta1Api()
        self.crd_cli = client.ApiextensionsV1beta1Api()
        self.storage_cli = client.StorageV1Api()
        self.admission_cli = client.AdmissionregistrationV1beta1Api()
        self.delete_options = client.V1DeleteOptions()
        self.delete_options.grace_period_seconds = 2
        self.delete_options.propagation_policy = 'Foreground'
        self.core_cli.api_client.configuration.assert_hostname = False
        self.apps_cli.api_client.configuration.assert_hostname = False

    def check_error_and_response(self, starting_time, resp):
        end_time = time.time()
        running_time = end_time - starting_time
        if resp.status != 404 and resp.status:
            logger.info("Waiting for the kubernetes object to be fully terminated.")
            time.sleep(1)
            if running_time > 60:
                logger.exception(resp)
                return False
            return True
        else:
            # The kubernetes object has been removed or does not exist"
            return False

    def check_read_error_and_response(self, starting_time, resp):
        end_time = time.time()
        running_time = end_time - starting_time
        if resp.status == 404 and not resp.status:
            logger.info("Resource not found. Trying to read again...")
            time.sleep(1)
            if running_time > 40:
                logger.exception(resp)
                return False
            return True
        else:
            # The kubernetes object has been found"
            return False

    def delete_namespace(self, name):
        """Delete namespace with name"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_namespace(name)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info("namespace/{} has been removed or does not exist".format(name))

    def delete_validating_webhook_configuration(self, name):
        """Delete validating webhook configuration with name"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.admission_cli.delete_validating_webhook_configuration(name, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info("validatingwebhookconfiguration/{} has been removed or does not exist".format(name))

    def delete_mutating_webhook_configuration(self, name):
        """Delete mutating webhook configuration with name"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.admission_cli.delete_mutating_webhook_configuration(name, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info("mutatingwebhookconfiguration/{} has been removed or does not exist".format(name))

    def delete_service(self, name, namespace="default"):
        """Delete service with name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_namespaced_service(name=name, namespace=namespace, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info("service/{} from namespace/{} has been removed or does not exist".format(name, namespace))

    def delete_deployment_using_label(self, namespace="default", app_label=None):
        """Delete deployment using app label in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.apps_cli.delete_collection_namespaced_deployment(namespace=namespace,
                                                                             label_selector=app_label,
                                                                             v1_delete_options=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info(
            'deployment with label {} in namespace/{} has been removed or does not exist'.format(app_label, namespace))

    def delete_deployment_using_name(self, name, namespace="default"):
        """Delete deployment using name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.apps_cli.delete_namespaced_deployment(name, namespace, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('deployment/{} in namespace/{} has been removed or does not exist'.format(name, namespace))

    def delete_stateful_set(self, namespace="default", app_label=None):
        """Delete statefulset using app label in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.apps_cli.delete_collection_namespaced_stateful_set(namespace=namespace,
                                                                               label_selector=app_label,
                                                                               v1_delete_options=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info(
            'statefulset with label {} in namespace/{} has been removed or does not exist'.format(app_label, namespace))

    def delete_job(self, namespace="default", app_label=None):
        """Delete job using app label in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.jobs_cli.delete_collection_namespaced_job(namespace=namespace, label_selector=app_label,
                                                                      v1_delete_options=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('job with label {} in namespace/{} has been removed or does not exist'.format(app_label, namespace))

    def delete_secret(self, name, namespace="default"):
        """Delete secret using name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_namespaced_secret(name, namespace, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('secret/{} from namespace/{} has been removed or does not exist'.format(name, namespace))

    def delete_daemon_set(self, namespace="default", app_label=None):
        """Delete daemon set using app label in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.apps_cli.delete_collection_namespaced_daemon_set(namespace=namespace,
                                                                             label_selector=app_label,
                                                                             v1_delete_options=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info(
            'daemonset with label {} in namespace/{} has been removed or does not exist'.format(app_label, namespace))

    def delete_collection_namespaced_replication_controller(self, namespace="default", app_label=None):
        """Delete replication controller using app label in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_collection_namespaced_replication_controller(namespace=namespace,
                                                                                         label_selector=app_label,
                                                                                         v1_delete_options=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('replicationcontroller/{} from namespace/{} has been removed or does not exist'.format(app_label,
                                                                                                           namespace))

    def delete_config_map_using_label(self, namespace="default", app_label=None):
        """Delete config map using app label in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_collection_namespaced_config_map(namespace=namespace,
                                                                             label_selector=app_label,
                                                                             v1_delete_options=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('configmap/{} in namespace/{} has been removed or does not exist'.format(app_label, namespace))

    def delete_config_map_using_name(self, name, namespace="default"):
        """Delete config map using name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_namespaced_config_map(name, namespace, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('configmap/{} in namespace/{} has been removed or does not exist'.format(name, namespace))

    def delete_role(self, name, namespace="default"):
        """Delete role using name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.rbac_cli.delete_namespaced_role(name, namespace, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('role/{} in namespace/{} has been removed or does not exist'.format(name, namespace))

    def delete_role_binding(self, name, namespace="default"):
        """Delete role binding using name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.rbac_cli.delete_namespaced_role_binding(name, namespace, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('rolebinding/{} from namespace/{} has been removed or does not exist'.format(name, namespace))

    def delete_cluster_role(self, name):
        """Delete cluster role using name"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.rbac_cli.delete_cluster_role(name, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('role/{} has been removed or does not exist'.format(name))

    def delete_cluster_role_binding(self, name):
        """Delete cluster role binding using name"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.rbac_cli.delete_cluster_role_binding(name, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('clusterrolebinding/{} has been removed or does not exist'.format(name))

    def delete_persistent_volume(self, app_label=None):
        """Delete persistent volume using app label"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_collection_persistent_volume(label_selector=app_label,
                                                                         v1_delete_options=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('persistentvolume/{} has been removed or does not exist'.format(app_label))

    def delete_persistent_volume_claim(self, namespace="default", app_label=None):
        """Delete persistent volume claim using app label in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_collection_namespaced_persistent_volume_claim(namespace=namespace,
                                                                                          label_selector=app_label,
                                                                                          v1_delete_options=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)

        logger.info(
            'persistentvolumeclaim/{} in namespace/{} has been removed or does not exist'.format(app_label, namespace))

    def delete_service_account(self, name, namespace="default"):
        """Delete service account using name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.core_cli.delete_namespaced_service_account(name, namespace, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('serviceaccount/{} in namespace/{} has been removed or does not exist'.format(name, namespace))

    def delete_ingress(self, name, namespace="default"):
        """Delete ingress using name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.network_cli.delete_namespaced_ingress(name, namespace, body=self.delete_options)
            except client.rest.ApiException as e:
                try:
                    resp = self.extenstion_cli.delete_namespaced_ingress(name, namespace, body=self.delete_options)
                except client.rest.ApiException as e:
                    response = self.check_error_and_response(starting_time, e)
                else:
                    response = self.check_error_and_response(starting_time, resp)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('ingress/{} in namespace/{} has been removed or does not exist'.format(name, namespace))

    def delete_custom_resource(self, name):
        """Delete custom resource using name"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.crd_cli.delete_custom_resource_definition(name, body=self.delete_options)

            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('customeresource/{} has been removed or does not exist'.format(name))

    def delete_storage_class(self, name):
        """Delete storage class using name"""
        starting_time = time.time()
        response = True
        while response:
            try:
                resp = self.storage_cli.delete_storage_class(name, body=self.delete_options)
            except client.rest.ApiException as e:
                response = self.check_error_and_response(starting_time, e)
            else:
                response = self.check_error_and_response(starting_time, resp)
        logger.info('storageclass/{} has been removed or does not exist'.format(name))

    def create_namespace(self, name):
        """Create namespace using name"""
        body = client.V1Secret()
        metadata = client.V1ObjectMeta()
        metadata.name = name
        body.metadata = metadata
        try:
            self.core_cli.create_namespace(body=body, pretty="pretty")
            logger.info('Created namespace {}'.format(name))
            return True
        except client.rest.ApiException as e:
            logger.exception(e)
            return False

    def create_namespaced_service_account(self, name, namespace="default"):
        """Create service account using name in namespace"""
        body = client.V1ServiceAccount()
        metadata = client.V1ObjectMeta()
        metadata.name = name
        body.metadata = metadata

        try:
            self.core_cli.create_namespaced_service_account(namespace=namespace, body=body)
            logger.info('Created serviceaccount {} in namespace'.format(name, namespace))
            return
        except client.rest.ApiException as e:
            logger.exception(e)
            return False

    def create_namespaced_role_binding(self, role_binding_name, service_account_name, role_name, namespace="default"):
        """Create role binding using name=role_binding_name in namespace
        connecting role_name using service_account_name"""
        subject = client.V1Subject(kind="ServiceAccount", name=service_account_name, namespace=namespace)
        metadata = client.V1ObjectMeta(name=role_binding_name)
        role = client.V1RoleRef(kind="Role", name=role_name, api_group="rbac.authorization.k8s.io")
        body = client.V1RoleBinding(subjects=[subject], metadata=metadata, role_ref=role)

        try:
            self.rbac_cli.create_namespaced_role_binding(namespace=namespace, body=body)
            logger.info('Created role {} in namespace {}'.format(role_binding_name, namespace))
            return True
        except client.rest.ApiException as e:
            logger.exception(e)
            return False

    def create_namespaced_custom_object(self, filepath, namespace="default"):
        """Create custom object (couchbase) using file in namespace"""
        yaml_objects = Parser(filepath).return_manifests_dict
        for manifest in yaml_objects:
            try:
                self.custom_def_cli.create_namespaced_custom_object(group="couchbase.com",
                                                                    version="v1",
                                                                    namespace=namespace,
                                                                    plural="couchbaseclusters",
                                                                    body=manifest)

                logger.info('Created {}/{} in namespace  {}'.format(manifest["kind"],
                                                                    manifest["metadata"]["name"], namespace))
            except client.rest.ApiException as e:
                logger.exception(e)

    def patch_or_create_namespaced_configmap(self, name, literal=None, value_of_literal=None, namespace="default",
                                             second_literal=None, value_of_second_literal=None, data=None):
        """Patch configmap and if not exist create"""
        # Instantiate the configmap object
        body = client.V1ConfigMap()
        metadata = client.V1ObjectMeta(name=name)
        body.data = data
        if not data:
            body.data = {literal: value_of_literal}
        body.metadata = metadata
        if second_literal:
            body.data = {literal: value_of_literal, second_literal: value_of_second_literal}
        try:
            self.core_cli.patch_namespaced_config_map(name, namespace, body)
            logger.info('Configmap  {} in namespace {} has been patched'.format(name, namespace))
            return
        except client.rest.ApiException as e:
            if e.status == 404 or not e.status:
                try:
                    self.core_cli.create_namespaced_config_map(namespace=namespace, body=body)
                    logger.info('Created configmap {} in namespace {}'.format(name, namespace))
                    return True
                except client.rest.ApiException as e:
                    logger.exception(e)
                    return False
            logger.exception(e)
            return False

    def patch_namespaced_deployment_scale(self, name, replicas, namespace="default"):
        """Scale deployment using name in namespace to replicas"""
        body = {
            'spec': {
                'replicas': replicas,
            }
        }
        try:
            self.apps_cli.patch_namespaced_deployment_scale(name, namespace, body)
            logger.info('Deployemnt {} in namespace {} has been scaled to {}'.format(name, namespace, replicas))
            return
        except client.rest.ApiException as e:
            logger.exception(e)
            return False

    def patch_or_create_namespaced_secret(self, name, literal, value_of_literal, namespace="default",
                                          secret_type="Opaque", second_literal=None, value_of_second_literal=None, data=None):
        """Patch secret and if not exist create"""
        # Instantiate the Secret object
        body = client.V1Secret()
        metadata = client.V1ObjectMeta(name=name)
        body.data = data
        if not data:
            body.data = {literal: value_of_literal}
        body.metadata = metadata
        body.type = secret_type
        if second_literal:
            body.data = {literal: value_of_literal, second_literal: value_of_second_literal}
        try:
            self.core_cli.patch_namespaced_secret(name, namespace, body)
            logger.info('Secret  {} in namespace {} has been patched'.format(name, namespace))
            return
        except client.rest.ApiException as e:
            if e.status == 404 or not e.status:
                try:
                    self.core_cli.create_namespaced_secret(namespace=namespace, body=body)
                    logger.info('Created secret {} of type {} in namespace {}'.format(name, secret_type, namespace))
                    return True
                except client.rest.ApiException as e:
                    logger.exception(e)
                    return False
            logger.exception(e)
            return False

    def patch_namespaced_deployment(self, name, image, namespace="default"):
        """Scale deployment using name in namespace to replicas"""
        # Configureate Pod template container
        container = client.V1Container(name=name)
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": name}),
            spec=client.V1PodSpec(containers=[container]))
        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            template=template,
            selector={'matchLabels': {'app': name}})
        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=name),
            spec=spec)
        deployment.spec.template.spec.containers[0].image = image
        try:
            self.apps_cli.patch_namespaced_deployment(name, namespace, deployment)
            logger.info('Image of deployemnt {} in namespace {} has been updated to {}'.format(name, namespace, image))
            return
        except client.rest.ApiException as e:
            if e.status == 404 or not e.status:
                logger.info(
                    'Deployment {} in namespace {} is not found'.format(name, namespace))
                return
            logger.exception(e)
            return False

    def patch_namespaced_statefulset(self, name, image, namespace="default"):
        """Scale deployment using name in namespace to replicas"""
        # Configureate Pod template container
        container = client.V1Container(name=name)
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": name}),
            spec=client.V1PodSpec(containers=[container]))
        # Create the specification of statefulset
        spec = client.V1StatefulSetSpec(
            template=template,
            selector={'matchLabels': {'app': name}},
            service_name=name)
        # Instantiate the statefulset object
        statefulset = client.V1StatefulSet(
            api_version="apps/v1",
            kind="StatefulSet",
            metadata=client.V1ObjectMeta(name=name),
            spec=spec)
        statefulset.spec.template.spec.containers[0].image = image
        try:
            self.apps_cli.patch_namespaced_stateful_set(name, namespace, statefulset)
            logger.info('Image of statefulset {} in namespace {} has been updated to {}'.format(name, namespace, image))
            return
        except client.rest.ApiException as e:
            if e.status == 404 or not e.status:
                logger.info(
                    'Statefulset {} in namespace {} is not found'.format(name, namespace))
                return
            logger.exception(e)
            return False

    def patch_namespaced_daemonset(self, name, image, namespace="default"):
        """Scale deployment using name in namespace to replicas"""
        # Configureate Pod template container
        container = client.V1Container(name=name)
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": name}),
            spec=client.V1PodSpec(containers=[container]))
        # Create the specification of DaemonSet
        spec = client.V1DaemonSetSpec(
            template=template,
            selector={'matchLabels': {'app': name}})
        # Instantiate the DaemonSet object
        daemonset = client.V1DaemonSet(
            api_version="apps/v1",
            kind="DaemonSet",
            metadata=client.V1ObjectMeta(name=name),
            spec=spec)
        daemonset.spec.template.spec.containers[0].image = image
        try:
            self.apps_cli.patch_namespaced_daemon_set(name, namespace, daemonset)
            logger.info('Image of daemonset {} in namespace {} has been updated to {}'.format(name, namespace, image))
            return
        except client.rest.ApiException as e:
            if e.status == 404 or not e.status:
                logger.info(
                    'Daemonset {} in namespace {} is not found'.format(name, namespace))
                return
            logger.exception(e)
            return False

    def patch_namespaced_stateful_set_scale(self, name, replicas, namespace="default"):
        """Scale statefulset using name in namespace to replicas"""
        body = {
            'spec': {
                'replicas': replicas,
            }
        }
        try:
            self.apps_cli.patch_namespaced_stateful_set_scale(name, namespace, body)
            logger.info('StatefulSet {} in namespace {} has been scaled to {}'.format(name, namespace, replicas))
            return
        except client.rest.ApiException as e:
            logger.exception(e)
            return False

    def create_objects_from_dict(self, filepath, namespace=None):
        """Create kubernetes object from a yaml encapsulated inside a dictionary"""
        yaml_objects = Parser(filepath).return_manifests_dict
        for manifest in yaml_objects:
            try:
                # handle special cases of namespace injection
                if namespace:
                    manifest["metadata"]["namespace"] = namespace
                utils.create_from_dict(self.api_client, manifest)
                logger.info('Created {} /  {}'.format(manifest["kind"], manifest["metadata"]["name"]))
            except client.rest.ApiException as e:
                logger.exception(e)

    def list_pod_name_by_label(self, namespace="default", app_label=None):
        """List pods names with app label in namespace"""
        try:
            pods_name = []
            response = self.core_cli.list_namespaced_pod(namespace=namespace, label_selector=app_label, watch=False)
            number_of_pods = len(response.items)
            for i in range(number_of_pods):
                pods_name.append(response.items[i].metadata.name)
            return pods_name
        except client.rest.ApiException as e:
            logger.exception(e)

    def read_namespaced_secret(self, name, namespace="default"):
        """Read secret with name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                secret = self.core_cli.read_namespaced_secret(name=name, namespace=namespace)
                logger.info('Reading secret {}'.format(name))
                return secret
            except client.rest.ApiException as e:
                response = self.check_read_error_and_response(starting_time, e)

    def read_namespaced_service(self, name, namespace="default"):
        """Read service with name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                service = self.core_cli.read_namespaced_service(name=name, namespace=namespace)
                logger.info('Reading service {}'.format(name))
                return service
            except client.rest.ApiException as e:
                response = self.check_read_error_and_response(starting_time, e)

    def read_namespaced_configmap(self, name, namespace="default"):
        """Read configmap with name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                configmap = self.core_cli.read_namespaced_config_map(name=name, namespace=namespace)
                logger.info('Reading configmap {}'.format(name))
                return configmap
            except client.rest.ApiException as e:
                response = self.check_read_error_and_response(starting_time, e)

    def read_namespaced_ingress(self, name, namespace="default"):
        """Read service with name in namespace"""
        starting_time = time.time()
        response = True
        while response:
            try:
                ingress = self.extenstion_cli.read_namespaced_ingress(name=name, namespace=namespace)
                logger.info('Reading ingress {}'.format(name))
                return ingress
            except client.rest.ApiException as e:
                response = self.check_read_error_and_response(starting_time, e)

    def read_namespaced_pod_status(self, name, timeout, namespace="default"):
        """Read pod status with name in namespace"""

        starting_time = time.time()
        try:
            finished_prep_boolean = False
            while not finished_prep_boolean:
                end_time = time.time()
                running_time = end_time - starting_time
                time.sleep(5)
                response = self.core_cli.read_namespaced_pod_status(name=name, namespace=namespace)
                all_statuses = response.status.conditions
                try:
                    for status in all_statuses:
                        if status.type == "Ready":
                            try:
                                check_if_job = response.metadata.labels["job-name"]
                            except KeyError:
                                check_if_job = None
                            if check_if_job and status.reason == "PodCompleted":
                                finished_prep_boolean = True
                                break
                            elif not check_if_job and status.status == "True":
                                finished_prep_boolean = True
                                break
                except TypeError:
                    logger.warning("Pod might not exist or was evicted.")
                if running_time > timeout:
                    logger.warning("Timeout exceeded. This may not be an error. Please check pods statuses.")
                    return False
                logger.info("Waiting for pod {} to get ready".format(name))
        except client.rest.ApiException as e:
            logger.exception(e)

    def check_pods_statuses(self, namespace="default", app_label=None, timeout=300):
        """Loop through pod names and check statuses"""
        time.sleep(10)
        pods_name = self.list_pod_name_by_label(namespace, app_label)
        for pod_name in pods_name:
            self.read_namespaced_pod_status(name=pod_name, namespace=namespace, timeout=timeout)

    def connect_get_namespaced_pod_exec(self, exec_command, app_label=None, namespace="default"):
        """Execute command in pod with app label in namespace"""

        pods_name = self.list_pod_name_by_label(namespace, app_label)
        for pod_name in pods_name:
            try:
                resp = stream(self.core_cli.connect_get_namespaced_pod_exec,
                              name=pod_name,
                              namespace=namespace,
                              command=exec_command,
                              stderr=True, stdin=False,
                              stdout=True, tty=False)
                logger.info("{}".format(resp))
            except client.rest.ApiException as e:
                logger.exception(e)

    def get_namespaces(self):
        """List all namespaces"""
        try:
            return self.core_cli.list_namespace(pretty="pretty")
        except client.rest.ApiException as e:
            logger.exception(e)
            return False

    def list_nodes(self):
        """List all nodes"""
        try:
            nodes_list = self.core_cli.list_node(pretty="pretty")
            logger.info("Getting list of nodes")
            return nodes_list
        except client.rest.ApiException as e:
            logger.exception(e)
            return False

    def read_node(self, name):
        """Read node information"""
        try:
            node_data = self.core_cli.read_node(name)
            logger.info("Getting node {} data".format(name))
            return node_data
        except client.rest.ApiException as e:
            logger.exception(e)
            return False
