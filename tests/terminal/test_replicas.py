import pytest


def test_prompt_replicas_auth_server(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("OXTRUST_REPLICAS", 1)

    PromptReplicas(settings).prompt_replicas()
    assert settings.get("AUTH_SERVER_REPLICAS") == 1


def test_prompt_replicas_oxtrust(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)

    PromptReplicas(settings).prompt_replicas()
    assert settings.get("OXTRUST_REPLICAS") == 1


def test_prompt_replicas_fido2(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)
    settings.set("OXTRUST_REPLICAS", 1)

    settings.set("ENABLE_FIDO2", "Y")
    PromptReplicas(settings).prompt_replicas()
    assert settings.get("FIDO2_REPLICAS") == 1


def test_prompt_replicas_scim(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)
    settings.set("OXTRUST_REPLICAS", 1)

    settings.set("ENABLE_SCIM", "Y")
    PromptReplicas(settings).prompt_replicas()
    assert settings.get("SCIM_REPLICAS") == 1


@pytest.mark.parametrize("type_", ["ldap", "hybrid"])
def test_prompt_replicas_persistence(monkeypatch, settings, type_):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)
    settings.set("OXTRUST_REPLICAS", 1)

    settings.set("CN_PERSISTENCE_BACKEND", type_)
    PromptReplicas(settings).prompt_replicas()
    assert settings.get("LDAP_REPLICAS") == 1


def test_prompt_replicas_oxshibboleth(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)
    settings.set("OXTRUST_REPLICAS", 1)

    settings.set("ENABLE_OXSHIBBOLETH", "Y")
    PromptReplicas(settings).prompt_replicas()
    assert settings.get("OXSHIBBOLETH_REPLICAS") == 1


def test_prompt_replicas_oxpassport(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)
    settings.set("OXTRUST_REPLICAS", 1)

    settings.set("ENABLE_OXPASSPORT", "Y")
    PromptReplicas(settings).prompt_replicas()
    assert settings.get("OXPASSPORT_REPLICAS") == 1


def test_prompt_replicas_client_api(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)
    settings.set("OXTRUST_REPLICAS", 1)

    settings.set("ENABLE_CLIENT_API", "Y")
    PromptReplicas(settings).prompt_replicas()
    assert settings.get("CLIENT_API_REPLICAS") == 1


def test_prompt_replicas_casa(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)
    settings.set("OXTRUST_REPLICAS", 1)

    settings.set("ENABLE_CASA", "Y")
    PromptReplicas(settings).prompt_replicas()
    assert settings.get("CASA_REPLICAS") == 1


def test_prompt_replicas_radius(monkeypatch, settings):
    from pygluu.kubernetes.terminal.replicas import PromptReplicas

    monkeypatch.setattr("click.prompt", lambda x, default: 1)

    # bypass
    settings.set("AUTH_SERVER_REPLICAS", 1)
    settings.set("OXTRUST_REPLICAS", 1)

    settings.set("ENABLE_RADIUS", "Y")
    PromptReplicas(settings).prompt_replicas()
    assert settings.get("RADIUS_REPLICAS") == 1
