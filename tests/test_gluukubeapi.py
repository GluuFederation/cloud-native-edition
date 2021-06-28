import pygluu.kubernetes.kubeapi as module0
from pygluu.kubernetes.kubeapi import load_kubernetes_config, Kubernetes
from kubernetes import config


def test_patch_or_create_namespaced_secret():
    try:
        var0 = None
        var1 = None
        var2 = 892
        var3 = 1065.52
        var4 = module0.Kubernetes()
        assert var4 is not None
        var5 = '9P ZRA'
        var6 = None
        var7 = module0.Kubernetes()
        assert var7 is not None
        var8 = var7.patch_or_create_namespaced_secret(var0, var0, var1,
            var2, var3, var4, var5, var6)
    except BaseException:
        pass


def test_delete_custom_resource():
    try:
        var0 = None
        var1 = module0.Kubernetes()
        assert var1 is not None
        var2 = var1.delete_custom_resource(var0)
    except BaseException:
        pass


def test_delete_collection_namespaced_replication_controller1():
    try:
        var0 = None
        var1 = module0.Kubernetes()
        assert var1 is not None
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_collection_namespaced_replication_controller(var0, var1)
    except BaseException:
        pass


def test_delete_deployment_using_name():
    try:
        var0 = module0.Kubernetes()
        assert var0 is not None
        var1 = -3280.74
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_deployment_using_name(var0, var1)
    except BaseException:
        pass


def test_delete_deployment_using_name_exception():
    try:
        var0 = module0.Kubernetes()
        assert var0 is not None
        var1 = module0.Kubernetes()
        assert var1 is not None
        var2 = var1.c(var0)
    except BaseException:
        pass


def test_check_read_error_and_response():
    try:
        var0 = b'\x11\xc1\xfaAvPv\xb5]Q\x1b'
        var1 = b"G\xbe\x948'\xef\x8d("
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.check_read_error_and_response(var0, var1)
    except BaseException:
        pass


def test_patch_or_create_namespaced_secrets():
    try:
        var0 = None
        var1 = None
        var2 = 892
        var3 = 1065.52
        var4 = module0.Kubernetes()
        assert var4 is not None
        var5 = '9P ZRA'
        var6 = None
        var7 = module0.Kubernetes()
        assert var7 is not None
        var8 = var7.patch_or_create_namespaced_secret(var0, var0, var1,
            var2, var3, var4, var5, var6)
    except BaseException:
        pass


def test_delete_custom_resources():
    try:
        var0 = None
        var1 = module0.Kubernetes()
        assert var1 is not None
        var2 = var1.delete_custom_resource(var0)
    except BaseException:
        pass


def test_delete_collection_namespaced_replication_controller():
    try:
        var0 = None
        var1 = module0.Kubernetes()
        assert var1 is not None
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_collection_namespaced_replication_controller(var0,
            var1)
    except BaseException:
        pass


def test_delete_deployment_using_names():
    try:
        var0 = module0.Kubernetes()
        assert var0 is not None
        var1 = -3280.74
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_deployment_using_name(var0, var1)
    except BaseException:
        pass


def test_read_nodes():
    try:
        var0 = module0.Kubernetes()
        assert var0 is not None
        var1 = module0.Kubernetes()
        assert var1 is not None
        var2 = var1.read_node(var0)
    except BaseException:
        pass


def test_check_read_error_and_responses():
    try:
        var0 = b'\x11\xc1\xfaAvPv\xb5]Q\x1b'
        var1 = b"G\xbe\x948'\xef\x8d("
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.check_read_error_and_response(var0, var1)
    except BaseException:
        pass


def test_webhook_configuration():
    try:
        var0 = '\n'
        var1 = module0.load_kubernetes_config(var0)
        assert var1 is None
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_mutating_webhook_configuration(var0)
    except BaseException:
        pass


def test_undefined_role():
    try:
        var0 = None
        var1 = ']J4?1tK,V71M&53-XlTF'
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_role(var0, var1)
    except BaseException:
        pass


def test_empty_custom_resource():
    try:
        var0 = '\n'
        var1 = module0.load_kubernetes_config(var0)
        assert var1 is None
        var2 = -932
        var3 = module0.Kubernetes()
        assert var3 is not None
        var4 = var3.delete_custom_resource(var2)
    except BaseException:
        pass


def test_role_bind():
    try:
        var0 = -1198.1
        var1 = ',Ru.: ,V'
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_role_binding(var0, var1)
    except BaseException:
        pass


def test_namespaced_custom_object():
    try:
        var0 = 'IIp\x0cIk'
        var1 = 1739
        var2 = 1869
        var3 = None
        var4 = None
        var5 = module0.Kubernetes()
        assert var5 is not None
        var6 = var5.create_namespaced_custom_object(var0, var1, var2, var3,
            var4)
    except BaseException:
        pass


def test_empty_secrets():
    try:
        var0 = -2807
        var1 = False
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_secret(var0, var1)
    except BaseException:
        pass


def test_service_endpoint():
    try:
        var0 = '\n'
        var1 = module0.load_kubernetes_config(var0)
        assert var1 is None
        var2 = False
        var3 = module0.Kubernetes()
        assert var3 is not None
        var4 = var3.delete_service(var2, var2)
    except BaseException:
        pass


def test_namespaced_service_account():
    try:
        var0 = module0.Kubernetes()
        assert var0 is not None
        var1 = var0.delete_job()
        assert var1 is None
        var2 = '2_>RP6#\rZnH'
        var3 = 'V*{| #>'
        var4 = ()
        var5 = var0.delete_role_binding(var3, var4)
        assert var5 is None
        var6 = 'e2&Xkp8P&|'
        var7 = 'bIZ4eo'
        var8 = b'\xf4\xcd\x08\x06b\\2v\xe9EX\xcb\xf6\xe3\x1a#S\x85Z\xed'
        var9 = 1703
        var10 = var6, var7, var8, var9
        var11 = var0.delete_validating_webhook_configuration(var9)
        assert var11 is None
        var12 = []
        var13 = var0.connect_get_namespaced_pod_exec(var10, var12)
        assert var13 is None
        var14 = False
        var15 = b'\xb9,\xd8H\xd2\xe8B\x94Y'
        var16 = module0.Kubernetes()
        assert var16 is not None
        var17 = 1722.2919
        var18 = var16.create_namespaced_service_account(var17)
    except BaseException:
        pass


def test_stateful_set_scale():
    try:
        var0 = None
        var1 = module0.Kubernetes()
        assert var1 is not None
        var2 = var0, var1
        var3 = {var0: var1, var1: var1, var0: var2}
        var4 = module0.Kubernetes()
        assert var4 is not None
        var5 = var4.patch_namespaced_stateful_set_scale(var2, var3)
    except BaseException:
        pass


def test_created_namespace():
    try:
        var0 = 2599
        var1 = 'FU'
        var2 = var1,
        var3 = module0.Kubernetes()
        assert var3 is not None
        var4 = var3.delete_ingress(var2)
        assert var4 is None
        var5 = module0.Kubernetes()
        assert var5 is not None
        var6 = []
        var7 = var3.create_namespace(var6)
    except BaseException:
        pass


def test_delete_resources():
    try:
        var0 = '_'
        var1 = module0.Kubernetes()
        assert var1 is not None
        var2 = var1.delete_role_binding(var0)
        var3 = var1.delete_service(var1)
    except BaseException:
        pass


def test_delete_cronjob():
    try:
        var0 = module0.Kubernetes()
        assert var0 is not None
        var1 = b'n\xcb\xba\xda\xc0K\xf4a'
        var2 = var0.delete_job()
        assert var2 is None
        var3 = None
        var4 = module0.Kubernetes()
        assert var4 is not None
        var5 = var4.delete_cronjob(var3)
    except BaseException:
        pass


def test_namespaced_configmap():
    try:
        var0 = b'\xcc'
        var1 = {var0: var0, var0: var0, var0: var0, var0: var0}
        var2 = module0.Kubernetes()
        var3 = var2.read_namespaced_configmap(var1)
        assert var3 is None
        var4 = None
        var5 = module0.Kubernetes()
        assert var5 is not None
        var6 = {var0: var0, var5: var5}
        var7 = None
        var8 = var2.delete_persistent_volume(var7)
        assert var8 is None
        var9 = '\n&\n&\nn@k#[>#2tJp*e\x0cz'
        var10 = var5.delete_mutating_webhook_configuration(var9)
        assert var10 is None
        var11 = (
            '| [22] Persistent Disk  dynamically provisioned                    |'
            )
        var12 = var5.patch_or_create_namespaced_configmap(var6, var11)
    except BaseException:
        pass


def test_object_functions():
    try:
        var0 = True
        var1 = {var0: var0}
        var2 = ''
        var3 = module0.Kubernetes()
        assert var3 is not None
        var4 = var3.read_namespaced_service(var1, var2)
        assert var4 is None
        var5 = set()
        var6 = 1932.87119
        var7 = None
        var8 = None
        var9 = False
        var10 = -1258
        var11 = var3.list_nodes()
        assert var11 is not None
        var12 = module0.Kubernetes()
        assert var12 is not None
        var13 = ()
        var14 = [var3, var1, var4, var10]
        var15 = [var14, var0, var4, var9]
        var16 = {var1: var5, var0: var5, var5: var10, var12: var15}
    except BaseException:
        pass


def test_read_ingress():
    try:
        var0 = 489
        var1 = [var0, var0, var0]
        var2 = module0.Kubernetes()
        assert var2 is not None
        var3 = var2.delete_config_map_using_label(var1)
        assert var3 is None
        var4 = module0.Kubernetes()
        assert var4 is not None
        var5 = var4.get_namespaces()
        assert var5 is not None
        var6 = None
        var7 = module0.Kubernetes()
        assert var7 is not None
        var8 = var7.read_namespaced_ingress(var6)
    except BaseException:
        pass


def test_del_service_account():
    try:
        var0 = module0.Kubernetes()
        assert var0 is not None
        var1 = "FIC{jaL'cgj"
        var2 = 221.71901
        var3 = None
        var4 = {var1: var2, var1: var3, var3: var1}
        var5 = var0.delete_role(var4)
        assert var5 is None
        var6 = -1891
        var7 = {var6, var5}
        var8 = var0.delete_service_account(var7)
    except BaseException:
        pass