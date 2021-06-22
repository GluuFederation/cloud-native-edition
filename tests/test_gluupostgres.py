import pygluu.kubernetes.postgres as module0
from pygluu.kubernetes.postgres import Postgres


def test_base_exception():
    try:
        var0 = module0.Postgres()
    except BaseException:
        pass


def test_class_object1():
    var0 = module0.Postgres()
    var1 = var0.uninstall_postgres()


def test_class_object2():
    var0 = module0.Postgres()
    var1 = var0.__init__()