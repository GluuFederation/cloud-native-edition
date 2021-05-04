import pytest
import click
from pygluu.kubernetes.terminal.helpers import gather_ip
import ipaddress

@pytest.mark.parametrize("given, expected", [
    (True, True),
    (False, False),
])
def test_helpers_confirm_yesno(monkeypatch, given, expected):

    monkeypatch.setattr("click.confirm", lambda x: given)
    assert click.confirm("Random question") == expected

def test_node_ip(settings):
    settings.set("installer-settings.nodes.ips", node_ip_list)
    assert settings.get("installer-settings.nodes.ips") == []

def test_node_zone(ettings):
    settings.set("installer-settings.nodes.zones", node_zone_list)
    assert settings.get("installer-settings.nodes.zones") == []

def test_node_name(settings):
    settings.set("installer-settings.nodes.names", node_names_list)
    assert settings.get("installer-settings.nodes.names") == []

@pytest.mark.parametrize("arch", [
    ("kubernetes.io/aws-ebs"),
    ("kubernetes.io/gce-pd"),
    ("kubernetes.io/azure-disk"),
    ("dobs.csi.digitalocean.com"),
    ("openebs.io/local"),
])
def test_prompt_app_volume_type(monkeypatch, settings, arch, vol_type):
    from pygluu.kubernetes.terminal.helpers import gather_ip
    monkeypatch.setattr("click.prompt", lambda x, default: "22.22.22.22")
    settings.set("global.storageClass.provisioner", arch)
    assert "22.22.22.22"


def test_empty_ip(caplog, settings):
    with caplog.at_level(logging.INFO):
        assert settings.get("CN_HOST_EXT_IP", "")
        assert "Cannot determine IP address" in caplog.text

def test_invalid_ip(caplog, settings):
    with caplog.at_level(logging.INFO):
        assert settings.get("CN_HOST_EXT_IP", "775885.968.0") is False
        assert "Cannot determine IP address" in caplog.text