import pygluu.kubernetes.postgres as module0


def test_base_exception():
    try:
        var0 = module0.Postgres()
    except BaseException:
        pass
