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

def test_confirm_settings(settings):
    var0 = module0.Prompt()
    settings.set("installer-settings.confirmSettings", False)
    var1 = var0.load_settings()

    var2 = var0.confirm_settings()

def test_configuration():
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    var2 = var0.configuration()

def test_backup(settings):
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    settings.set("global.storageClass.provisioner", "kubernetes.io/gce-pd")
    var2 = var0.backup()

def test_cache():
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    var2 = var0.cache()

def test_couchbase(settings):
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    settings.set("global.cnPersistenceType", "ldap")
    var2 = var0.couchbase()

def test_volumes(settings):
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    settings.set("global.cnPersistenceType", "couchbase")
    settings.set("global.jackrabbit")
    var2 = var0.volumes()

def test_ldap(settings):
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    settings.set("global.cnPersistenceType", "hybrid")
    var2 = var0.ldap()

def test_network(settings):
    var0 = module0.Prompt()
    var1 = var0.load_settings()
    settings.set("CN_HOST_EXT_IP", "")
    settings.set("installer-settings.volumeProvisionStrategy", "awsEbsDynamic")
    settings.set("global.istio.enabled", False)
    var2 = var0.network()

def test_base_exception_against_prompt():
    try:
        var0 = module0.Prompt()
    except BaseException:
        pass

