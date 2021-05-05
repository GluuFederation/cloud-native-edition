import pygluu.kubernetes.postgres as module0

def test_postgres_class_object():
    var0 = module0.Postgres()


def test_base_exception():
    try:
        var0 = module0.Postgres()
    except BaseException:
        pass


def test_postgres_install_exception():
    try:
        var0 = module0.Postgres()
        var1 = var0.install_postgres()
    except BaseException:
        pass


def test_install_postgres():
    try:
        var0 = module0.Postgres()
        assert var0 is not None
        var1 = var0.install_postgres()
    except BaseException:
        pass


def test_uninstall_install_prompt():
    try:
        var0 = module0.Postgres()
        assert var0 is not None
        var1 = module0.Postgres()
        assert var1 is not None
        var2 = module0.Postgres()
        assert var2 is not None
        var3 = var0.uninstall_postgres()
        assert var3 is None
        var4 = module0.Postgres()
        assert var4 is not None
        var5 = var2.install_postgres()
    except BaseException:
        pass


def test_uninstall_postgres():
    var0 = module0.Postgres()
    assert var0 is not None
    var1 = module0.Postgres()
    assert var1 is not None
    var2 = module0.Postgres()
    assert var2 is not None
    var3 = var0.uninstall_postgres()
    assert var3 is None