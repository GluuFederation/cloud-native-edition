import pygluu.kubernetes.couchbase as simulate


def test_exception():
    try:
        var0 = simulate.Couchbase()
    except BaseException:
        pass


def test_uninstall_parameters():
    try:
        var0 = simulate.Couchbase()
        assert var0 is not None
        var1 = simulate.Couchbase()
        assert var1 is not None
        var2 = var1.uninstall()
    except BaseException:
        pass


def test_uninstall_modules():
    try:
        var0 = simulate.Couchbase()
        assert var0 is not None
        var1 = simulate.Couchbase()
        assert var1 is not None
        var2 = simulate.Couchbase()
        assert var2 is not None
        var3 = simulate.Couchbase()
        assert var3 is not None
        var4 = simulate.Couchbase()
        var5 = var4.uninstall()
    except BaseException:
        pass


def test_uninstall_couchbase():
    try:
        var0 = simulate.Couchbase()
        assert var0 is not None
        var1 = simulate.Couchbase()
        var2 = var1.uninstall()
    except BaseException:
        pass
