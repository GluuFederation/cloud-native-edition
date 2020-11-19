import logging
from pathlib import Path

def test_store_data_exception(caplog, settings):
    # set collection to something that cannot be dumped as JSON
    settings.db = str

    with caplog.at_level(logging.INFO):
        assert settings.store_data() is False
        assert "Uncaught error" in caplog.text


def test_set_exception(caplog, settings):
    # set collection to something that cannot be dumped as JSON
    settings.db = str

    with caplog.at_level(logging.INFO):
        assert settings.set("CN_VERSION", "5.0") is False
        assert "Uncaught error" in caplog.text


def test_get_exception(caplog, settings):
    with caplog.at_level(logging.INFO):
        assert settings.get("RANDOM_KEY") is False
        assert "No Value" in caplog.text


def test_update_exception(caplog, settings):
    # set collection to something that is not a collection
    collection = 1

    with caplog.at_level(logging.INFO):
        assert settings.update(collection) is False
        assert "Uncaught error" in caplog.text


def test_reset_data_exception(caplog, monkeypatch, settings):
    def fake_store_data():
        1 / 0

    monkeypatch.setattr(
        "pygluu.kubernetes.settings.SettingsHandler.store_data",
        fake_store_data,
    )

    with caplog.at_level(logging.INFO):
        assert settings.reset_data() is False
        assert "Uncaught error" in caplog.text


def test_settings_is_not_exist(settings, tmpdir):
    p = Path(tmpdir) / 'test_settings.json'
    settings.setting_file = p

    assert settings.is_exist() is False


def test_settings_is_exist(settings, tmpdir):
    p = Path(tmpdir) / 'test_settings.json'
    p.write_text('{}')
    settings.setting_file = p

    assert settings.is_exist() is True
