import pytest


@pytest.mark.parametrize("given, expected", [
    ("", "gluu"),  # default
    ("random", "random"),
])
def test_helm_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("INSTALL_GLUU_GATEWAY", "N")
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "N")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("GLUU_HELM_RELEASE_NAME") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "ningress"),  # default
    ("random", "random"),
])
def test_helm_ingress_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("GLUU_HELM_RELEASE_NAME", "gluu")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("INSTALL_GLUU_GATEWAY", "N")
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "N")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("NGINX_INGRESS_RELEASE_NAME") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "ingress-nginx"),  # default
    ("random", "random"),
])
def test_helm_ingress_namespace(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("GLUU_HELM_RELEASE_NAME", "gluu")
    settings.set("INSTALL_GLUU_GATEWAY", "N")
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "N")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("NGINX_INGRESS_NAMESPACE") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu-gateway"),  # default
    ("random", "random"),
])
def test_helm_gg_helm_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "N")
    settings.set("INSTALL_GLUU_GATEWAY", "Y")
    settings.set("GLUU_GATEWAY_UI_HELM_RELEASE_NAME", "gluu-gateway-ui")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("KONG_HELM_RELEASE_NAME") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "gluu-gateway-ui"),  # default
    ("random", "random"),
])
def test_helm_gg_ui_helm_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("INSTALL_GLUU_GATEWAY", "Y")
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "N")
    settings.set("KONG_HELM_RELEASE_NAME", "gluu-gateway")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("GLUU_GATEWAY_UI_HELM_RELEASE_NAME") == expected


def test_helm_ldap_multi_cluster_name(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.confirm", lambda x, default: True)

    settings.set("GLUU_HELM_RELEASE_NAME", "gluu")
    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("INSTALL_GLUU_GATEWAY", "N")
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "Y")
    settings.set("GLUU_LDAP_SERF_PORT", "30946")
    settings.set("GLUU_LDAP_ADVERTISE_ADDRESS", "demoexample.gluu.org:30946")
    settings.set("GLUU_LDAP_ADVERTISE_ADMIN_PORT", "30444")
    settings.set("GLUU_LDAP_ADVERTISE_LDAPS_PORT", "30636")
    settings.set("GLUU_LDAP_ADVERTISE_REPLICATION_PORT", "30989")
    settings.set("GLUU_LDAP_SECONDARY_CLUSTER", "Y")
    settings.set("GLUU_LDAP_SERF_PEERS", "[firstldap.gluu.org:30946]")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("GLUU_LDAP_MULTI_CLUSTER") == "Y"
    assert settings.get("GLUU_LDAP_SERF_PORT") == "30946"
    assert settings.get("GLUU_LDAP_ADVERTISE_ADDRESS") == "demoexample.gluu.org:30946"
    assert settings.get("GLUU_LDAP_ADVERTISE_ADMIN_PORT") == "30444"
    assert settings.get("GLUU_LDAP_ADVERTISE_LDAPS_PORT") == "30636"
    assert settings.get("GLUU_LDAP_ADVERTISE_REPLICATION_PORT") == "30989"
    assert settings.get("GLUU_LDAP_SECONDARY_CLUSTER") == "Y"
    assert settings.get("GLUU_LDAP_SERF_PEERS") == "[firstldap.gluu.org:30946]"

