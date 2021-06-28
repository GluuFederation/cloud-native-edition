import pygluu.kubernetes.gluu as module0

def test_check_install_nginx_ingress():
    var0 = ()
    var1 = module0.Gluu()
    assert var1 is not None
    var2 = var1.check_install_nginx_ingress(var0)


def test_prepare_alb():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.prepare_alb()
    assert var1 is None


def test_uninstall_nginx_ingress():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.prepare_alb()
    assert var1 is None
    var2 = var0.uninstall_nginx_ingress()
    assert var2 is None


def test_install_gluu():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.prepare_alb()
    assert var1 is None
    var2 = module0.Gluu()
    assert var2 is not None
    var3 = var2.prepare_alb()
    assert var3 is None
    var4 = var2.uninstall_nginx_ingress()
    assert var4 is None
    var5 = None
    var6 = var0.install_gluu(var5)


def test_gluu_object():
    var0 = module0.Gluu()
    assert var0 is not None


def test_uninstall_gluu():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.prepare_alb()
    assert var1 is None
    var2 = var0.uninstall_nginx_ingress()
    assert var2 is None
    var3 = var0.uninstall_gluu()


def test_uninstall_install_gluu():
    var0 = ()
    var1 = module0.Gluu()
    assert var1 is not None
    var2 = var1.check_install_nginx_ingress(var0)
    var3 = module0.Gluu()
    var4 = var3.prepare_alb()
    var5 = var3.uninstall_nginx_ingress()
    var6 = var3.uninstall_gluu()
    var7 = module0.Gluu()
    var8 = var7.prepare_alb()
    var9 = module0.Gluu()
    var10 = var9.prepare_alb()
    var11 = var9.uninstall_nginx_ingress()
    var12 = None
    var13 = var7.install_gluu(var12)
    var14 = module0.Gluu()
    var15 = var14.prepare_alb()
    var16 = var14.uninstall_nginx_ingress()
    var17 = module0.Gluu()
    var18 = var17.prepare_alb()
    var19 = var1.uninstall_nginx_ingress()


def test_install_gluu_without_ingress():
    var0 = ()
    var1 = module0.Gluu()
    assert var1 is not None
    var2 = var1.check_install_nginx_ingress(var0)
    var3 = module0.Gluu()
    var4 = var3.prepare_alb()
    var5 = var3.uninstall_nginx_ingress()
    var6 = module0.Gluu()
    var7 = var6.prepare_alb()
    var8 = module0.Gluu()
    var9 = var8.prepare_alb()
    var10 = var8.uninstall_nginx_ingress()
    var11 = None
    var12 = var6.install_gluu(var11)
    var13 = var1.uninstall_gluu()


def test_delete_ingress():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.prepare_alb()
    assert var1 is None
    var2 = module0.Gluu()
    assert var2 is not None
    var3 = var2.prepare_alb()
    assert var3 is None
    var4 = var2.uninstall_nginx_ingress()
    assert var4 is None
    var5 = module0.Gluu()
    assert var5 is not None


def test_empty_gluu_object():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.prepare_alb()
    assert var1 is None
    var2 = module0.Gluu()
    assert var2 is not None
    var3 = ()
    var4 = module0.Gluu()
    assert var4 is not None
    var5 = var4.check_install_nginx_ingress(var3)
    var6 = var2.install_gluu()


def test_base_exception():
    try:
        var0 = module0.Gluu()
    except BaseException:
        pass

#slow
def test_deploy_alb():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = var0.install_gluu()
    var2 = var0.install_gluu()
    var3 = var0.prepare_alb()
    var4 = var0.uninstall_gluu()
    var5 = {var2}
    var6 = var0.install_gluu(var5)
    var7 = var0.uninstall_nginx_ingress()
    var8 = var0.check_install_nginx_ingress()
    var9 = var0.uninstall_nginx_ingress()
    var10 = var0.prepare_alb()
    var11 = var0.prepare_alb()
    var12 = var0.uninstall_gluu()

#slow
def test_uninstall():
    var0 = module0.Gluu()
    assert var0 is not None
    var1 = module0.Gluu()
    assert var1 is not None
    var2 = var1.prepare_alb()
    assert var2 is None
    var3 = module0.Gluu()
    assert var3 is not None
    var4 = module0.Gluu()
    assert var4 is not None
    var5 = var4.uninstall_nginx_ingress()
    var6 = var3.install_gluu()
    var7 = var3.install_gluu()
    var8 = var3.uninstall_gluu()
    var9 = var3.prepare_alb()
    var10 = var3.install_gluu()
    var11 = var3.uninstall_gluu()
    var12 = var3.uninstall_gluu()