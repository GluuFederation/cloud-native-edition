"""
pygluu.kubernetes.gui.forms.version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's input for gui gluu version form

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import  DataRequired

from pygluu.kubernetes.helpers import get_supported_versions


class VersionForm(FlaskForm):
    """
    Gluu version form

    Fields :
        gluu_version (string|required)
    """
    versions, version_number = get_supported_versions()
    supported_versions = []

    for k, v in versions.items():
        supported_versions.append((k, k))

    gluu_version = RadioField(
        "Please select the current version of Gluu or the version to be installed",
        choices=supported_versions,
        default=version_number,
        validators=[DataRequired(message="Please select version")])
