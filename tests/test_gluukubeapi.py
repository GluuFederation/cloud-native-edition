import pygluu.kubernetes.kubeapi as module0
from pygluu.kubernetes.kubeapi import load_kubernetes_config, Kubernetes
from kubernetes import config


def test_load_kubernetes_config():
    var0 = '\n'
    var1 = module0.load_kubernetes_config(var0)
    assert var1 is None


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
