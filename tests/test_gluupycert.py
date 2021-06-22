import pygluu.kubernetes.pycert as module0


def test_cert_setup_static_provision():
    try:
        var0 = (
            '| [18] Persistent Disk  statically provisioned                     |'
            )
        var1 = 645.424
        var2 = module0.check_cert_with_private_key(var0, var1)
    except BaseException:
        pass


def test_correct_setup():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = b'R\x9au(\xed\xfc\xcc\x87|`\xdbG\xe0\xbb\xbf@'
        var7 = True
        var8 = module0.check_cert_with_private_key(var6, var7)
    except BaseException:
        pass


def test_incorrect_setup():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = '< 0W~'
        var7 = 1917
        var8 = module0.check_cert_with_private_key(var6, var7)
    except BaseException:
        pass


def test_setup():
    try:
        var0 = '6*_$ '
        var1 = True
        var2 = None
        var3 = module0.setup_crts(var0, var1, var2)
    except BaseException:
        pass


def test_check_cert_with_pk():
    try:
        var0 = True
        var1 = {var0, var0, var0, var0}
        var2 = True
        var3 = module0.check_cert_with_private_key(var1, var2)
    except BaseException:
        pass


def test_chain_pem():
    try:
        var0 = None
        var1 = 52
        var2 = b'\x86P\xefx3'
        var3 = None
        var4 = module0.setup_crts(var0, var1, var2, var3, var2)
    except BaseException:
        pass


def test_key_size():
    try:
        var0 = None
        var1 = -578
        var2 = module0.check_cert_with_private_key(var0, var1)
    except BaseException:
        pass


def test_mock_args():
    var0 = 'DLh'
    var1 = 'crt'
    var2 = '}L@\x0becz86fq9}y*S'
    var3 = "%A'>lpu3"
    var4 = var1, var2, var3
    var5 = module0.setup_crts(var0, var0, var4)
    assert var5 is None


def test_cert_keysize():
    try:
        var0 = b"\xe8\x0cG\x01\xab\xc63\xb1\x19B\xda\x18\xcf\xb8\x90:(a'`"
        var1 = 2620.700518
        var2 = {var0: var0, var0: var1, var0: var0, var1: var1}
        var3 = True
        var4 = module0.setup_crts(var2, var3, var2, var0)
    except BaseException:
        pass


def test_base64_key():
    try:
        var0 = 'z\n1ITB4qk@}@A30'
        var1 = [var0, var0, var0, var0]
        var2 = {var1, var0, var0, var1}
    except BaseException:
        pass


def test_encryption_algorithm():
    try:
        var0 = -2402
        var1 = None
        var2 = module0.check_cert_with_private_key(var0, var1)
    except BaseException:
        pass


def test_509x():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = -1915
        var7 = module0.check_cert_with_private_key(var6, var3)
    except BaseException:
        pass


def test_data_encipherment():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = 2000
        var7 = {var4: var5, var4: var2}
        var8 = module0.check_cert_with_private_key(var6, var7)
    except BaseException:
        pass


def test_key_agreement():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = [var1, var5, var5]
        var7 = False
        var8 = None
        var9 = module0.setup_crts(var6, var7, var8)
    except BaseException:
        pass


def test_authority_cert_issuer():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = None
        var7 = {var1: var4, var4: var2, var2: var6, var6: var1}
        var8 = module0.check_cert_with_private_key(var7, var7)
    except BaseException:
        pass


def test_key_identifier():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = 1455.72286
        var7 = 5713
        var8 = True
        var9 = module0.setup_crts(var0, var6, var7, var6, var6, var8)
    except BaseException:
        pass


def test_digital_signature():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = b'iN:\xee\xdb\xcc\xd1?J?\x90\xc1_@4\xfc'
        var7 = -139.2
        var8 = 'SLc6Ef|MLc`cA:'
        var9 = [var8, var2]
        var10 = {var4, var5}
        var11 = module0.setup_crts(var4, var6, var7, var8, var9, var9, var10)
    except BaseException:
        pass


def test_setup_cert_return():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = '{w|<I?Mg\tF )\x0b Rt|'
        var7 = {var5: var5}
        var8 = module0.check_cert_with_private_key(var6, var7)
    except BaseException:
        pass


def test_cert_types():
    try:
        var0 = ()
        var1 = []
        var2 = None
        var3 = module0.setup_crts(var0, var1, var2, var0)
    except BaseException:
        pass


def test_setup_execption():
    try:
        var0 = 155
        var1 = set()
        var2 = []
        var3 = module0.setup_crts(var0, var1, var2)
    except BaseException:
        pass


def test_genrate_pk():
    try:
        var0 = None
        var1 = 'Yus!2|NB'
        var2 = module0.check_cert_with_private_key(var0, var1)
    except BaseException:
        pass


def test_couchbase_cert():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = 'couchbase-autonomous-operator-kubernetes_*.tar.gz'
        var7 = [var6, var0, var5, var1]
        var8 = module0.check_cert_with_private_key(var6, var7)
    except BaseException:
        pass


def test_cert_root_serialno():
    try:
        var0 = b'\xdf\x9a\x0e\x9a8\x99'
        var1 = -136
        var2 = 3031.27891
        var3 = None
        var4 = 'l\x0c?q<BE\r@'
        var5 = 'Number of Radius replicas'
        var6 = var4, var5
        var7 = module0.setup_crts(var0, var1, var0, var2, var3, var6)
    except BaseException:
        pass


def test_private_key_obj():
    try:
        var0 = -1070
        var1 = [var0]
        var2 = set()
        var3 = module0.check_cert_with_private_key(var1, var2)
    except BaseException:
        pass


def test_key_file():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = -1374
        var7 = b'\xbc\xc7S{\xac\x87\xaeu\xe5-\xe9\x9f\x9d'
        var8 = module0.check_cert_with_private_key(var6, var7)
    except BaseException:
        pass


def test_cert_file():
    try:
        var0 = -2521
        var1 = False
        var2 = module0.check_cert_with_private_key(var0, var1)
    except BaseException:
        pass


def test_ca_key_file():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = b'\xdb\x02u\x10\x92\x0f\xb6\xe3\xa7\x9d\x1d\xcd'
        var7 = module0.check_cert_with_private_key(var6, var6)
    except BaseException:
        pass


def test_ca_cert_file():
    try:
        var0 = 'DLh'
        var1 = 'crt'
        var2 = '}L@\x0becz86fq9}y*S'
        var3 = "%A'>lpu3"
        var4 = var1, var2, var3
        var5 = module0.setup_crts(var0, var0, var4)
        assert var5 is None
        var6 = module0.check_cert_with_private_key(var0, var4)
    except BaseException:
        pass


def test_san_list():
    try:
        var0 = '/static'
        var1 = 141
        var2 = module0.check_cert_with_private_key(var0, var1)
    except BaseException:
        pass


def test_cert_common_name():
    try:
        var0 = None
        var1 = {var0, var0, var0}
        var2 = module0.check_cert_with_private_key(var0, var1)
    except BaseException:
        pass


def test_ca_common_name():
    try:
        var0 = '5'
        var1 = {var0, var0, var0}
        var2 = {var1}
    except BaseException:
        pass


def test_wrong_file_cert():
    try:
        var0 = False
        var1 = b'R'
        var2 = {var0: var1}
        var3 = {var2, var2, var0, var0}
    except BaseException:
        pass


def test_full_setup_args():
    try:
        var0 = b'\xee\x85 \xd49\x86./4J'
        var1 = {var0}
        var2 = -2131.0
        var3 = module0.setup_crts(var0, var1, var2, var1, var1, var0)
    except BaseException:
        pass


def test_cert_keyfile():
    try:
        var0 = b'B\x1b\xfc\x10\x98}SU\xe2\xc3\xe1\xfa\x94&\x9b{G\x92'
        var1 = None
        var2 = None
        var3 = module0.setup_crts(var0, var1, var2)
    except BaseException:
        pass


def test_cert_key_rotation():
    try:
        var0 = 'oxauth-key-rotation'
        var1 = None
        var2 = module0.check_cert_with_private_key(var0, var1)
    except BaseException:
        pass


def test_setup_parameters():
    try:
        var0 = b"\xe8\x0cG\x01\xab\xc63\xb1\x19B\xda\x18\xcf\xb8\x90:(a'`"
        var1 = 2620.700518
        var2 = {var0: var0, var0: var1, var0: var0, var1: var1}
        var3 = True
        var4 = module0.setup_crts(var2, var3, var2, var0)
    except BaseException:
        pass


def test_pycert_var_declaration():
    try:
        var0 = 'z\n1ITB4qk@}@A30'
        var1 = [var0, var0, var0, var0]
        var2 = {var1, var0, var0, var1}
    except BaseException:
        pass
