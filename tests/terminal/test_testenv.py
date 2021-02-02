import pytest


@pytest.mark.parametrize("given, expected", [
    (False, False),
    (True, True),
])
def test_testenv_prompt_test_environment(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.testenv import PromptTestEnvironment

    monkeypatch.setattr("click.confirm", lambda x: given)

    PromptTestEnvironment(settings).prompt_test_environment()
    assert settings.get("global.cloud.testEnviroment") == expected

