def test_prompt_persistence_backend_ldap(monkeypatch, settings):
    from pygluu.kubernetes.terminal.persistencebackend import PromptPersistenceBackend

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    settings.set("PERSISTENCE_BACKEND", "")
    PromptPersistenceBackend(settings).prompt_persistence_backend()

    assert settings.get("PERSISTENCE_BACKEND") == "ldap"
    assert "ldap" in settings.get("ENABLED_SERVICES_LIST")


def test_prompt_persistence_backend_couchbase(monkeypatch, settings):
    from pygluu.kubernetes.terminal.persistencebackend import PromptPersistenceBackend

    monkeypatch.setattr("click.prompt", lambda x, default: 2)

    settings.set("PERSISTENCE_BACKEND", "")
    PromptPersistenceBackend(settings).prompt_persistence_backend()
    assert settings.get("PERSISTENCE_BACKEND") == "couchbase"


def test_prompt_persistence_backend_hybrid(monkeypatch, settings):
    from pygluu.kubernetes.terminal.persistencebackend import PromptPersistenceBackend

    monkeypatch.setattr("click.prompt", lambda x, default: 3)

    settings.set("PERSISTENCE_BACKEND", "")
    PromptPersistenceBackend(settings).prompt_persistence_backend()
    assert settings.get("PERSISTENCE_BACKEND") == "hybrid"
