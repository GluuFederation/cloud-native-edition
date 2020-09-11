import pytest


@pytest.mark.parametrize("given, expected", [
    ("", "4.2"),
    ("4.2", "4.2"),
])
def test_upgrade_version(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.upgrade import PromptUpgrade

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompt = PromptUpgrade(settings)
    prompt.prompt_upgrade()
    assert settings.get("GLUU_UPGRADE_TARGET_VERSION") == expected
