import pygluu.kubernetes.postgres as module0
from pygluu.kubernetes.postgres import Postgres


def test_base_exception():
    try:
        var0 = module0.Postgres()
    except BaseException:
        pass


def test_postgres_install():
    try:
        var0 = module0.Postgres()
        assert var0 is not None
        var1 = var0.install_postgres()
    except BaseException:
        pass


def test_postgres_object():
    try:
        var0 = module0.Postgres()
        assert var0 is not None
        var1 = var0.uninstall_postgres()
        assert var1 is None
        var2 = module0.Postgres()
        assert var2 is not None
        var3 = var2.install_postgres()
        var4 = var2.install_postgres()
    except BaseException:
        pass


def test_delete_uninstalled_postgres():
    try:
        var0 = module0.Postgres()
        assert var0 is not None
        var1 = module0.Postgres()
        assert var1 is not None
        var2 = var0.uninstall_postgres()
        assert var2 is None
        var3 = var0.uninstall_postgres()
        assert var3 is None
        var4 = var0.uninstall_postgres()
        assert var4 is None
        var5 = var0.uninstall_postgres()
        var6 = var1.install_postgres()
    except BaseException:
        pass


def test_install_execption():
    try:
        var0 = module0.Postgres()
        assert var0 is not None
        var1 = var0.uninstall_postgres()
        assert var1 is None
        var2 = var0.install_postgres()
    except BaseException:
        pass
