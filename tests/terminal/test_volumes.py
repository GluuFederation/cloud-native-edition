import pytest


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_volumes_identifier(monkeypatch, settings, persistence):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x: "vol-1234")

    settings.set("PERSISTENCE_BACKEND", persistence)
    PromptVolumes(settings).prompt_volumes_identifier()
    assert settings.get("LDAP_STATIC_VOLUME_ID") == "vol-1234"


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_disk_uris(monkeypatch, settings, persistence):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x: "MC_aks")

    settings.set("PERSISTENCE_BACKEND", persistence)
    PromptVolumes(settings).prompt_disk_uris()
    assert settings.get("LDAP_STATIC_DISK_URI") == "MC_aks"


@pytest.mark.parametrize("arch, vol_type", [
    ("eks", 7),
    ("gke", 12),
    ("aks", 17),
    ("do", 22),
    ("local", 26),
])
def test_prompt_app_volume_type(monkeypatch, settings, arch, vol_type):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x, default: vol_type)

    settings.set("DEPLOYMENT_ARCH", arch)
    PromptVolumes(settings).prompt_app_volume_type()
    assert settings.get("APP_VOLUME_TYPE") == vol_type


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_prompt_storage(monkeypatch, settings, persistence):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x, default: "4Gi")

    settings.set("PERSISTENCE_BACKEND", persistence)
    PromptVolumes(settings).prompt_storage()
    assert settings.get("LDAP_STORAGE_SIZE") == "4Gi"


def test_prompt_volumes_microk8s(settings):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    settings.set("DEPLOYMENT_ARCH", "microk8s")
    PromptVolumes(settings).prompt_volumes()
    assert settings.get("APP_VOLUME_TYPE") == 1


def test_prompt_volumes_minikube(settings):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    settings.set("DEPLOYMENT_ARCH", "minikube")
    PromptVolumes(settings).prompt_volumes()
    assert settings.get("APP_VOLUME_TYPE") == 2


@pytest.mark.parametrize("vol_type", [0, 8, 13, 18])
def test_prompt_volumes_misc_vol_type(settings, vol_type):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    settings.set("APP_VOLUME_TYPE", vol_type)
    PromptVolumes(settings).prompt_volumes()


@pytest.mark.parametrize("arch", ["aks", "eks", "gke"])
def test_prompt_volumes_jackrabbit(monkeypatch, settings, arch):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x, default: "io1")

    settings.set("DEPLOYMENT_ARCH", arch)
    settings.set("APP_VOLUME_TYPE", 7)
    PromptVolumes(settings).prompt_volumes()
    assert settings.get("LDAP_JACKRABBIT_VOLUME") == "io1"
