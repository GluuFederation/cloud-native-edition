import pytest


@pytest.mark.parametrize("given, expected", [
    ("", "gluu"),  # default
    ("random", "random"),
])
def test_helm_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("installer-settings.nginxIngress.releaseName", "ningress")
    settings.set("installer-settings.nginxIngress.namespace", "ingress-nginx")
    settings.set("opendj.multiCluster.enabled", "N")
    settings.set("installer-settings.releaseName", "")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("installer-settings.releaseName") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "ningress"),  # default
    ("random", "random"),
])
def test_helm_ingress_release_name(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("installer-settings.releaseName", "gluu")
    settings.set("installer-settings.nginxIngress.namespace", "ingress-nginx")
    settings.set("opendj.multiCluster.enabled", "N")
    settings.set("installer-settings.nginxIngress.releaseName", "")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("installer-settings.nginxIngress.releaseName") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "ingress-nginx"),  # default
    ("random", "random"),
])
def test_helm_ingress_namespace(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("installer-settings.nginxIngress.releaseName", "ningress")
    settings.set("installer-settings.releaseName", "gluu")
    settings.set("opendj.multiCluster.enabled", "N")
    settings.set("installer-settings.nginxIngress.namespace", "")

    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("installer-settings.nginxIngress.namespace") == expected


def test_helm_ldap_multi_cluster_name(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.confirm", lambda x, default: True)

    settings.set("installer-settings.releaseName", "gluu")
    settings.set("installer-settings.nginxIngress.releaseName", "ningress")
    settings.set("installer-settings.nginxIngress.namespace", "ingress-nginx")
    settings.set("opendj.multiCluster.enabled", "Y")
    settings.set("opendj.ports.tcp-serf.nodePort", "30946")
    settings.set("opendj.multiCluster.serfAdvertiseAddr", "demoexample.gluu.org:30946")
    settings.set("opendj.ports.tcp-admin.nodePort", "30444")
    settings.set("opendj.ports.tcp-ldaps.nodePort", "30636")
    settings.set("opendj.ports.tcp-repl.nodePort", "30989")
    settings.set("installer-settings.ldap.subsequentCluster", "Y")
    settings.set("opendj.multiCluster.serfPeers", "[firstldap.gluu.org:30946]")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("opendj.multiCluster.enabled") == "Y"
    assert settings.get("opendj.ports.tcp-serf.nodePort") == "30946"
    assert settings.get("opendj.multiCluster.serfAdvertiseAddr") == "demoexample.gluu.org:30946"
    assert settings.get("opendj.ports.tcp-admin.nodePort") == "30444"
    assert settings.get("opendj.ports.tcp-ldaps.nodePort") == "30636"
    assert settings.get("opendj.ports.tcp-repl.nodePort") == "30989"
    assert settings.get("installer-settings.ldap.subsequentCluster") == "Y"
    assert settings.get("opendj.multiCluster.serfPeers") == "[firstldap.gluu.org:30946]"


def test_tcp_serf_nodeport(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: 30946)

    settings.set("opendj.multiCluster.enabled", True)
    settings.set("opendj.ports.tcp-serf.nodePort", "")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("opendj.ports.tcp-serf.nodePort") == 30946


def test_multicluster_serfadvertise_addr(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: "demoexample.gluu.org:30946")

    settings.set("opendj.multiCluster.enabled", True)
    settings.set("opendj.multiCluster.serfAdvertiseAddr", "")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("opendj.multiCluster.serfAdvertiseAddr") == int("demoexample.gluu.org:30946")


def test_tcp_admin_nodeport(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: 30444)

    settings.set("opendj.multiCluster.enabled", True)
    settings.set("opendj.ports.tcp-admin.nodePort", "")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("opendj.ports.tcp-admin.nodePort") == 30444


def test_tcp_ldaps_nodeport(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: 30636)

    settings.set("opendj.multiCluster.enabled", True)
    settings.set("opendj.ports.tcp-ldaps.nodePort", "")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("opendj.ports.tcp-ldaps.nodePort") == 30636


def test_tcp_rpl_nodeport(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: 30989)

    settings.set("opendj.multiCluster.enabled", True)
    settings.set("opendj.ports.tcp-repl.nodePort", "")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("opendj.ports.tcp-repl.nodePort") == 30989


def test_amulticluster_nodepeers(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.prompt", lambda x, default: "['firstldap.gluu.org:30946', 'secondldap.gluu.org:31946']")

    settings.set("opendj.multiCluster.enabled", True)
    settings.set("opendj.multiCluster.serfPeers", "")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("opendj.multiCluster.serfPeers") == "['firstldap.gluu.org:30946', 'secondldap.gluu.org:31946']"


def test_aws_arn(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.confirm", lambda x: fake_arn)

    fake_arn = "ALPHA-FEATURE-Are you setting up a multi kubernetes cluster"
    monkeypatch.setattr("click.prompt", lambda x: fake_arn)
    ettings.set("global.cnPersistenceType", "ldap")
    settings.set("opendj.multiCluster.enabled", False)
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("opendj.multiCluster.enabled") == fake_arn


def test_aws_arn(monkeypatch, settings):
    from pygluu.kubernetes.terminal.helm import PromptHelm

    monkeypatch.setattr("click.confirm", lambda x: True)

    fake_arn = "ALPHA-FEATURE-Is this a subsequent kubernetes cluster "
    
    monkeypatch.setattr("click.prompt", lambda x: fake_arn)
    settings.set("opendj.multiCluster.enabled", True)
    settings.set("installer-settings.ldap.subsequentCluster", "")
    prompt = PromptHelm(settings)
    prompt.prompt_helm()
    assert settings.get("installer-settings.ldap.subsequentCluster") == fake_arn