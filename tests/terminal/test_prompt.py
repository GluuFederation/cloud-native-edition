import pygluu.kubernetes.terminal.prompt as module0


def test_class_object():
    var0 = module0.Prompt()
    var1 = var0.load_settings()


def test_images():
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    var2 = var0.images()


def test_replicas():
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    var2 = var0.replicas()


def test_istio():
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    var2 = var0.istio()


def test_jackrabbit():
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    var2 = var0.jackrabbit()


def test_namespace():
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    var2 = var0.namespace()


def test_arch():
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    var2 = var0.arch()


def test_backup(settings):
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    settings.set("global.storageClass.provisioner", "kubernetes.io/gce-pd")
    var2 = var0.backup()


def test_couchbase(settings):
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    settings.set("global.cnPersistenceType", "ldap")
    var2 = var0.couchbase()


def test_base_exception_against_prompt():
    try:
        var0 = module0.Prompt()
    except BaseException:
        pass
