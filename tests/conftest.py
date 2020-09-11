import pytest


@pytest.fixture()
def settings():
    from pygluu.kubernetes.settings import SettingsHandler, unlink_settings_json

    handler = SettingsHandler()
    yield handler
    unlink_settings_json()
