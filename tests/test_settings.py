import logging


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
        assert settings.set("GLUU_VERSION", "4.5") is False
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
