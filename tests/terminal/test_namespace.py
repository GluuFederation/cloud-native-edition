import pytest


@pytest.mark.parametrize("given, expected", [
    ("", "gluu"),
    ("my-ns", "my-ns"),
])
def test_gluu_namespace(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.namespace import PromptNamespace

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    prompt = PromptNamespace(settings)
    prompt.prompt_gluu_namespace()
    assert settings.get("GLUU_NAMESPACE") == expected
