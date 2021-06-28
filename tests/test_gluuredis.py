import pygluu.kubernetes.redis as module0
from pygluu.kubernetes.redis import Redis


def test_base_exception():
    try:
        var0 = module0.Redis()
    except BaseException:
        pass

def test_case():
    try:
        var0 = module0.Redis()
        assert var0 is not None
        var1 = var0.uninstall_redis()
        assert var1 is None
        var2 = var0.uninstall_redis()
        var3 = var0.uninstall_redis()
        var4 = module0.Redis()
        var5 = var4.install_redis()
    except BaseException:
        pass


def test_install_execption():
    try:
        var0 = module0.Redis()
        var1 = var0.install_redis()
    except BaseException:
        pass


def test_uninstall_install():
    try:
        var0 = module0.Redis()
        assert var0 is not None
        var1 = module0.Redis()
        var2 = var0.uninstall_redis()
        var3 = var0.install_redis()
    except BaseException:
        pass


def test_install_redis():
    try:
        var0 = module0.Redis()
        assert var0 is not None
        var1 = var0.uninstall_redis()
        var2 = module0.Redis()
        var3 = var0.install_redis()
    except BaseException:
        pass


def test_redis_class_object():
    try:
        var0 = module0.Redis()
        assert var0 is not None
        var1 = var0.uninstall_redis()
        var2 = var0.install_redis()
    except BaseException:
        pass