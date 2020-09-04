import contextlib
import os

import pytest


@pytest.fixture()
def settings():
    from pygluu.kubernetes.settings import SettingsHandler, unlink_settings_json

    handler = SettingsHandler()
    yield handler
    unlink_settings_json()


@pytest.mark.parametrize("given, expected", [
    (True, "Y"),
    (False, "N"),
])
def test_confirm_yesno(monkeypatch, given, expected):
    from pygluu.kubernetes.terminal.common import confirm_yesno

    monkeypatch.setattr("click.confirm", lambda x: given)
    assert confirm_yesno("Random question") == expected


def test_prompt_license_no_prompt(settings):
    from pygluu.kubernetes.terminal.license import PromptLicense

    prompt = PromptLicense(settings, accept_license=True)
    prompt.prompt_license()
    assert settings.get("ACCEPT_GLUU_LICENSE") == "Y"


def test_prompt_version_no_prompt(settings):
    from pygluu.kubernetes.terminal.version import PromptVersion

    prompt = PromptVersion(settings, version="4.2")
    prompt.prompt_version()
    assert settings.get("GLUU_VERSION") == "4.2"


@pytest.mark.parametrize("given, expected", [
    ("", "4.2.0_01"),  # default if empty
    ("4.2.1_dev", "4.2.1_dev"),  # non-empty shouldn't be overriden
])
def test_prompt_version_merge_names_tags(settings, given, expected):
    import json
    from pygluu.kubernetes.terminal.version import PromptVersion

    with open("./gluu_versions.json", "w") as f:
        json.dump({"4.2": {"LDAP_IMAGE_TAG": "4.2.0_01"}}, f)

    settings.set("GLUU_VERSION", "4.2")
    settings.set("LDAP_IMAGE_TAG", given)

    PromptVersion(settings)
    assert settings.get("LDAP_IMAGE_TAG") == expected

    with contextlib.suppress(FileNotFoundError):
        os.unlink("./gluu_versions.json")


@pytest.mark.parametrize("given, expected", [
    ("", "4.2"),
    ("4.2", "4.2"),
])
def test_prompt_version(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.version import PromptVersion

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompt = PromptVersion(settings)

    # unset GLUU_VERSION in order to prompt user-input
    settings.set("GLUU_VERSION", "")

    prompt.prompt_version()
    assert settings.get("GLUU_VERSION") == expected


def test_prompt_license_accepted(monkeypatch, settings):
    from pygluu.kubernetes.terminal.license import PromptLicense

    monkeypatch.setattr("click.confirm", lambda x: True)

    PromptLicense(settings)
    assert settings.get("ACCEPT_GLUU_LICENSE") == "Y"


def test_prompt_license_rejected(monkeypatch, settings):
    from pygluu.kubernetes.terminal.license import PromptLicense

    monkeypatch.setattr("click.confirm", lambda x: False)

    with pytest.raises(SystemExit):
        PromptLicense(settings)


@pytest.mark.parametrize("given, expected", [
    (1, "microk8s"),
    (2, "minikube"),
    (3, "eks"),
    (4, "gke"),
    (5, "aks"),
    (6, "do"),
    (7, "local"),
    ("random", "microk8s"),
])
def test_prompt_arch(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.architecture import PromptArch

    monkeypatch.setattr("click.prompt", lambda x, default: given)

    settings.set("DEPLOYMENT_ARCH", "")
    prompt = PromptArch(settings)
    prompt.prompt_arch()
    assert settings.get("DEPLOYMENT_ARCH") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu"),
    ("my-ns", "my-ns"),
])
def test_prompt_gluu_namespace(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.namespace import PromptNamespace

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompt = PromptNamespace(settings)
    prompt.prompt_gluu_namespace()
    assert settings.get("GLUU_NAMESPACE") == expected


def test_prompt_jackrabbit_enable(monkeypatch, settings):
    from pygluu.kubernetes.terminal.jackrabbit import PromptJackrabbit

    monkeypatch.setattr("click.confirm", lambda x, default: True)

    settings.set("JACKRABBIT_ADMIN_PASSWORD", "Test1234#")
    settings.set("JACKRABBIT_CLUSTER", "N")
    settings.set("JACKRABBIT_ADMIN_ID", "admin")
    settings.set("JACKRABBIT_STORAGE_SIZE", "4Gi")

    prompt = PromptJackrabbit(settings)
    prompt.prompt_jackrabbit()

    assert settings.get("INSTALL_JACKRABBIT") == "Y"
    assert settings.get("JACKRABBIT_STORAGE_SIZE") == "4Gi"
    assert settings.get("JACKRABBIT_URL") == "http://jackrabbit:8080"
    assert settings.get("JACKRABBIT_ADMIN_ID") == "admin"
    assert settings.get("JACKRABBIT_ADMIN_PASSWORD") == "Test1234#"
    assert settings.get("JACKRABBIT_CLUSTER") == "N"


def test_prompt_jackrabbit_disable_no_url(monkeypatch, settings):
    from pygluu.kubernetes.terminal.jackrabbit import PromptJackrabbit

    monkeypatch.setattr("click.confirm", lambda x, default: False)
    monkeypatch.setattr("click.prompt", lambda x, default: "http://jackrabbit:8080")

    settings.set("JACKRABBIT_ADMIN_ID", "admin")
    settings.set("JACKRABBIT_ADMIN_PASSWORD", "Test1234#")
    settings.set("JACKRABBIT_CLUSTER", "N")

    prompt = PromptJackrabbit(settings)
    prompt.prompt_jackrabbit()

    assert settings.get("INSTALL_JACKRABBIT") == "N"
    assert settings.get("JACKRABBIT_URL") == "http://jackrabbit:8080"


def test_prompt_confirm_params(monkeypatch, settings):
    from pygluu.kubernetes.terminal.confirmsettings import PromptConfirmSettings

    monkeypatch.setattr("click.confirm", lambda x: True)

    prompt = PromptConfirmSettings(settings)
    prompt.confirm_params()
    assert settings.get("CONFIRM_PARAMS") == "Y"


@pytest.mark.parametrize("given, expected", [
    ("", "gluu"),  # default
    ("random", "random"),
])
def test_prompt_helm_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("INSTALL_GLUU_GATEWAY", "N")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("GLUU_HELM_RELEASE_NAME") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "ningress"),  # default
    ("random", "random"),
])
def test_prompt_helm_ingress_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("GLUU_HELM_RELEASE_NAME", "gluu")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("INSTALL_GLUU_GATEWAY", "N")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("NGINX_INGRESS_RELEASE_NAME") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "ingress-nginx"),  # default
    ("random", "random"),
])
def test_prompt_helm_ingress_namespace(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("GLUU_HELM_RELEASE_NAME", "gluu")
    settings.set("INSTALL_GLUU_GATEWAY", "N")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("NGINX_INGRESS_NAMESPACE") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu-gateway"),  # default
    ("random", "random"),
])
def test_prompt_helm_gg_helm_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("INSTALL_GLUU_GATEWAY", "Y")
    settings.set("GLUU_GATEWAY_UI_HELM_RELEASE_NAME", "gluu-gateway-ui")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("KONG_HELM_RELEASE_NAME") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu-gateway-ui"),  # default
    ("random", "random"),
])
def test_prompt_helm_gg_ui_helm_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("INSTALL_GLUU_GATEWAY", "Y")
    settings.set("KONG_HELM_RELEASE_NAME", "gluu-gateway")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("GLUU_GATEWAY_UI_HELM_RELEASE_NAME") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "4.2"),
    ("4.2", "4.2"),
])
def test_prompt_upgrade_version(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.upgrade import PromptUpgrade

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompt = PromptUpgrade(settings)
    prompt.prompt_upgrade()
    assert settings.get("GLUU_UPGRADE_TARGET_VERSION") == expected


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_prompt_volumes_identifier(monkeypatch, settings, persistence):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x: "vol-1234")

    settings.set("PERSISTENCE_BACKEND", persistence)

    prompt = PromptVolumes(settings)
    prompt.prompt_volumes_identifier()
    assert settings.get("LDAP_STATIC_VOLUME_ID") == "vol-1234"


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_prompt_disk_uris(monkeypatch, settings, persistence):
    from pygluu.kubernetes.terminal.volumes import PromptVolumes

    monkeypatch.setattr("click.prompt", lambda x: "MC_aks")

    settings.set("PERSISTENCE_BACKEND", persistence)

    prompt = PromptVolumes(settings)
    prompt.prompt_disk_uris()
    assert settings.get("LDAP_STATIC_DISK_URI") == "MC_aks"


@pytest.mark.parametrize("given, expected", [
    ("", "postgres"),  # default
    ("random", "random"),
])
def test_prompt_postgres_namespace(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.postgres import PromptPostgres

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("POSTGRES_REPLICAS", 3)
    settings.set("POSTGRES_URL", "postgres.postgres.svc.cluster.local")

    prompt = PromptPostgres(settings)
    prompt.prompt_postgres()
    assert settings.get("POSTGRES_NAMESPACE") == expected


@pytest.mark.parametrize("given, expected", [
    ("", 3),  # default
    (2, 2),
])
def test_prompt_postgres_replicas(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.postgres import PromptPostgres

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("POSTGRES_NAMESPACE", "postgres")
    settings.set("POSTGRES_URL", "postgres.postgres.svc.cluster.local")

    prompt = PromptPostgres(settings)
    prompt.prompt_postgres()
    assert settings.get("POSTGRES_REPLICAS") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "postgres.postgres.svc.cluster.local"),  # default
    ("random", "random"),
])
def test_prompt_postgres_url(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.postgres import PromptPostgres

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("POSTGRES_NAMESPACE", "postgres")
    settings.set("POSTGRES_REPLICAS", 3)

    prompt = PromptPostgres(settings)
    prompt.prompt_postgres()
    assert settings.get("POSTGRES_URL") == expected
