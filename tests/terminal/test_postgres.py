import pytest


@pytest.mark.parametrize("given, expected", [
    ("", "postgres"),  # default
    ("random", "random"),
])
def test_postgres_namespace(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.postgres import PromptPostgres

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)
    settings.set("INSTALL_POSTGRES", "Y")
    settings.set("POSTGRES_URL", "postgres.postgres.svc.cluster.local")

    prompt = PromptPostgres(settings)
    prompt.prompt_postgres()
    assert settings.get("POSTGRES_NAMESPACE") == expected

@pytest.mark.parametrize("given, expected", [
    ("", "postgres.postgres.svc.cluster.local"),  # default
    ("random", "random"),
])
def test_postgres_url(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.postgres import PromptPostgres

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)
    settings.set("INSTALL_POSTGRES", "N")

    prompt = PromptPostgres(settings)
    prompt.prompt_postgres()
    assert settings.get("POSTGRES_URL") == expected
