import pygluu.kubernetes.redis as module0


def test_base_exception():
    try:
        var0 = module0.Redis()
    except BaseException:
        pass
