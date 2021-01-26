import pytest


@pytest.mark.parametrize("given, expected", [
    ("", "postgres"),  # default
    ("random", "random"),
])
def test_postgres_namespace(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.postgres import PromptPostgres

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("CN_POSTGRES_REPLICAS", 3)
    settings.set("CN_POSTGRES_URL", "postgres.postgres.svc.cluster.local")

    prompt = PromptPostgres(settings)
    prompt.prompt_postgres()
    assert settings.get("CN_POSTGRES_NAMESPACE") == expected


@pytest.mark.parametrize("given, expected", [
    ("", 3),  # default
    (2, 2),
])
def test_postgres_replicas(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.postgres import PromptPostgres

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("CN_POSTGRES_NAMESPACE", "postgres")
    settings.set("CN_POSTGRES_URL", "postgres.postgres.svc.cluster.local")

    prompt = PromptPostgres(settings)
    prompt.prompt_postgres()
    assert settings.get("CN_POSTGRES_REPLICAS") == expected


@pytest.mark.parametrize("given, expected", [
    ("", "postgres.postgres.svc.cluster.local"),  # default
    ("random", "random"),
])
def test_postgres_url(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.postgres import PromptPostgres

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("CN_POSTGRES_NAMESPACE", "postgres")
    settings.set("CN_POSTGRES_REPLICAS", 3)

    prompt = PromptPostgres(settings)
    prompt.prompt_postgres()
    assert settings.get("CN_POSTGRES_URL") == expected
