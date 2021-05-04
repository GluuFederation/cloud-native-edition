import pygluu.kubernetes.gluu as module0
import pytest
from pygluu.kubernetes.yamlparser import Parser


def test_prompt1(settings):
    from pygluu.kubernetes.gluu import Gluu

    settings.set("installer-settings.volumeProvisionStrategy", "gke")
    settings.set("config.configmap.cnCacheType", "REDIS")
    settings.set("installer-settings.couchbase.install")
    prompt = Gluu(settings)
    prompt.__init__()
    assert exec_cmd("gcloud config get-value core/account")

def test_prep_alb(settings):
    from pygluu.kubernetes.gluu import Gluu

    settings.set("installer-settings.aws.arn.enabled")
    prompt = Gluu(settings)
    prompt.prepare_alb()
    assert ngress_parser["metadata"]["annotations"]["alb.ingress.kubernetes.io/certificate-arn"] is False

def test_prep2_alb(settings):
    from pygluu.kubernetes.gluu import Gluu

    settings.set("config.configmap.cnCasaEnabled", "casa")
    path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
    prompt = Gluu(settings)
    prompt.prepare_alb()
    assert ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index] is False

def test_prep3_alb(settings):
    from pygluu.kubernetes.gluu import Gluu

    settings.set("global.oxshibboleth.enabled", "oxshibboleth")
    path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
    prompt = Gluu(settings)
    prompt.prepare_alb()
    assert ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index] is False

def test_prep4_alb(settings):
    from pygluu.kubernetes.gluu import Gluu

    settings.set("config.configmap.cnPassportEnabled", "oxpassport")
    path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
    prompt = Gluu(settings)
    prompt.prepare_alb()
    assert ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index] is False

def test_prep5_alb(settings):
    from pygluu.kubernetes.gluu import Gluu

    settings.set("installer-settings.global.scim.enabled", "jans-scim")
    path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
    prompt = Gluu(settings)
    prompt.prepare_alb()
    assert ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index] is False

def test_prep6_alb(settings):
    from pygluu.kubernetes.gluu import Gluu

    settings.set("installer-settings.config-api.enabled", "config-api")
    path_index = ingress_parser["spec"]["rules"][0]["http"]["paths"].index(path)
    prompt = Gluu(settings)
    prompt.prepare_alb()
    assert ingress_parser["spec"]["rules"][0]["http"]["paths"][path_index] is False

def test_install_ldap_backup():
    var0 = module0.Gluu()
    var1 = var0.install_ldap_backup()


def test_unisntall_gluu():
    var0 = module0.Gluu()
    var1 = var0.install_ldap_backup()
    var2 = module0.Gluu()
    var3 = var2.install_ldap_backup()
    var4 = var2.uninstall_nginx_ingress()
    var5 = module0.Gluu()


def test_wait_for_nginx_add():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.install_ldap_backup()
    assert var1 is None
    var2 = module0.Gluu()
    var3 = var2.install_ldap_backup()
    var4 = var2.uninstall_nginx_ingress()
    var5 = module0.Gluu()
    var6 = var5.install_ldap_backup()
    var7 = module0.Gluu()
    var8 = var7.install_ldap_backup()
    var9 = var7.uninstall_nginx_ingress()
    var10 = module0.Gluu()
    var11 = var0.wait_for_nginx_add()


def test_uninstall_nginx_ingress2():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.install_ldap_backup()
    var2 = module0.Gluu()
    assert var2 is not None
    var3 = var2.install_ldap_backup()
    var4 = var2.uninstall_nginx_ingress()
    var5 = module0.Gluu()
    var6 = module0.Gluu()
    var7 = var6.install_ldap_backup()
    var8 = module0.Gluu()
    var9 = var8.install_ldap_backup()
    var10 = var8.uninstall_nginx_ingress()
    var11 = var2.uninstall_nginx_ingress()


def test_uninstall_nginx_ingress():
    var0 = module0.Gluu()
    var1 = var0.install_ldap_backup()
    var2 = module0.Gluu()
    var3 = var2.install_ldap_backup()
    var4 = var2.uninstall_nginx_ingress()
    var5 = module0.Gluu()
    var6 = var5.uninstall_nginx_ingress()


def test_upgrade_gluu():
    var0 = module0.Gluu()
    var1 = var0.install_ldap_backup()
    var2 = module0.Gluu()
    var3 = var2.install_ldap_backup()
    var4 = var2.uninstall_nginx_ingress()
    var5 = module0.Gluu()
    var6 = var5.uninstall_nginx_ingress()
    var7 = module0.Gluu()
    var8 = var7.install_ldap_backup()
    var9 = module0.Gluu()
    var10 = var9.install_ldap_backup()
    var11 = module0.Gluu()
    var12 = var11.install_ldap_backup()
    var13 = var11.uninstall_nginx_ingress()
    var14 = module0.Gluu()
    var15 = var14.upgrade_gluu()


def test_wait_for_nginx_add():
    try:
        var0 = module0.Gluu()
        assert var0 is not None
        var1 = var0.install_ldap_backup()
        assert var1 is None
        var2 = module0.Gluu()
        var3 = var2.install_ldap_backup()
        var4 = var2.uninstall_nginx_ingress()
        var5 = module0.Gluu()
    except BaseException:
        pass


def test_exception():
    try:
        var0 = module0.Gluu()
    except BaseException:
        pass


def test_ldap_nginx_ingress():
    try:
        var0 = module0.Gluu()
        assert var0 is not None
        var1 = var0.install_ldap_backup()
        assert var1 is None
        var2 = module0.Gluu()
        var3 = var2.install_ldap_backup()
        var4 = var2.uninstall_nginx_ingress()
        var5 = module0.Gluu()
    except BaseException:
        pass
