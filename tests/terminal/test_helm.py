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
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "N")
    settings.set("NGINX_LEGACY", "N")

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

    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("GLUU_HELM_RELEASE_NAME", "gluu")
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "N")
    settings.set("NGINX_LEGACY", "N")

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
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "N")
    settings.set("NGINX_LEGACY", "N")
    
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("NGINX_INGRESS_NAMESPACE") == expected

def test_helm_ldap_multi_cluster_name(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.confirm", lambda x, default: True)

    settings.set("GLUU_HELM_RELEASE_NAME", "gluu")
    settings.set("NGINX_INGRESS_RELEASE_NAME", "ningress")
    settings.set("NGINX_INGRESS_NAMESPACE", "ingress-nginx")
    settings.set("GLUU_LDAP_MULTI_CLUSTER", "Y")
    settings.set("GLUU_LDAP_ADVERTISE_ADDRESS_SUFFIX", "demoexample.gluu.org")
    settings.set("GLUU_LDAP_MULTI_CLUSTER_REPLICAS", "1")
    settings.set("GLUU_LDAP_SECONDARY_CLUSTER", "Y")
    settings.set("GLUU_LDAP_SERF_PEERS", ["firstldap.gluu.org:30946", "secondldap.gluu.org:31946"])
    settings.set("GLUU_LDAP_MULTI_CLUSTER_CLUSTER_ID", "test")
    settings.set("GLUU_LDAP_MULTI_CLUSTER_NAMESPACE_INT_ID", "0")
    settings.set("GLUU_LDAP_MULTI_CLUSTERS_IDS", ["east","west"])
    settings.set("NGINX_LEGACY", "N")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("GLUU_LDAP_MULTI_CLUSTER") == "Y"
    assert settings.get("GLUU_LDAP_ADVERTISE_ADDRESS_SUFFIX") == "demoexample.gluu.org"
    assert settings.get("GLUU_LDAP_SECONDARY_CLUSTER") == "Y"
    assert settings.get("GLUU_LDAP_SERF_PEERS") == ["firstldap.gluu.org:30946", "secondldap.gluu.org:31946"]
    assert settings.get("GLUU_LDAP_MULTI_CLUSTER_CLUSTER_ID") == "test"
    assert settings.get("GLUU_LDAP_MULTI_CLUSTERS_IDS") == ["east","west"]
