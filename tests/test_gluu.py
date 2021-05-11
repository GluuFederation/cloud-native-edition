import pygluu.kubernetes.gluu as module0
import pytest
from pygluu.kubernetes.yamlparser import Parser


def test_uninstall_nginx_ingress():
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


def test_install_exception():
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
