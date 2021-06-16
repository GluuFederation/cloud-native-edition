import logging
from pathlib import Path
from pygluu.kubernetes.gluu import Gluu


def test_settings_is_not_exist(settings, tmpdir):
    p = Path(tmpdir) / './helm/gluu/values.yaml'
    settings.values_file = p

    assert settings.is_exist() is False


def test_values_is_exist(settings, tmpdir):
    p = Path(tmpdir) / 'values.yaml'
    p.write_text('{}')
    settings.values_file = p

    assert settings.is_exist() is True

  
def test_overide_values_is_exist(settings, tmpdir):
    p = Path(tmpdir) / 'gluu-upgradevalues.yaml'
    p.write_text('{}')
    settings.values_file = p

    assert settings.is_exist() is True
