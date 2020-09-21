import pytest


@pytest.mark.parametrize("given, expected", [
    ("", "*/30 * * * *"),  # default
    ("*/10 * * * *", "*/10 * * * *"),
])
def test_backup_ldap(monkeypatch, settings, given, expected):
    from pygluu.kubernetes.terminal.backup import PromptBackup

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("PERSISTENCE_BACKEND", "ldap")
    PromptBackup(settings).prompt_backup()
    assert settings.get("LDAP_BACKUP_SCHEDULE") == expected


@pytest.mark.parametrize("given, expected, type_", [
    ("", "*/30 * * * *", "couchbase"),  # default
    ("*/10 * * * *", "*/10 * * * *", "couchbase"),
    ("", "*/30 * * * *", "hybrid"),  # default
    ("*/10 * * * *", "*/10 * * * *", "hybrid"),
])
def test_backup_not_ldap_incr(monkeypatch, settings, given, expected, type_):
    from pygluu.kubernetes.terminal.backup import PromptBackup

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("PERSISTENCE_BACKEND", type_)
    settings.set("COUCHBASE_FULL_BACKUP_SCHEDULE", "0 2 * * 6")
    settings.set("COUCHBASE_BACKUP_RETENTION_TIME", "168h")
    settings.set("COUCHBASE_BACKUP_STORAGE_SIZE", "20Gi")

    PromptBackup(settings).prompt_backup()
    assert settings.get("COUCHBASE_INCR_BACKUP_SCHEDULE") == expected


@pytest.mark.parametrize("given, expected, type_", [
    ("", "0 2 * * 6", "couchbase"),  # default
    ("0 1 * * 6", "0 1 * * 6", "couchbase"),
    ("", "0 2 * * 6", "hybrid"),  # default
    ("0 1 * * 6", "0 1 * * 6", "hybrid"),
])
def test_backup_not_ldap_full(monkeypatch, settings, given, expected, type_):
    from pygluu.kubernetes.terminal.backup import PromptBackup

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("PERSISTENCE_BACKEND", type_)
    settings.set("COUCHBASE_INC_BACKUP_SCHEDULE", "*/30 * * * *")
    settings.set("COUCHBASE_BACKUP_RETENTION_TIME", "168h")
    settings.set("COUCHBASE_BACKUP_STORAGE_SIZE", "20Gi")

    PromptBackup(settings).prompt_backup()
    assert settings.get("COUCHBASE_FULL_BACKUP_SCHEDULE") == expected


@pytest.mark.parametrize("given, expected, type_", [
    ("", "168h", "couchbase"),  # default
    ("160h", "160h", "couchbase"),
    ("", "168h", "hybrid"),  # default
    ("160h", "160h", "hybrid"),
])
def test_backup_not_ldap_retention(monkeypatch, settings, given, expected, type_):
    from pygluu.kubernetes.terminal.backup import PromptBackup

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("PERSISTENCE_BACKEND", type_)
    settings.set("COUCHBASE_INC_BACKUP_SCHEDULE", "*/30 * * * *")
    settings.set("COUCHBASE_FULL_BACKUP_SCHEDULE", "0 2 * * 6")
    settings.set("COUCHBASE_BACKUP_STORAGE_SIZE", "20Gi")

    PromptBackup(settings).prompt_backup()
    assert settings.get("COUCHBASE_BACKUP_RETENTION_TIME") == expected


@pytest.mark.parametrize("given, expected, type_", [
    ("", "20Gi", "couchbase"),  # default
    ("10Gi", "10Gi", "couchbase"),
    ("", "20Gi", "hybrid"),  # default
    ("10Gi", "10Gi", "hybrid"),
])
def test_backup_not_ldap_storage(monkeypatch, settings, given, expected, type_):
    from pygluu.kubernetes.terminal.backup import PromptBackup

    monkeypatch.setattr("click.prompt", lambda x, default: given or expected)

    settings.set("PERSISTENCE_BACKEND", type_)
    settings.set("COUCHBASE_INC_BACKUP_SCHEDULE", "*/30 * * * *")
    settings.set("COUCHBASE_FULL_BACKUP_SCHEDULE", "0 2 * * 6")
    settings.set("COUCHBASE_BACKUP_RETENTION_TIME", "168h")

    PromptBackup(settings).prompt_backup()
    assert settings.get("COUCHBASE_BACKUP_STORAGE_SIZE") == expected
