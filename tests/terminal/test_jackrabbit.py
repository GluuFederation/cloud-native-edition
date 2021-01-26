def test_jackrabbit_enable(monkeypatch, settings):
    from pygluu.kubernetes.terminal.jackrabbit import PromptJackrabbit

    monkeypatch.setattr("click.confirm", lambda x, default: True)

    settings.set("CN_JACKRABBIT_ADMIN_PASSWORD", "Test1234#")
    settings.set("CN_JACKRABBIT_CLUSTER", "N")
    settings.set("CN_JACKRABBIT_ADMIN_ID", "admin")
    settings.set("CN_JACKRABBIT_STORAGE_SIZE", "4Gi")

    prompt = PromptJackrabbit(settings)
    prompt.prompt_jackrabbit()

    assert settings.get("CN_INSTALL_JACKRABBIT") == "Y"
    assert settings.get("CN_JACKRABBIT_STORAGE_SIZE") == "4Gi"
    assert settings.get("CN_JACKRABBIT_URL") == "http://jackrabbit:8080"
    assert settings.get("CN_JACKRABBIT_ADMIN_ID") == "admin"
    assert settings.get("CN_JACKRABBIT_ADMIN_PASSWORD") == "Test1234#"
    assert settings.get("CN_JACKRABBIT_CLUSTER") == "N"


def test_jackrabbit_disable_no_url(monkeypatch, settings):
    from pygluu.kubernetes.terminal.jackrabbit import PromptJackrabbit

    monkeypatch.setattr("click.confirm", lambda x, default: False)
    monkeypatch.setattr("click.prompt", lambda x, default: "http://jackrabbit:8080")

    settings.set("CN_JACKRABBIT_ADMIN_ID", "admin")
    settings.set("CN_JACKRABBIT_ADMIN_PASSWORD", "Test1234#")
    settings.set("CN_JACKRABBIT_CLUSTER", "N")

    prompt = PromptJackrabbit(settings)
    prompt.prompt_jackrabbit()

    assert settings.get("CN_INSTALL_JACKRABBIT") == "N"
    assert settings.get("CN_JACKRABBIT_URL") == "http://jackrabbit:8080"
