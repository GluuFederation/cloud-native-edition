import pygluu.kubernetes.couchbase as module0


def test_exception():
    try:
        var0 = module0.Couchbase()
    except BaseException:
        pass


def test_uninstall_parameters():
    try:
        var0 = module0.Couchbase()
        assert var0 is not None
        var1 = module0.Couchbase()
        assert var1 is not None
        var2 = var1.uninstall()
    except BaseException:
        pass


def test_uninstall_modules():
    try:
        var0 = module0.Couchbase()
        assert var0 is not None
        var1 = module0.Couchbase()
        assert var1 is not None
        var2 = module0.Couchbase()
        assert var2 is not None
        var3 = module0.Couchbase()
        assert var3 is not None
        var4 = module0.Couchbase()
        var5 = var4.uninstall()
    except BaseException:
        pass


def test_uninstall_couchbase():
    try:
        var0 = module0.Couchbase()
        assert var0 is not None
        var1 = module0.Couchbase()
        var2 = var1.uninstall()
    except BaseException:
        pass