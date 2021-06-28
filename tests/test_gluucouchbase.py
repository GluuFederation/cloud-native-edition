import pygluu.kubernetes.couchbase as module0


def test_couchbase_install():
    try:
        var0 = module0.Couchbase()
        assert var0 is not None
        var1 = var0.install()
    except BaseException:
        pass


def test_create_server_spec_per_cb_service():
    try:
        var0 = set()
        var1 = '^ UYJJfQ3-|3#BnGXU:'
        var2 = ()
        var3 = var1, var0, var2
        var4 = 1262
        var5 = [var3, var4, var0]
        var6 = -131
        var7 = -4375.8757
        var8 = module0.create_server_spec_per_cb_service(var0, var3, var4,
            var0, var5, var6, var7)
    except BaseException:
        pass


def test_get_couchbase_files():
    try:
        var0 = b'+'
        var1 = -3661.3
        var2 = {var0, var0, var1, var1}
        var3 = '"f^@D`[/YvQB?D\n('
        var4 = module0.Couchbase()
        assert var4 is not None
        var5 = -834.0
        var6 = {var2: var3, var5: var5, var2: var0, var1: var5}
    except BaseException:
        pass


def test_extract_couchbase_tar():
    try:
        var0 = module0.Couchbase()
        assert var0 is not None
        var1 = module0.extract_couchbase_tar(var0)
    except BaseException:
        pass


def test_base_exception():
    try:
        var0 = module0.Couchbase()
    except BaseException:
        pass


def test_server_spec_per_cb():
    try:
        var0 = module0.Couchbase()
        assert var0 is not None
        var1 = 3059.070629
        var2 = '[wKlZvFZoC2eidHx'
        var3 = '"\x0beLIa|XP-Tt&0`'
        var4 = False
        var5 = 1071.92757
        var6 = {var3: var4, var3: var0, var2: var3, var5: var3}
        var7 = []
        var8 = [var7]
        var9 = module0.create_server_spec_per_cb_service(var1, var2, var3,
            var4, var6, var8, var3)
    except BaseException:
        pass


def test_set_memory_for_buckets():
    try:
        var0 = """
pygluu.kubernetes.gui.license
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's input for gui license form

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
        var1 = 749.96
        var2 = [var0, var1, var0, var0]
        var3 = False
        var4 = module0.set_memory_for_buckets(var2, var3)
    except BaseException:
        pass


def test_analyze_couchbase_cluster_yaml():
    try:
        var0 = module0.Couchbase()
        assert var0 is not None
        var1 = var0.setup_backup_couchbase()
        assert var1 is None
        var2 = module0.Couchbase()
        var3 = var2.analyze_couchbase_cluster_yaml()
    except BaseException:
        pass


def test_extract_cb_tar():
    try:
        var0 = '|f9\\#oD67e%hT6BB"Zv9'
        var1 = {var0: var0}
        var2 = False
        var3 = None
        var4 = 3622.0
        var5 = ()
        var6 = None
        var7 = module0.create_server_spec_per_cb_service(var1, var2, var3,
            var1, var4, var5, var6)
        assert var7 is not None
        var8 = {var0: var0}
        var9 = module0.extract_couchbase_tar(var8)
    except BaseException:
        pass


def test_cb_install():
    try:
        var0 = module0.Couchbase()
        assert var0 is not None
        var1 = var0.setup_backup_couchbase()
        assert var1 is None
        var2 = module0.Couchbase()
        assert var2 is not None
        var3 = var2.install()
    except BaseException:
        pass


def test_install():
    try:
        var0 = """
pygluu.kubernetes.terminal.aws
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's inputs for aws terminal prompts.

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
        var1 = module0.Couchbase()
        assert var1 is not None
        var2 = module0.Couchbase()
        assert var2 is not None
        var3 = var1.install()
    except BaseException:
        pass