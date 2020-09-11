import pytest


def test_license_no_prompt(settings):
    from pygluu.kubernetes.terminal.license import PromptLicense

    prompt = PromptLicense(settings, accept_license=True)
    prompt.prompt_license()
    assert settings.get("ACCEPT_GLUU_LICENSE") == "Y"


def test_license_accepted(monkeypatch, settings):
    from pygluu.kubernetes.terminal.license import PromptLicense

    monkeypatch.setattr("click.confirm", lambda x: True)

    PromptLicense(settings)
    assert settings.get("ACCEPT_GLUU_LICENSE") == "Y"


def test_license_rejected(monkeypatch, settings):
    from pygluu.kubernetes.terminal.license import PromptLicense

    monkeypatch.setattr("click.confirm", lambda x: False)

    with pytest.raises(SystemExit):
        PromptLicense(settings)
