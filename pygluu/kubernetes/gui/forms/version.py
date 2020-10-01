"""
pygluu.kubernetes.gui.forms.version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helpers to interact with user's input for gui gluu version form

License terms and conditions for Gluu Cloud Native Edition:
https://www.apache.org/licenses/LICENSE-2.0
"""
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import DataRequired


class VersionForm(FlaskForm):
    """
    Gluu version form

    Fields :
        gluu_version (string|required)
    """
    gluu_version = RadioField(
        "Please select the current version of Gluu or the version to be installed",
        choices=[],
        default="",
        validators=[DataRequired(message="Please select version")])
