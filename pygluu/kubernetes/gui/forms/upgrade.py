"""
pygluu.kubernetes.gui.forms.upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's input for gui gluu upgrade form

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import DataRequired

from pygluu.kubernetes.helpers import get_supported_versions


class UpgradeForm(FlaskForm):
    """
    Gluu upgrade form

    Fields :
        gluu_version (string|required)
    """
    versions, version_number = get_supported_versions()
    supported_versions = []

    for k, _ in versions.items():
        supported_versions.append((k, k))

    upgrade_target_version = RadioField(
        "Please enter the version to upgrade Gluu to",
        choices=supported_versions,
        default=version_number,
        validators=[DataRequired(message="Please select version")])
