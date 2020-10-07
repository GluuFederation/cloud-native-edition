def test_secret_key_generated(tmpdir):
    from pygluu.kubernetes.gui.app import resolve_secret_key

    file_ = tmpdir.join("secret-key")
    expected = resolve_secret_key(str(file_))

    with open(str(file_)) as f:
        actual = f.read()
    assert actual == expected


def test_secret_key_reused(tmpdir):
    from pygluu.kubernetes.gui.app import resolve_secret_key

    file_ = tmpdir.join("secret-key")
    file_.write("testingsecret")
    assert resolve_secret_key(str(file_)) == "testingsecret"
