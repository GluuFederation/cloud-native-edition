import pytest


@pytest.mark.parametrize("given, expected", [
    (False, "N"),
    (True, "Y"),
])
def test_testenv_prompt_test_environment(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.testenv import PromptTestEnvironment

    monkeypatch.setattr("click.confirm", lambda x: given)

    PromptTestEnvironment(settings).prompt_test_environment()
    assert settings.get("TEST_ENVIRONMENT") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "~/.ssh/id_rsa"),
    ("~/.ssh/id_rsa_gluu", "~/.ssh/id_rsa_gluu"),
])
def test_testenv_prompt_ssh_key(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.testenv import PromptTestEnvironment

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    PromptTestEnvironment(settings).prompt_ssh_key()
    assert settings.get("NODE_SSH_KEY") == expected
