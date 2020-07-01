import contextlib
import os

import pytest


@pytest.fixture
def prompter():
    from pygluu.kubernetes.prompt import Prompt

    prompt = Prompt(accept_license=True, version="4.2.0_dev")

    yield prompt

    # cleanup
    for file_ in ["settings.json", "gluu_versions.json"]:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(file_)


@pytest.mark.parametrize("given, expected", [
    (True, "Y"),
    (False, "N"),
])
def test_confirm_yesno(monkeypatch, given, expected):
    from pygluu.kubernetes.prompt import confirm_yesno

    monkeypatch.setattr("click.confirm", lambda x: given)
    assert confirm_yesno("Random question") == expected


def test_prompt_license_no_prompt(prompter):
    prompter.prompt_license()
    assert prompter.settings["ACCEPT_GLUU_LICENSE"] == "Y"


def test_prompt_version_no_prompt(prompter):
    prompter.prompt_version()
    assert prompter.settings["GLUU_VERSION"] == "4.2.0_dev"


@pytest.mark.parametrize("given, expected", [
    ("", "0"),
    ("4.2.0_dev", "4.2.0_dev"),
])
def test_prompt_version(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    # unset GLUU_VERSION in order to prompt user-input
    prompter.settings["GLUU_VERSION"] = ""
    prompter.prompt_version()
    assert prompter.settings["GLUU_VERSION"] == expected


def test_prompt_license_accepted(monkeypatch, prompter):
    monkeypatch.setattr("click.confirm", lambda x: True)

    # unset GLUU_VERSION in order to prompt user-input
    prompter.settings["ACCEPT_GLUU_LICENSE"] = ""
    prompter.prompt_license()
    assert prompter.settings["ACCEPT_GLUU_LICENSE"] == "Y"


def test_prompt_license_rejected(monkeypatch, prompter):
    monkeypatch.setattr("click.confirm", lambda x: False)

    with pytest.raises(SystemExit):
        # unset GLUU_VERSION in order to prompt user-input
        prompter.settings["ACCEPT_GLUU_LICENSE"] = ""
        prompter.prompt_license()


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
def test_prompt_arch(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given)
    prompter.prompt_arch()
    assert prompter.settings["DEPLOYMENT_ARCH"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu"),
    ("my-ns", "my-ns"),
])
def test_prompt_gluu_namespace(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.prompt_gluu_namespace()
    assert prompter.settings["GLUU_NAMESPACE"] == expected


def test_prompt_jackrabbit_enable(monkeypatch, prompter):
    monkeypatch.setattr("click.confirm", lambda x, default: True)
    monkeypatch.setattr("click.prompt", lambda x, default: "4Gi")

    prompter.prompt_jackrabbit()
    assert prompter.settings["INSTALL_JACKRABBIT"] == "Y"
    assert prompter.settings["JACKRABBIT_USER"] == "admin"
    assert prompter.settings["JACKRABBIT_URL"] == "http://jackrabbit:8080"
    assert prompter.settings["JACKRABBIT_STORAGE_SIZE"] == "4Gi"


def test_prompt_jackrabbit_disable_no_url(monkeypatch, prompter):
    monkeypatch.setattr("click.confirm", lambda x, default: False)
    monkeypatch.setattr("click.prompt", lambda x, default: "http://jackrabbit:8080")

    prompter.settings["JACKRABBIT_USER"] = "admin"
    prompter.prompt_jackrabbit()
    assert prompter.settings["INSTALL_JACKRABBIT"] == "N"
    assert prompter.settings["JACKRABBIT_URL"] == "http://jackrabbit:8080"


def test_prompt_jackrabbit_disable_no_user(monkeypatch, prompter):
    monkeypatch.setattr("click.confirm", lambda x, default: False)
    monkeypatch.setattr("click.prompt", lambda x, default: "admin")

    prompter.settings["JACKRABBIT_URL"] = "http://jackrabbit:8080"
    prompter.prompt_jackrabbit()
    assert prompter.settings["INSTALL_JACKRABBIT"] == "N"
    assert prompter.settings["JACKRABBIT_USER"] == "admin"


def test_prompt_confirm_params(monkeypatch, prompter):
    monkeypatch.setattr("click.confirm", lambda x: True)

    prompter.confirm_params()
    assert prompter.settings["CONFIRM_PARAMS"] == "Y"


@pytest.mark.parametrize("given, expected", [
    ("", "gluu"),  # default
    ("random", "random"),
])
def test_prompt_helm_release_name(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.settings["NGINX_INGRESS_RELEASE_NAME"] = "ningress"
    prompter.settings["NGINX_INGRESS_NAMESPACE"] = "ingress-nginx"
    prompter.settings["INSTALL_GLUU_GATEWAY"] = "N"

    prompter.prompt_helm
    assert prompter.settings["GLUU_HELM_RELEASE_NAME"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", "ningress"),  # default
    ("random", "random"),
])
def test_prompt_helm_ingress_release_name(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.settings["GLUU_HELM_RELEASE_NAME"] = "gluu"
    prompter.settings["NGINX_INGRESS_NAMESPACE"] = "ingress-nginx"
    prompter.settings["INSTALL_GLUU_GATEWAY"] = "N"

    prompter.prompt_helm
    assert prompter.settings["NGINX_INGRESS_RELEASE_NAME"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", "ingress-nginx"),  # default
    ("random", "random"),
])
def test_prompt_helm_ingress_namespace(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.settings["GLUU_HELM_RELEASE_NAME"] = "gluu"
    prompter.settings["NGINX_INGRESS_RELEASE_NAME"] = "ningress"
    prompter.settings["INSTALL_GLUU_GATEWAY"] = "N"

    prompter.prompt_helm
    assert prompter.settings["NGINX_INGRESS_NAMESPACE"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu-gateway"),  # default
    ("random", "random"),
])
def test_prompt_helm_gg_helm_release_name(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.settings["GLUU_HELM_RELEASE_NAME"] = "gluu"
    prompter.settings["NGINX_INGRESS_RELEASE_NAME"] = "ningress"
    prompter.settings["NGINX_INGRESS_NAMESPACE"] = "ingress-nginx"
    prompter.settings["INSTALL_GLUU_GATEWAY"] = "Y"
    prompter.settings["GLUU_GATEWAY_UI_HELM_RELEASE_NAME"] = "gluu-gateway-ui"

    prompter.prompt_helm
    assert prompter.settings["KONG_HELM_RELEASE_NAME"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu-gateway-ui"),  # default
    ("random", "random"),
])
def test_prompt_helm_gg_ui_helm_release_name(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.settings["GLUU_HELM_RELEASE_NAME"] = "gluu"
    prompter.settings["NGINX_INGRESS_RELEASE_NAME"] = "ningress"
    prompter.settings["NGINX_INGRESS_NAMESPACE"] = "ingress-nginx"
    prompter.settings["INSTALL_GLUU_GATEWAY"] = "Y"
    prompter.settings["KONG_HELM_RELEASE_NAME"] = "gluu-gateway"

    prompter.prompt_helm
    assert prompter.settings["GLUU_GATEWAY_UI_HELM_RELEASE_NAME"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", "0"),
    ("4.2.0_dev", "4.2.0_dev"),
])
def test_prompt_upgrade_version(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.prompt_upgrade
    assert prompter.settings["GLUU_UPGRADE_TARGET_VERSION"] == expected


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_prompt_volumes_identifier(monkeypatch, prompter, persistence):
    monkeypatch.setattr("click.prompt", lambda x: "vol-1234")

    prompter.settings["PERSISTENCE_BACKEND"] = persistence
    prompter.prompt_volumes_identifier()
    assert prompter.settings["LDAP_STATIC_VOLUME_ID"] == "vol-1234"


@pytest.mark.parametrize("persistence", ["ldap", "hybrid"])
def test_prompt_disk_uris(monkeypatch, prompter, persistence):
    monkeypatch.setattr("click.prompt", lambda x: "MC_aks")

    prompter.settings["PERSISTENCE_BACKEND"] = persistence
    prompter.prompt_disk_uris()
    assert prompter.settings["LDAP_STATIC_DISK_URI"] == "MC_aks"


@pytest.mark.parametrize("given, expected", [
    ("", "postgres"),  # default
    ("random", "random"),
])
def test_prompt_postgres_namespace(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.settings["POSTGRES_REPLICAS"] = 3
    prompter.settings["POSTGRES_URL"] = "postgres.postgres.svc.cluster.local"

    prompter.prompt_postgres()
    assert prompter.settings["POSTGRES_NAMESPACE"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", 3),  # default
    (2, 2),
])
def test_prompt_postgres_replicas(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.settings["POSTGRES_NAMESPACE"] = "postgres"
    prompter.settings["POSTGRES_URL"] = "postgres.postgres.svc.cluster.local"

    prompter.prompt_postgres()
    assert prompter.settings["POSTGRES_REPLICAS"] == expected


@pytest.mark.parametrize("given, expected", [
    ("", "postgres.postgres.svc.cluster.local"),  # default
    ("random", "random"),
])
def test_prompt_postgres_url(monkeypatch, prompter, given, expected):
    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompter.settings["POSTGRES_NAMESPACE"] = "postgres"
    prompter.settings["POSTGRES_REPLICAS"] = 3

    prompter.prompt_postgres()
    assert prompter.settings["POSTGRES_URL"] == expected
