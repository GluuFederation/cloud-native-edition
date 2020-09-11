import pytest


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_volumes_identifier(monkeypatch, settings, persistence):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x: "vol-1234")

    settings.set("PERSISTENCE_BACKEND", persistence)

    prompt = PromptVolumes(settings)
    prompt.prompt_volumes_identifier()
    assert settings.get("LDAP_STATIC_VOLUME_ID") == "vol-1234"


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_disk_uris(monkeypatch, settings, persistence):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x: "MC_aks")

    settings.set("PERSISTENCE_BACKEND", persistence)

    prompt = PromptVolumes(settings)
    prompt.prompt_disk_uris()
    assert settings.get("LDAP_STATIC_DISK_URI") == "MC_aks"
